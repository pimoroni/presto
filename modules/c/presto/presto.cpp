#include "st7701.hpp"
#include "micropython/modules/util.hpp"
#include "ws2812.hpp"
#include <cstdio>
#include <cfloat>


#include "hardware/structs/ioqspi.h"
#include "hardware/structs/qmi.h"
#include "hardware/structs/xip_ctrl.h"
#include "hardware/irq.h"


using namespace pimoroni;
using namespace plasma;

extern "C" {
#include "presto.h"
#include "py/builtin.h"
#include <stdarg.h>

// MicroPython's GC heap will automatically resize, so we should just
// statically allocate these in C++ to avoid fragmentation.
// Scanout is RGB565 and read continuously by DMA, so it has to be SRAM. The
// RGBA8888 surface picovector draws into sits right behind it. Both fit for the
// default half-res mode; full res needs 1.35M and comes from the GC heap.
#define HALF_WIDTH (WIDTH / 2)
#define HALF_HEIGHT (HEIGHT / 2)
#define HALF_PIXELS (HALF_WIDTH * HALF_HEIGHT)
// Full res scans out of PSRAM through this many SRAM lines, kept ahead of the
// beam by the line ISR.
#define FULL_RES_CACHE_LINES 4
__attribute__((section(".uninitialized_data"), aligned(4)))
static uint8_t presto_sram_pool[HALF_PIXELS * (sizeof(uint16_t) + sizeof(uint32_t))];
static uint16_t *presto_buffer = (uint16_t *)presto_sram_pool;

typedef struct _Presto_sample_point_t {
    int x, y;
} _Presto_sample_point_t;

void __printf_debug_flush() {
    for(auto i = 0u; i < 10; i++) {
        sleep_ms(2);
        mp_event_handle_nowait();
    }
}

int mp_vprintf(const mp_print_t *print, const char *fmt, va_list args);

#if DEBUG
void presto_debug(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int ret = mp_vprintf(&mp_plat_print, fmt, ap);
    va_end(ap);
    __printf_debug_flush();
    (void)ret;
}
#else
#define presto_debug(fmt, ...)
#endif

typedef struct _Presto_led_values_t {
    uint32_t r, g, b;
} _Presto_led_values_t;

/***** Variables Struct *****/
typedef struct _Presto_obj_t {
    mp_obj_base_t base;
    ST7701* presto;
    uint16_t width;
    uint16_t height;
    bool using_palette;

    // RGBA8888 drawing surface, handed to picovector's image() via the buffer
    // protocol. At half res it lives in the tail of presto_sram_pool; at full
    // res both buffers need 1.35M and come from the GC heap, which is in PSRAM.
    // The GC only scans its own heap and the stack, so full-res allocations are
    // kept reachable from here.
    uint32_t* back_buffer;
    uint16_t* front_buffer;
    uint16_t* scanout_cache;
    uint16_t* psram_frame;

    // Automatic ambient backlight control
    volatile bool auto_ambient_leds;
    WS2812* ws2812;
    _Presto_led_values_t led_values[7];
} _Presto_obj_t;

// There can only be one presto display, so have a global pointer
// so that core1 can access it.  Note it also needs to be in the
// Micropython object to prevent GC freeing it.
static _Presto_obj_t *presto_obj;

static volatile bool exit_core1;

// ST7701 must be allocated into SRAM (not PSRAM), so reserve a buffer
// for it here - Presto_make_new will placement new into this buffer.
__attribute__((section(".uninitialized_data"))) static uint32_t st7701_buffer[sizeof(ST7701) / sizeof(uint32_t)];

#define NUM_LEDS 7

// These must be tweaked together
#define SAMPLE_RANGE 64
#define LOG2_OF_SAMPLE_RANGE_SQUARED 12

#define SAMPLE_SHIFT (LOG2_OF_SAMPLE_RANGE_SQUARED + 2)
static void __no_inline_not_in_flash_func(update_backlight_leds)() {
    const _Presto_sample_point_t led_sample_locations[NUM_LEDS] = {
        { presto_obj->width - SAMPLE_RANGE, presto_obj->height - SAMPLE_RANGE },
        { presto_obj->width - SAMPLE_RANGE, (presto_obj->height - SAMPLE_RANGE)/2 },
        { presto_obj->width - SAMPLE_RANGE, 0 },
        { (presto_obj->width - SAMPLE_RANGE)/2, 0 },
        { 0, 0 },
        { 0, (presto_obj->height - SAMPLE_RANGE)/2 },
        { 0, presto_obj->height - SAMPLE_RANGE }
    };

    while (!exit_core1) {
        if (presto_obj->auto_ambient_leds) {
            for (int i = 0; i < NUM_LEDS; ++i) {
                uint32_t r = presto_obj->led_values[i].r;
                uint32_t g = presto_obj->led_values[i].g;
                uint32_t b = presto_obj->led_values[i].b;

                if (presto_obj->using_palette) {
                    for (int y = 0; y < SAMPLE_RANGE; ++y) {
                        uint8_t* ptr = (uint8_t*)presto_buffer;
                        ptr += (led_sample_locations[i].y + y) * presto_obj->width + led_sample_locations[i].x;
                        for (int x = 0; x < SAMPLE_RANGE; ++x) {
                            uint16_t sample = presto_obj->presto->get_encoded_palette_entry(*ptr++) >> 16;
                            r += (sample >> 8) & 0xF8;
                            g += (sample >> 3) & 0xFC;
                            b += (sample << 3) & 0xF8;
                        }
                    }
                }
                else {
                    uint16_t* frame = presto_obj->psram_frame ? presto_obj->psram_frame : presto_buffer;
                    for (int y = 0; y < SAMPLE_RANGE; ++y) {
                        uint16_t* ptr = &frame[(led_sample_locations[i].y + y) * presto_obj->width + led_sample_locations[i].x];
                        for (int x = 0; x < SAMPLE_RANGE; ++x) {
                            uint16_t sample = __builtin_bswap16(*ptr++);
                            r += (sample >> 8) & 0xF8;
                            g += (sample >> 3) & 0xFC;
                            b += (sample << 3) & 0xF8;
                        }
                    }
                }
                presto_obj->led_values[i].r = r;
                presto_obj->led_values[i].g = g;
                presto_obj->led_values[i].b = b;
            }
        }

        presto_obj->presto->wait_for_vsync();

        if (exit_core1) break;

        // Note this section calls into code that executes from flash
        // It's important this is done during vsync to avoid artifacts,
        // hence the wait for vsync above.
        if (presto_obj->auto_ambient_leds) {
            for (int i = 0; i < NUM_LEDS; ++i) {
                const uint32_t r = presto_obj->led_values[i].r;
                const uint32_t g = presto_obj->led_values[i].g;
                const uint32_t b = presto_obj->led_values[i].b;
                presto_obj->ws2812->set_rgb(i, r >> SAMPLE_SHIFT, g >> SAMPLE_SHIFT, b >> SAMPLE_SHIFT);
                presto_obj->led_values[i].r = (r * 3) >> 2;
                presto_obj->led_values[i].g = (g * 3) >> 2;
                presto_obj->led_values[i].b = (b * 3) >> 2;
            }
        } else {
            for (int i = 0; i < NUM_LEDS; ++i) {
                const uint32_t r = presto_obj->led_values[i].r;
                const uint32_t g = presto_obj->led_values[i].g;
                const uint32_t b = presto_obj->led_values[i].b;
                presto_obj->ws2812->set_rgb(i, r, g, b);
            }
        }
        presto_obj->ws2812->update();
    }

    multicore_fifo_push_blocking(1);
}

#define LOCKOUT_MAGIC_START 0x73a8831eu
#define LOCKOUT_MAGIC_END (~LOCKOUT_MAGIC_START)

// Alternative version of the lockout handler which does not disable interrupts
// We know that all interrupts running on core1 will not access flash or PSRAM, so this is safe.
static void __isr __not_in_flash_func(presto_core1_lockout_handler)(void) {
    multicore_fifo_clear_irq();
    while (multicore_fifo_rvalid()) {
        if (sio_hw->fifo_rd == LOCKOUT_MAGIC_START) {
            sio_hw->fifo_wr = LOCKOUT_MAGIC_START;
            __sev();
            while (multicore_fifo_pop_blocking_inline() != LOCKOUT_MAGIC_END) {
                tight_loop_contents(); // not tight but endless potentially
            }
            sio_hw->fifo_wr = LOCKOUT_MAGIC_END;
            __sev();
        }
    }
}

static bool ever_inited = false;

void presto_core1_entry() {
    // The multicore lockout uses the FIFO, so we use just use sev and volatile flags to signal this core
    multicore_lockout_victim_init();

    // Replace the lockout handler
    irq_handler_t sdk_handler = irq_get_exclusive_handler(SIO_IRQ_FIFO);
    irq_remove_handler(SIO_IRQ_FIFO, sdk_handler);
    irq_set_exclusive_handler(SIO_IRQ_FIFO, presto_core1_lockout_handler);

    ever_inited = true;

    presto_obj->presto->init();

    multicore_fifo_push_blocking(0); // Todo handle issues here?*/

    // Presto is now running the display using interrupts on this core.
    // We can also drive the backlight if requested.
    while (!exit_core1) {
        if (!exit_core1) {
            update_backlight_leds();
        }
    }

    presto_obj->presto->cleanup();

    // Restore the original lockout handler and deinit.
    irq_remove_handler(SIO_IRQ_FIFO, presto_core1_lockout_handler);
    irq_set_exclusive_handler(SIO_IRQ_FIFO, sdk_handler);
    multicore_lockout_victim_deinit();

    multicore_fifo_push_blocking(0);
}

#define stack_size 512u
static uint32_t core1_stack[stack_size] = {0};

mp_obj_t Presto_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    _Presto_obj_t *self = nullptr;

    // Clean up any existing instance of Presto.
    (void)Presto___del__(mp_const_none);

    enum { ARG_full_res, ARG_palette, ARG_rotate };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_full_res, MP_ARG_BOOL, {.u_bool = false} },
        { MP_QSTR_palette, MP_ARG_BOOL, {.u_bool = false} },
        { MP_QSTR_rotate, MP_ARG_INT, {.u_int = 0} },
    };

    // Parse args.
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    presto_debug("malloc self\n");
    self = mp_obj_malloc_with_finaliser(_Presto_obj_t, &Presto_type);
    presto_obj = self;

    presto_debug("set fb pointers\n");

    if (!args[ARG_full_res].u_bool) {
        self->width = WIDTH / 2;
        self->height = HEIGHT / 2;
    }
    else {
        self->width = WIDTH;
        self->height = HEIGHT;
    }

    if (args[ARG_palette].u_bool) {
        mp_raise_ValueError(MP_ERROR_TEXT("Presto: palette mode is not supported by the PicoVector rasteriser."));
    }
    self->using_palette = false;

    {
        const size_t pixels = (size_t)self->width * self->height;
        if (pixels <= HALF_PIXELS) {
            // Everything fits in SRAM, so the panel scans the front buffer
            // directly and no line cache is needed.
            presto_buffer = (uint16_t *)presto_sram_pool;
            self->back_buffer = (uint32_t *)(presto_sram_pool + pixels * sizeof(uint16_t));
            self->scanout_cache = nullptr;
            self->psram_frame = nullptr;
        } else {
            presto_buffer = (uint16_t *)presto_sram_pool;
            self->scanout_cache = presto_buffer;
            self->psram_frame = m_new(uint16_t, pixels);
            self->back_buffer = m_new(uint32_t, pixels);
            memset(self->psram_frame, 0, pixels * sizeof(uint16_t));
        }
        self->front_buffer = presto_buffer;
        memset(presto_buffer, 0,
               (self->psram_frame ? (size_t)self->width * FULL_RES_CACHE_LINES : pixels) * sizeof(uint16_t));
        memset(self->back_buffer, 0, pixels * sizeof(uint32_t));
    }

    presto_debug("m_new_class(ST7701...\n");
    Rotation rotation = ROTATE_0;
    switch (args[ARG_rotate].u_int) {
        case 0: rotation = ROTATE_0; break;
        case 180: rotation = ROTATE_180; break;
        default: mp_raise_ValueError(MP_ERROR_TEXT("Presto: rotate must be ROTATE_0 or ROTATE_180."));
    }

    self->presto = new (st7701_buffer) ST7701(self->width, self->height, rotation,
        SPIPins{spi1, LCD_CS, LCD_CLK, LCD_DAT, PIN_UNUSED, LCD_DC, BACKLIGHT},
        presto_buffer, nullptr,
        LCD_D0);

    if (self->psram_frame) {
        self->presto->set_line_cache(self->scanout_cache, FULL_RES_CACHE_LINES, self->psram_frame);
    }

    presto_debug("launch core1\n");
    multicore_reset_core1();
    exit_core1 = false;
    self->auto_ambient_leds = false;

    WS2812::RGB* buffer = m_new(WS2812::RGB, NUM_LEDS);
    self->ws2812 = m_new_class(WS2812, NUM_LEDS, pio0, 3, LED_DAT, WS2812::DEFAULT_SERIAL_FREQ, false, WS2812::COLOR_ORDER::GRB, buffer);
    memset(self->led_values, 0, sizeof(self->led_values));

    // Micropython uses all of both scratch memory (and more!) for core0 stack, 
    // so we must supply our own small stack for core1 here.
    multicore_launch_core1_with_stack(presto_core1_entry, core1_stack, sizeof(core1_stack));
    presto_debug("launched core1\n");

    int res = multicore_fifo_pop_blocking();
    presto_debug("core1 returned\n");

    if(res != 0) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Presto: failed to start ST7701 on Core1."));
    }

    return MP_OBJ_FROM_PTR(self);
}

