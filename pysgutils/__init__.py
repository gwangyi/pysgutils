import ctypes
from . import os

libsgutils2 = None
libc = None


def _load(libsgutils2_path, libc_path):
    global libsgutils2, libc

    libsgutils2 = ctypes.CDLL(libsgutils2_path)
    libc = ctypes.CDLL(libc_path)
    
    def set_res_type(mod, fn, tp):
        try:
            getattr(mod, fn).restype = tp
        except AttributeError:
            pass

    def set_arg_types(mod, fn, *tps):
        try:
            getattr(mod, fn).argtypes = tps
        except AttributeError:
            pass

    set_res_type(libsgutils2, "sg_lib_version", ctypes.c_char_p)
    set_res_type(libsgutils2, "sg_get_sense_key_str", ctypes.c_char_p)
    set_res_type(libsgutils2, "sg_get_sense_info_fld", ctypes.c_bool)
    set_res_type(libsgutils2, "sg_get_sense_filemark_eom_ili", ctypes.c_bool)
    set_res_type(libsgutils2, "sg_get_sense_progress_fld", ctypes.c_bool)
    set_res_type(libsgutils2, "sg_get_desig_type_str", ctypes.c_char_p)
    set_res_type(libsgutils2, "sg_get_desig_code_set_str", ctypes.c_char_p)
    set_res_type(libsgutils2, "sg_get_desig_assoc_str", ctypes.c_char_p)
    set_res_type(libsgutils2, "safe_strerror", ctypes.c_char_p)
    set_res_type(libsgutils2, "sg_is_big_endian", ctypes.c_bool)
    set_res_type(libsgutils2, "sg_get_llnum", ctypes.c_int64)

    set_res_type(libsgutils2, "scsi_pt_version", ctypes.c_char_p)
    set_res_type(libsgutils2, "construct_scsi_pt_obj", ctypes.c_void_p)

    set_arg_types(libsgutils2, "set_scsi_pt_tag", ctypes.c_void_p, ctypes.c_uint64)

    libc.strerror.restype = ctypes.c_char_p

    try:
        stdout = libc.fdopen(1, b'w')
        stderr = libc.fdopen(2, b'w')
    except AttributeError:
        stdout = libc._fdopen(1, b'w')
        stderr = libc._fdopen(2, b'w')
    libc.setbuf(stdout, None)
    libc.setbuf(stderr, None)


def _autoload():
    import sys
    import importlib
    osdep = importlib.import_module("{}.{}".format(os.__name__, sys.platform))
    _load(osdep.libsgutils2, osdep.libc)

_autoload()
