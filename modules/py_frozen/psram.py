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
def viper_memset(dest: ptr8, value: int, num: int):
    for i in range(num):
        dest[i] = value


@micropython.viper
def viper_psram_flush():
    # XIP_MAINTENANCE_BASE
    dest: ptr8 = ptr8(0x18000000)
    i: int = 1
    end: int = 16 * 1024
    while i < end:
        dest[i] = 0
        i += 8


class PSRAMBlockDevice:
    def __init__(self, size, offset=None, blocksize=256, debug=False):
        self.debug = debug
        self.blocks, remainder = divmod(size, blocksize)

        if remainder:
            raise ValueError("Size should be a multiple of {blocksize:0,d}")

        self.blocksize = blocksize

        if offset is None:
            offset = PSRAM_SIZE - size

        self.offset = PSRAM_BASE | offset

    def readblocks(self, block_num, buf, offset=0):
        if self.debug:
            print(f"PSRAM: readblocks: {block_num} {len(buf)}, {offset}")
        viper_memcpy(buf, self.offset + (block_num * self.blocksize) + offset, len(buf))

    def writeblocks(self, block_num, buf, offset=0):
        if self.debug:
            print(f"PSRAM: writeblocks: {block_num} {len(buf)}, {offset}")
        viper_memcpy(self.offset + (block_num * self.blocksize) + offset, buf, len(buf))

    def ioctl(self, op, arg):
        if self.debug:
            print(f"PSRAML: ioctl: {op} {arg}")
        if op == 1:  # Initialize
            return None
        if op == 2:  # Shutdown
            return None
        if op == 3:  # Sync
            viper_psram_flush()
            return 0
        if op == 4:  # Block Count
            return self.blocks
        if op == 5:  # Block Size
            return self.blocksize
        if op == 6:  # Erase
            # We don't really *need* to erase blocks but should we?
            return 0


def mkramfs(size=1024 * 64, mount_point="/ramfs", debug=False):
    psram = PSRAMBlockDevice(size, debug=debug)

    try:
        fs = vfs.VfsLfs2(psram, progsize=256)
    except OSError:
        vfs.VfsLfs2.mkfs(psram, progsize=256)
        fs = vfs.VfsLfs2(psram, progsize=256)

    vfs.mount(fs, mount_point)