mp_int_t Presto_get_framebuffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags) {
    _Presto_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);
    (void)flags;
    bufinfo->buf = self->back_buffer;
    bufinfo->len = (size_t)self->width * self->height * sizeof(uint32_t);
    bufinfo->typecode = 'B';
    return 0;
}

extern mp_obj_t Presto_update(mp_obj_t self_in) {
    _Presto_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);

    self->presto->update(self->back_buffer);

    return mp_const_none;
}

extern mp_obj_t Presto_partial_update(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    enum { ARG_self, ARG_x, ARG_y, ARG_w, ARG_h };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_x, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_y, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_w, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_h, MP_ARG_REQUIRED | MP_ARG_INT }
    };

    // Parse args.
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    _Presto_obj_t *self = MP_OBJ_TO_PTR2(args[ARG_self].u_obj, _Presto_obj_t);
    int x = args[ARG_x].u_int;
    int y = args[ARG_y].u_int;
    int w = args[ARG_w].u_int;
    int h = args[ARG_h].u_int;

    self->presto->partial_update(self->back_buffer, x, y, w, h);

    return mp_const_none;
}

mp_obj_t Presto_set_backlight(mp_obj_t self_in, mp_obj_t brightness) {
    _Presto_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);

    float b = mp_obj_get_float(brightness);

    if(b < 0 || b > 1.0f) mp_raise_ValueError(MP_ERROR_TEXT("brightness out of range. Expected 0.0 to 1.0"));

    self->presto->set_backlight((uint8_t)(b * 255.0f));

    return mp_const_none;
}

