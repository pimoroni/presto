import io
import struct
import vfs
import micropython


PSRAM_BASE = 0x11000000
PSRAM_SIZE = 8 * 1024 * 1024


@micropython.viper
def viper_memcpy(dest: ptr8, src: ptr8, num: int) -> int:
    for i in range(num):
        dest[i] = src[i]
    return num


@micropython.viper
def viper_mem8_findnext(addr: ptr8, num: int, delimiter: int) -> int:
    for i in range(num):
        if addr[i] == delimiter:
            return i + 1
    return num


@micropython.viper
def viper_memset(dest: ptr8, value: int, num: int):
    for i in range(num):
        dest[i] = value


@micropython.viper
def viper_crc16(data: ptr8, num: int) -> int:
    crc: int = 0x0000
    i: int = 0

    while i < num:
        crc ^= data[i] << 8
        j: int = 8
        while j > 0:
            if crc & (1 << 15):
                crc <<= 1
                crc ^= 0x8001
                crc &= 0xffff
            else:
                crc <<= 1
                crc &= 0xffff
            j -= 1
        i += 1
    return crc


class PSRAM(io.StringIO):
    HEADER = b"PSRAM_____"
    HEADER_SIZE = 16

    def __init__(self, size, offset=None, create=False, blocksize=256, skip_crc=False, debug=False):
        self.debug = debug
        self.skip_crc = skip_crc

        if size >= 0xffffffff:
            raise ValueError(f"Max length {0xffffffff:0,d} bytes")

        self.blocks, self.remainder = divmod(size, blocksize)

        if self.remainder:
            raise ValueError("Size should be a multiple of {blocksize:0,d}")

        self.blocksize = blocksize
        self.length = size

        if offset is None:
            offset = PSRAM_SIZE - self.length

        self.offset = PSRAM_BASE | offset
        self.ptr = 0

        self.check_header(create)

    def check_header(self, create):
        # Read and check the header
        header, length, hcrc, valid = self._read_header()
        if not valid:
            if not create:
                raise ValueError("Invalid data found, refusing to overwrite!")
            self.clear()
            self._write_header()

    def _read_header(self):
        header = bytearray(self.HEADER_SIZE)
        viper_memcpy(header, self.offset - self.HEADER_SIZE, self.HEADER_SIZE)
        header, length, crc = struct.unpack("<10sIH", header)
        return header, length, crc, header == self.HEADER and crc == self.calculate_crc() and length == self.length

    def _write_header(self):
        header = struct.pack("<10sIH", self.HEADER, self.length, self.calculate_crc())
        viper_memcpy(self.offset - self.HEADER_SIZE, header, self.HEADER_SIZE)

    def calculate_crc(self):
        if self.skip_crc:
            return 0
        return viper_crc16(self.offset, self.length)

    def clear(self):
        self.ptr = 0
        viper_memset(self.offset, 0, self.length)

    def seek(self, to):
        self.ptr = to

    def tell(self):
        return self.ptr

    def readinto(self, buffer):
        limit = min(self.length - self.ptr, len(buffer))
        self.ptr = viper_memcpy(buffer, self.offset + self.ptr, limit)
        return limit

    def readline(self):
        limit = viper_mem8_findnext(self.offset + self.ptr, self.length - self.ptr, ord('\n'))
        return self.read(limit)

    def read(self, length=None):
        limit = min(self.length - self.ptr, length or self.length)
        buffer = bytearray(limit)
        self.ptr += viper_memcpy(buffer, self.offset + self.ptr, limit)
        return buffer

    def write(self, buffer):
        limit = min(self.length - self.ptr, len(buffer))
        self.ptr += viper_memcpy(self.offset + self.ptr, buffer, limit)
        self._write_header()

    def getvalue(self):
        buffer = bytearray(self.length)
        viper_memcpy(buffer, self.offset, self.length)
        return buffer

    def readblocks(self, block_num, buf, offset=0):
        if self.debug:
            print(f"PSRAM: readblocks: {block_num} {len(buf)}, {offset}")
        _ptr = self.ptr
        self.ptr = block_num * self.blocksize + offset
        self.readinto(buf)
        self.ptr = _ptr

    def writeblocks(self, block_num, buf, offset=0):
        if self.debug:
            print(f"PSRAM: writeblocks: {block_num} {len(buf)}, {offset}")
        _ptr = self.ptr
        self.ptr = block_num * self.blocksize + offset
        result = self.write(buf)
        self.ptr = _ptr
        return result

    def eraseblock(self, block_num):
        if self.debug:
            print(f"PSRAM: eraseblock: {block_num}")
        viper_memset(block_num * self.blocksize + self.offset, 0, self.length)

    def ioctl(self, op, arg):
        if self.debug:
            print(f"PSRAML: ioctl: {op} {arg}")
        if op == 1:  # Initialize
            return None
        if op == 2:  # Shutdown
            return None
        if op == 3:  # Sync
            return 0
        if op == 4:  # Block Count
            return self.blocks
        if op == 5:  # Block Size
            return self.blocksize
        if op == 6:  # Erase
            # We don't really *need* to erase blocks
            # but should we?
            # self.eraseblock(arg)
            return 0

    def __str__(self):
        header, length, hcrc, valid = self._read_header()
        return f"PSRAM: length: {length}, crc: {hcrc:04x}, valid: {valid}"


def mktmpfs(size=1024 * 64, raw=False, debug=False):
    psram = PSRAM(size, create=True, skip_crc=size > 1024 * 256, debug=debug)

    if not raw:
        try:
            fs = vfs.VfsLfs2(psram, progsize=256)
        except OSError:
            vfs.VfsLfs2.mkfs(psram, progsize=256)
            fs = vfs.VfsLfs2(psram, progsize=256)

        vfs.mount(fs, "/ramfs")

    return psram
