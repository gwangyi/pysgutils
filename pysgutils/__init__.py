import ctypes
import six
from . import os

libsgutils2 = None
libc = None


def _impl_check(f):
    def not_implemented(*args, **kwargs):
        raise NotImplementedError(f.__name__)

    if hasattr(libsgutils2, f.__name__):
        return f
    else:
        not_implemented.__name__ = f.__name__
        return not_implemented


class Buffer(object):
    def __init__(self, init, size=None):
        if not isinstance(init, (six.integer_types, bytes)):
            init = bytes(init)
            size = len(init)
        self._buffer = ctypes.create_string_buffer(init, size)
        self._as_parameter_ = self._buffer

    def resize(self, size):
        if size > ctypes.sizeof(self._buffer):
            ctypes.resize(self._buffer, size)
        # noinspection PyUnresolvedReferences
        self._as_parameter_ = (ctypes.c_char * size).from_buffer(self._buffer)
        return self

    def __len__(self):
        return len(self._as_parameter_)

    def __getitem__(self, item):
        return self._as_parameter_[item]

    def __setitem__(self, key, value):
        self._as_parameter_[key] = value

    def __iter__(self):
        return iter(self._as_parameter_)

    def __bytes__(self):
        return bytes(self._as_parameter_)


class AlignedBuffer(Buffer):
    alignment = None

    # noinspection PySuperArguments
    def __init__(self, init, size=None, alignment=None):
        if alignment is None:
            alignment = self.alignment
        self._alignment = alignment
        if alignment is None:
            super(AlignedBuffer, self).__init__(init, size)
        else:
            if isinstance(init, six.integer_types):
                size = init
                init = b''
            elif size is None:
                if isinstance(init, bytes):
                    init = init
                    size = len(init) + 1
                else:
                    init = bytes(init)
                    size = len(init)
            super(AlignedBuffer, self).__init__(size + alignment)
            self._as_parameter_ = self._align(self._buffer, size, alignment)
            ctypes.memmove(self._as_parameter_, init, min(len(init), size))

    @staticmethod
    def _align(buffer, size, alignment):
        if alignment & (alignment - 1) != 0:
            raise ValueError("Alignment must be a power of 2")
        address = ctypes.addressof(buffer)
        offset = alignment - (address & (alignment - 1))
        # noinspection PyUnresolvedReferences
        return (ctypes.c_char * size).from_buffer(buffer, offset)

    def resize(self, size):
        if self._alignment is None:
            return super(AlignedBuffer, self).resize(size)
        previous_aligned_buffer = self._as_parameter_
        previous_unaligned_buffer_address = ctypes.addressof(self._buffer)
        super(AlignedBuffer, self).resize(size + self._alignment)
        self._as_parameter_ = self._align(self._buffer, size, self._alignment)
        if ctypes.addressof(self._as_parameter_) != ctypes.addressof(previous_aligned_buffer):
            if ctypes.addressof(self._as_parameter_) - ctypes.addressof(self._buffer) != \
                    ctypes.addressof(previous_aligned_buffer) - previous_unaligned_buffer_address:
                ctypes.memmove(self._as_parameter_, previous_aligned_buffer, len(previous_aligned_buffer))


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
