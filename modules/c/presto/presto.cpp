#include "st7701.hpp"
#include "libraries/pico_graphics/pico_graphics.hpp"
#include "micropython/modules/util.hpp"
#include <cstdio>
#include <cfloat>


#include "hardware/structs/ioqspi.h"
#include "hardware/structs/qmi.h"
#include "hardware/structs/xip_ctrl.h"


using namespace pimoroni;


extern "C" {
#include "presto.h"
#include "py/builtin.h"
#include <stdarg.h>

// MicroPython's GC heap will automatically resize, so we should just
// statically allocate these in C++ to avoid fragmentation.
__attribute__((section(".uninitialized_data"))) static uint16_t presto_buffer[WIDTH * HEIGHT] = {0};

void __printf_debug_flush() {
    for(auto i = 0u; i < 10; i++) {
        sleep_ms(2);
        mp_event_handle_nowait();
    }
}

int mp_vprintf(const mp_print_t *print, const char *fmt, va_list args);

void presto_debug(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int ret = mp_vprintf(&mp_plat_print, fmt, ap);
    va_end(ap);
    __printf_debug_flush();
    (void)ret;
}

/***** Variables Struct *****/
typedef struct _Presto_obj_t {
    mp_obj_base_t base;
    ST7701* presto;
    uint16_t width;
    uint16_t height;
} _Presto_obj_t;

typedef struct _ModPicoGraphics_obj_t {
    mp_obj_base_t base;
    PicoGraphics *graphics;
    DisplayDriver *display;
} ModPicoGraphics_obj_t;



void presto_core1_entry() {
    multicore_fifo_push_blocking(0); // TODO: Remove, debug to signal core has actually started

    ST7701 *presto = (ST7701*)multicore_fifo_pop_blocking();

    presto->init();

    multicore_fifo_push_blocking(0); // Todo handle issues here?*/

    multicore_fifo_pop_blocking(); // Block until exit is sent

    presto->cleanup();

    multicore_fifo_push_blocking(0);
}

#define stack_size 256u
static uint32_t core1_stack[stack_size] = {0};

mp_obj_t Presto_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    _Presto_obj_t *self = nullptr;

    enum { ARG_full_res };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_full_res, MP_ARG_BOOL, {.u_bool = false} }
    };

    // Parse args.
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    presto_debug("malloc self\n");
    self = mp_obj_malloc_with_finaliser(_Presto_obj_t, &Presto_type);

    presto_debug("set fb pointers\n");

    if (!args[ARG_full_res].u_bool) {
        self->width = WIDTH / 2;
        self->height = HEIGHT / 2;
    }
    else {
        self->width = WIDTH;
        self->height = HEIGHT;
    }

    presto_debug("m_new_class(ST7701...\n");
    ST7701 *presto = m_new_class(ST7701, self->width, self->height, ROTATE_0,
        SPIPins{spi1, LCD_CS, LCD_CLK, LCD_DAT, PIN_UNUSED, LCD_DC, BACKLIGHT},
        presto_buffer,
        LCD_D0);

    self->presto = presto;

    presto_debug("launch core1\n");
    multicore_reset_core1();
    //multicore_launch_core1(presto_core1_entry);
    // multicore_launch_core1 probably uses malloc for its stack, and will return but apparently not launch core1 on MicroPython
    multicore_launch_core1_with_stack(presto_core1_entry, core1_stack, stack_size);
    presto_debug("waiting for core1...\n");
    multicore_fifo_pop_blocking();
    presto_debug("core1 running...\n");

    /*presto_debug("presto_set_qmi_timing: ");
    presto_set_qmi_timing();
    presto_debug("ok\n");

    presto_debug("presto_setup_psram: ");
    presto_setup_psram(47);
    presto_debug("ok\n");*/

    presto_debug("signal core1\n");
    multicore_fifo_push_blocking((uintptr_t)self->presto);
    int res = multicore_fifo_pop_blocking();
    presto_debug("core1 returned\n");

    //presto_debug("presto->init(): ");
    //presto->init();
    //presto_debug("ok\n");

    if(res != 0) {
        mp_raise_msg(&mp_type_RuntimeError, "Presto: failed to start ST7701 on Core1.");
    }

    return MP_OBJ_FROM_PTR(self);
}

mp_int_t Presto_get_framebuffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags) {
    _Presto_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);
    (void)flags;
    bufinfo->buf = presto_buffer;
    bufinfo->len = self->width * self->height * 2;
    bufinfo->typecode = 'B';
    return 0;
}

extern mp_obj_t Presto_update(mp_obj_t self_in, mp_obj_t graphics_in) {
    _Presto_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);
    ModPicoGraphics_obj_t *picographics = MP_OBJ_TO_PTR2(graphics_in, ModPicoGraphics_obj_t);

    self->presto->update(picographics->graphics);

    return mp_const_none;
}

extern mp_obj_t Presto_partial_update(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    enum { ARG_self, ARG_graphics, ARG_x, ARG_y, ARG_w, ARG_h };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_graphics, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_x, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_y, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_w, MP_ARG_REQUIRED | MP_ARG_INT },
        { MP_QSTR_h, MP_ARG_REQUIRED | MP_ARG_INT }
    };

    // Parse args.
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    _Presto_obj_t *self = MP_OBJ_TO_PTR2(args[ARG_self].u_obj, _Presto_obj_t);
    ModPicoGraphics_obj_t *picographics = MP_OBJ_TO_PTR2(args[ARG_graphics].u_obj, ModPicoGraphics_obj_t);
    int x = args[ARG_x].u_int;
    int y = args[ARG_y].u_int;
    int w = args[ARG_w].u_int;
    int h = args[ARG_h].u_int;

    self->presto->partial_update(picographics->graphics, {x, y, w, h});

    return mp_const_none;
}

mp_obj_t Presto_set_backlight(mp_obj_t self_in, mp_obj_t brightness) {
    _Presto_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);

    float b = mp_obj_get_float(brightness);

    if(b < 0 || b > 1.0f) mp_raise_ValueError("brightness out of range. Expected 0.0 to 1.0");

    self->presto->set_backlight((uint8_t)(b * 255.0f));

    return mp_const_none;
}

mp_obj_t Presto___del__(mp_obj_t self_in) {
    (void)self_in;
    //_Presto_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Presto_obj_t);
    presto_debug("signal core1\n");
    multicore_fifo_push_blocking(0);
    (void)multicore_fifo_pop_blocking();
    presto_debug("core1 returned\n");

    //self->presto->cleanup();
    //m_del_class(ST7701, self->presto);
    return mp_const_none;
}

}