static void cleanup_leds() {
    void* buffer = presto_obj->ws2812->buffer;
    presto_obj->ws2812->stop();
    presto_obj->ws2812->clear();
    sleep_ms(1);
    presto_obj->ws2812->update(true);
    sleep_ms(1);
    m_del_class(WS2812, presto_obj->ws2812);
    m_del(WS2812::RGB, buffer, NUM_LEDS);
    presto_obj->ws2812 = nullptr;
}

mp_obj_t Presto_auto_ambient_leds(mp_obj_t self_in, mp_obj_t enable) {
    _Presto_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);

    if(mp_obj_is_true(enable)) {
        memset(self->led_values, 0, sizeof(self->led_values));
    }

    self->auto_ambient_leds = mp_obj_is_true(enable);

    return mp_const_none;
}

mp_obj_t Presto_set_led_rgb(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    enum { ARG_self, ARG_index, ARG_r, ARG_g, ARG_b };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_index, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_r, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_g, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_b, MP_ARG_REQUIRED | MP_ARG_INT },
    };

    // Parse args.
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    _Presto_obj_t *self = MP_OBJ_TO_PTR2(args[ARG_self].u_obj, _Presto_obj_t);

    self->led_values[args[ARG_index].u_int] = {(uint32_t)args[ARG_r].u_int, (uint32_t)args[ARG_g].u_int, (uint32_t)args[ARG_b].u_int};

    return mp_const_none;
}

