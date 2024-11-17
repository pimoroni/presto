// Include MicroPython API.
#include "py/runtime.h"

/***** Constants *****/
static const uint BACKLIGHT = 45;

static const int WIDTH = 480;
static const int HEIGHT = 480;
static const uint LCD_CLK = 26;
static const uint LCD_CS = 28;
static const uint LCD_DAT = 27;
static const uint LCD_DC = -1;
static const uint LCD_D0 = 1;

/***** Extern of Class Definition *****/
extern const mp_obj_type_t Presto_type;

/***** Extern of Class Methods *****/
extern mp_obj_t Presto_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args);
extern mp_obj_t Presto_update(mp_obj_t self_in, mp_obj_t graphics_in);
extern mp_obj_t Presto_partial_update(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args);
extern mp_int_t Presto_get_framebuffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags);
extern mp_obj_t Presto_set_backlight(mp_obj_t self_in, mp_obj_t brightness);
extern mp_obj_t Presto___del__(mp_obj_t self_in);