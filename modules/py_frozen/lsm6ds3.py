# Registers
WHO_AM_I = const(0x0F)
CTRL2_G = const(0x11)
CTRL1_XL = const(0x10)
CTRL10_C = const(0x19)
CTRL3_C = const(0x12)

# This is the start of the data registers for the Gyro and Accelerometer
# There are 12 Bytes in total starting at 0x23 and ending at 0x2D
OUTX_L_G = const(0x22)

STEP_COUNTER_L = const(0x4B)
STEP_COUNTER_H = const(0x4C)
TAP_SRC = const(0x1C)
TAP_CFG = const(0x58)
FUNC_SRC1 = const(0x53)
FUNC_SRC2 = const(0x54)
TAP_THS_6D = const(0x59)
FREE_FALL = const(0x5D)
WAKE_UP_THS = const(0x5B)
WAKE_UP_SRC = const(0x1B)
INT_DUR2 = const(0x5A)

# CONFIG DATA
NORMAL_MODE_104HZ = const(0x40)
NORMAL_MODE_208HZ = const(0x50)
PERFORMANCE_MODE_416HZ = const(0x60)
LOW_POWER_26HZ = const(0x02)
SET_FUNC_EN = const(0xBD)
RESET_STEPS = const(0x02)
TAP_EN_XYZ = const(0x8E)
TAP_THRESHOLD = const(0x02)
DOUBLE_TAP_EN = const(0x80)
DOUBLE_TAP_DUR = const(0x20)


def twos_comp(val, bits=16):
    mask = 1 << (bits - 1)

    if val & mask:
        val &= ~mask
        val -= mask

    return val


class LSM6DS3:
    def __init__(self, i2c, address=0x6A, mode=NORMAL_MODE_104HZ):
        self.bus = i2c
        self.address = address
        self.mode = mode

        # Set gyro mode/enable
        self.bus.writeto_mem(self.address, CTRL2_G, bytearray([self.mode]))

        # Set accel mode/enable
        self.bus.writeto_mem(self.address, CTRL1_XL, bytearray([self.mode]))

        # Send the reset bit to clear the pedometer step count
        self.bus.writeto_mem(self.address, CTRL10_C, bytearray([RESET_STEPS]))

        # Enable sensor functions (Tap, Tilt, Significant Motion)
        self.bus.writeto_mem(self.address, CTRL10_C, bytearray([SET_FUNC_EN]))

        # Enable X Y Z Tap Detection
        self.bus.writeto_mem(self.address, TAP_CFG, bytearray([TAP_EN_XYZ]))

        # Enable Double tap
        self.bus.writeto_mem(self.address, WAKE_UP_THS, bytearray([DOUBLE_TAP_EN]))

        # Set tap threshold
        self.bus.writeto_mem(self.address, TAP_THS_6D, bytearray([TAP_THRESHOLD]))

        # Set double tap max time gap
        self.bus.writeto_mem(self.address, INT_DUR2, bytearray([DOUBLE_TAP_DUR]))

    def _read_reg(self, reg, size):
        return self.bus.readfrom_mem(self.address, reg, size)

    def get_readings(self):

        # Read 12 bytes starting from 0x22. This covers the XYZ data for gyro and accel
        data = self._read_reg(OUTX_L_G, 12)

        gx = (data[1] << 8) | data[0]
        gx = twos_comp(gx)

        gy = (data[3] << 8) | data[2]
        gy = twos_comp(gy)

        gz = (data[5] << 8) | data[4]
        gz = twos_comp(gz)

        ax = (data[7] << 8) | data[6]
        ax = twos_comp(ax)

        ay = (data[9] << 8) | data[8]
        ay = twos_comp(ay)

        az = (data[11] << 8) | data[10]
        az = twos_comp(az)

        return ax, ay, az, gx, gy, gz

    def get_step_count(self):

        data = self._read_reg(STEP_COUNTER_L, 2)
        steps = (data[1] << 8) | data[0]
        steps = twos_comp(steps)

        return steps

    def reset_step_count(self):

        # Send the reset bit
        self.bus.writeto_mem(self.address, CTRL10_C, bytearray([RESET_STEPS]))
        # Enable functions again
        self.bus.writeto_mem(self.address, CTRL10_C, bytearray([SET_FUNC_EN]))

    def tilt_detected(self):

        tilt = self._read_reg(FUNC_SRC1, 1)
        tilt = (tilt[0] >> 5) & 0b1

        return tilt

    def sig_motion_detected(self):

        sig = self._read_reg(FUNC_SRC1, 1)
        sig = (sig[0] >> 6) & 0b1

        return sig

    def single_tap_detected(self):

        s = self._read_reg(TAP_SRC, 1)
        s = (s[0] >> 5) & 0b1

        return s

    def double_tap_detected(self):

        d = self._read_reg(TAP_SRC, 1)
        d = (d[0] >> 4) & 0b1

        return d

    def freefall_detected(self):

        fall = self._read_reg(WAKE_UP_SRC, 1)
        fall = fall[0] >> 5

        return fall