typedef struct _mp_obj_float_t {
    mp_obj_base_t base;
    mp_float_t value;
} mp_obj_float_t;

const mp_obj_float_t const_float_1 = {{&mp_type_float}, 1.0f};

mp_obj_t Presto_set_led_hsv(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    enum { ARG_self, ARG_index, ARG_h, ARG_s, ARG_v };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_index, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_hue, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_sat, MP_ARG_OBJ, {.u_rom_obj = MP_ROM_PTR(&const_float_1)} },
        { MP_QSTR_val, MP_ARG_OBJ, {.u_rom_obj = MP_ROM_PTR(&const_float_1)} },
    };

    // Parse args.
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    _Presto_obj_t *self = MP_OBJ_TO_PTR2(args[ARG_self].u_obj, _Presto_obj_t);

    int index = args[ARG_index].u_int;
    float h = mp_obj_get_float(args[ARG_h].u_obj);
    float s = mp_obj_get_float(args[ARG_s].u_obj);
    float v = mp_obj_get_float(args[ARG_v].u_obj);

    float i = floor(h * 6.0f);
    float f = h * 6.0f - i;
    v *= 255.0f;
    uint8_t p = v * (1.0f - s);
    uint8_t q = v * (1.0f - f * s);
    uint8_t t = v * (1.0f - (1.0f - f) * s);

    switch (int(i) % 6) {
      case 0: self->led_values[index] = {(uint8_t)v, (uint8_t)t, (uint8_t)p}; break;
      case 1: self->led_values[index] = {(uint8_t)q, (uint8_t)v, (uint8_t)p}; break;
      case 2: self->led_values[index] = {(uint8_t)p, (uint8_t)v, (uint8_t)t}; break;
      case 3: self->led_values[index] = {(uint8_t)p, (uint8_t)q, (uint8_t)v}; break;
      case 4: self->led_values[index] = {(uint8_t)t, (uint8_t)p, (uint8_t)v}; break;
      case 5: self->led_values[index] = {(uint8_t)v, (uint8_t)p, (uint8_t)q}; break;
    }

    return mp_const_none;
}

mp_obj_t Presto___del__(mp_obj_t self_in) {
    // Since presto_obj is singleton, relying on __del__ and the finalizer
    // could leave us in a situation where an old Presto instance is garbage
    // collected after we've allocated a new one- ripping out the presto_obj
    // from underneath the new instance.

    _Presto_obj_t *self = nullptr;

    if(self_in != mp_const_none) {
        self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);
    }

    // Only allow an instance to tear down core1 if it's the current owner
    // or if we're explicitly calling `Presto___del__(mp_const_none)` in make_new.
    if(presto_obj == nullptr || (self != nullptr && self != presto_obj)) {
        presto_debug("__del__ called by non-owner, skipping teardown.\n");
        return mp_const_none;
    }

    presto_debug("stop core1\n");
    exit_core1 = true;
    __sev();

    uint32_t fifo_code;
    do {
        while (!multicore_fifo_pop_timeout_us(1000, &fifo_code)) __sev();
        if (fifo_code == 1) {
            cleanup_leds();
        }
    } while (fifo_code != 0);

    presto_debug("core1 stopped\n");

    presto_obj->presto->~ST7701();
    presto_obj->presto = nullptr;
    presto_obj = nullptr;
    
    return mp_const_none;
}

}