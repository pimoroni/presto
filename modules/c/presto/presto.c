#include "presto.h"


/***** Methods *****/

MP_DEFINE_CONST_FUN_OBJ_1(Presto___del___obj, Presto___del__);
MP_DEFINE_CONST_FUN_OBJ_2(Presto_update_obj, Presto_update);

/***** Binding of Methods *****/

static const mp_rom_map_elem_t Presto_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR___del__), MP_ROM_PTR(&Presto___del___obj) },
    { MP_ROM_QSTR(MP_QSTR_update), MP_ROM_PTR(&Presto_update_obj) },

    { MP_ROM_QSTR(MP_QSTR_WIDTH), MP_ROM_INT(WIDTH) },
    { MP_ROM_QSTR(MP_QSTR_HEIGHT), MP_ROM_INT(HEIGHT) },
};

static MP_DEFINE_CONST_DICT(Presto_locals_dict, Presto_locals_dict_table);


MP_DEFINE_CONST_OBJ_TYPE(
    Presto_type,
    MP_QSTR_Presto,
    MP_TYPE_FLAG_NONE,
    make_new, Presto_make_new,
    buffer, Presto_get_framebuffer,
    locals_dict, (mp_obj_dict_t*)&Presto_locals_dict
);

/***** Globals Table *****/
static const mp_map_elem_t presto_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_presto) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_Presto), (mp_obj_t)&Presto_type },
};

static MP_DEFINE_CONST_DICT(mp_module_presto_globals, presto_globals_table);

/***** Module Definition *****/

const mp_obj_module_t presto_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_presto_globals,
};

MP_REGISTER_MODULE(MP_QSTR_presto, presto_user_cmodule);