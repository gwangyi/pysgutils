"""
:mod:`pysgutils.sg_pt`
~~~~~~~~~~~~~~~~~~~~~~

Python port of sg_pt.h from sg3_utils

Comments from sg_pt.h:

Copyright (c) 2005-2014 Douglas Gilbert.
All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the BSD_LICENSE file.
"""
from __future__ import absolute_import
import os
import ctypes
import enum
import errno
import sys
import six
import weakref
from . import sg_lib, libsgutils2, _impl_check


class SGPTBase(ctypes.c_void_p):
    """
    This declaration hides the fact that each implementation has its own
    structure "derived" (using a C++ term) from this one. It compiles
    because 'struct sg_pt_base' is only referenced (by pointer: 'objp')
    in this interface. An instance of this structure represents the
    context of one SCSI command.
    """


def scsi_pt_version():
    """The format of the version string is like this: "2.01 20090201".
    The leading digit will be incremented if this interface changes
    in a way that may impact backward compatibility."""
    return libsgutils2.scsi_pt_version().decode('utf-8')


@_impl_check
def scsi_pt_open_device(device_name, read_only=False, verbose=False):
    """Returns >= 0 if successful. If error in Unix returns negated errno."""
    ret = libsgutils2.scsi_pt_open_device(device_name.encode('utf-8'), read_only, verbose)
    if ret < 0:
        raise OSError(-ret, sg_lib.safe_strerror(-ret))
    return ret


@_impl_check
def scsi_pt_open_flags(device_name, flags=os.O_RDWR, verbose=False):
    """Similar to scsi_pt_open_device() but takes Unix style open flags OR-ed
    together. Returns valid file descriptor( >= 0 ) if successful, otherwise
    returns -1 or a negated errno.
    In Win32 O_EXCL translated to equivalent."""
    ret = libsgutils2.scsi_pt_open_flags(device_name.encode('utf-8'), flags, verbose)
    if ret < 0:
        raise OSError(-ret, sg_lib.safe_strerror(-ret))
    return ret


@_impl_check
def scsi_pt_close_device(device_fd):
    """Returns 0 if successful. If error in Unix returns negated errno."""
    ret = libsgutils2.scsi_pt_close_device(device_fd)
    if ret < 0:
        raise OSError(-ret, sg_lib.safe_strerror(-ret))


@_impl_check
def construct_scsi_pt_obj():
    """Creates an object that can be used to issue one or more SCSI commands
    (or task management functions). Returns NULL if problem.
    Once this object has been created it should be destroyed with
    destruct_scsi_pt_obj() when it is no longer needed."""
    ret = libsgutils2.construct_scsi_pt_obj()
    if ret == 0:
        raise MemoryError("Construction of scsi pt object is failed")
    else:
        return SGPTBase(ret)


@_impl_check
def clear_scsi_pt_obj(objp):
    """Clear state information held in *objp . This allows this object to be
    used to issue more than one SCSI command."""
    libsgutils2.clear_scsi_pt_obj(objp)


@_impl_check
def set_scsi_pt_cdb(objp, cdb):
    """Set the CDB (command descriptor block)"""
    libsgutils2.set_scsi_pt_cdb(objp, cdb, len(cdb))


@_impl_check
def set_scsi_pt_sense(objp, sense):
    """Set the sense buffer and the maximum length that it can handle"""
    libsgutils2.set_scsi_pt_sense(objp, sense, len(sense))


@_impl_check
def set_scsi_pt_data_in(objp, dxferp):
    """Set a pointer and length to be used for data transferred from device"""
    libsgutils2.set_scsi_pt_data_in(objp, dxferp, len(dxferp))


@_impl_check
def set_scsi_pt_data_out(objp, dxferp):
    """Set a pointer and length to be used for data transferred to device"""
    libsgutils2.set_scsi_pt_data_out(objp, dxferp, len(dxferp))


@_impl_check
def set_scsi_pt_packet_id(objp, packet_id):
    """The following "set_"s implementations may be dummies"""
    libsgutils2.set_scsi_pt_packet_id(objp, packet_id)


@_impl_check
def set_scsi_pt_tag(objp, tag):
    libsgutils2.set_scsi_pt_tag(objp, tag)


@_impl_check
def set_scsi_pt_task_management(objp, tmf_code):
    libsgutils2.set_scsi_pt_task_management(objp, tmf_code)


@_impl_check
def set_scsi_pt_task_attr(objp, attribute, priority):
    libsgutils2.set_scsi_pt_task_attr(objp, attribute, priority)


class SCSIPTFlags(enum.IntEnum):
    """Following is a guard which is defined when set_scsi_pt_flags() is
    present. Older versions of this library may not have this function.
    If neither QUEUE_AT_HEAD nor QUEUE_AT_TAIL are given, or both
    are given, use the pass-through default."""
    NONE = 0
    FUNCTION = 1
    QUEUE_AT_TAIL = 0x10
    QUEUE_AT_HEAD = 0x20


@_impl_check
def set_scsi_pt_flags(objp, flags):
    """Set (potentially OS dependant) flags for pass-through mechanism.
    Apart from contradictions, flags can be OR-ed together."""
    libsgutils2.set_scsi_pt_flags(objp, flags)


@_impl_check
def do_scsi_pt(objp, fd, timeout_secs, verbose=False):
    """If OS error prior to or during command submission then returns negated
    error value (e.g. Unix '-errno'). This includes interrupted system calls
    (e.g. by a signal) in which case -EINTR would be returned. Note that
    system call errors also can be fetched with get_scsi_pt_os_err().
    Return 0 if okay (i.e. at the very least: command sent). Positive
    return values are errors (see SCSI_PT_DO_* defines)."""
    ret = libsgutils2.do_scsi_pt(objp, fd, timeout_secs, verbose)
    if ret < 0:
        raise OSError(-ret, sg_lib.safe_strerror(-ret))
    elif ret == 1:
        raise ValueError("SCSI_PT_DO_BAD_PARAMS (1)")
    elif ret == 2:
        if sys.version_info > (3,):
            # noinspection PyCompatibility
            raise TimeoutError("SCSI_PT_DO_TIMEOUT (2)")
        else:
            raise OSError(errno.ETIMEDOUT, "SCSI_PT_DO_TIMEOUT (2)")


class SCSIPTResult(enum.IntEnum):
    GOOD = 0
    #: other than GOOD and CHECK CONDITION
    STATUS = 1
    SENSE = 2
    TRANSPORT_ERR = 3
    OS_ERR = 4


@_impl_check
def get_scsi_pt_result_category(objp):
    """highest numbered applicable category returned"""
    return SCSIPTResult(libsgutils2.get_scsi_pt_result_category(objp))


@_impl_check
def get_scsi_pt_resid(objp):
    """If not available return 0"""
    return libsgutils2.get_scsi_pt_resid(objp)


@_impl_check
def get_scsi_pt_status_response(objp):
    """Returns SCSI status value (from device that received the
    command)."""
    return sg_lib.SCSIStatusCode(libsgutils2.get_scsi_pt_status_response(objp))


@_impl_check
def get_scsi_pt_sense_len(objp):
    """Actual sense length returned. If sense data is present but
    actual sense length is not known, return 'max_sense_len'"""
    return libsgutils2.get_scsi_pt_sense_len(objp)


@_impl_check
def get_scsi_pt_os_err(objp):
    """If not available return 0"""
    return libsgutils2.get_scsi_pt_os_err(objp)


@_impl_check
def get_scsi_pt_os_err_str(objp):
    buffer = ctypes.create_string_buffer(512)
    libsgutils2.get_scsi_pt_os_err_str(objp, 512, ctypes.byref(buffer))
    return buffer.value.decode('utf-8')


@_impl_check
def get_scsi_pt_transport_err(objp):
    """If not available return 0"""
    return libsgutils2.get_scsi_pt_transport_err(objp)


@_impl_check
def get_scsi_pt_transport_err_str(objp):
    buffer = ctypes.create_string_buffer(512)
    libsgutils2.get_scsi_pt_transport_err_str(objp, 512, ctypes.byref(buffer))
    return buffer.value.decode('utf-8')


@_impl_check
def get_scsi_pt_duration_ms(objp):
    """If not available return -1"""
    ret = libsgutils2.get_scsi_pt_duration_ms(objp)
    if ret == -1:
        return None
    else:
        return ret


@_impl_check
def destruct_scsi_pt_obj(objp):
    """Should be invoked once per objp after other processing is complete in
    order to clean up resources. For ever successful construct_scsi_pt_obj()
    call there should be one destruct_scsi_pt_obj()."""
    libsgutils2.destruct_scsi_pt_obj(objp)


@_impl_check
def scsi_pt_win32_direct(objp, state_direct):
    """Request SPT direct interface when state_direct is 1, state_direct set
    to 0 for the SPT indirect interface. Default setting selected by build
    (i.e. library compile time) and is usually indirect."""
    try:
        libsgutils2.scsi_pt_win32_direct(objp, state_direct)
    except AttributeError:
        pass


@_impl_check
def scsi_pt_win32_spt_state():
    try:
        return libsgutils2.scsi_pt_win32_spt_state() != 0
    except AttributeError:
        pass


class SCSIPTDevice(object):
    _refs = weakref.WeakValueDictionary()
    _stack = [None]

    def __init__(self, device_name, read_only_or_flags=False, verbose=False, **kwargs):
        if 'flags' in kwargs:
            read_only_or_flags = kwargs['flags']
        elif 'read_only' in kwargs:
            read_only_or_flags = kwargs['read_only']

        if isinstance(read_only_or_flags, bool):
            self._fd = scsi_pt_open_device(device_name, read_only_or_flags, verbose)
        elif isinstance(read_only_or_flags, six.integer_types):
            self._fd = scsi_pt_open_flags(device_name, read_only_or_flags, verbose)
        else:
            raise ValueError("read_only_or_flags must be one of bool or integer value")

        self.device_name = device_name
        self._refs[id(self)] = self

    def __repr__(self):
        return "<{}: {}, fd: {}>".format(type(self).__qualname__, self.device_name, self._fd)

    def __del__(self):
        if self._fd is not None:
            self.close()

    def close(self):
        scsi_pt_close_device(self._fd)
        self._fd = None

    def enter(self):
        self._stack.append(self)

    def exit(self):
        self._stack.pop()

    @classmethod
    def current(cls):
        return cls._stack[-1]

    def __enter__(self):
        return self.enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.exit()


class SCSIPTObject(object):
    _refs = weakref.WeakValueDictionary()
    timeout = 5

    class TaskAttr(object):
        def __init__(self, pt_obj):
            self._pt_obj = pt_obj
            self._attrs = dict()

        def __getitem__(self, item):
            return self._attrs.get(item, None)

        def __setitem__(self, key, value):
            set_scsi_pt_task_attr(self._pt_obj, key, value)
            self._attrs[key] = value

    def __init__(self):
        self._pt_obj = construct_scsi_pt_obj()
        self._cdb = None
        self._sense = None
        self._data_in = None
        self._data_out = None
        self._packet_id = None
        self._tag = None
        self._task_management = None
        self.task_attr = self.TaskAttr(self._pt_obj)
        self._flags = SCSIPTFlags.NONE
        try:
            self._win32_direct = scsi_pt_win32_spt_state()
        except NotImplementedError:
            self._win32_direct = None
        self._refs[id(self)] = self

    def clear(self):
        clear_scsi_pt_obj(self._pt_obj)

    def __del__(self):
        destruct_scsi_pt_obj(self._pt_obj)

    @property
    def cdb(self):
        return self._cdb

    @cdb.setter
    def cdb(self, val):
        set_scsi_pt_cdb(self._pt_obj, val)
        if isinstance(val, sg_lib.SCSICommand):
            self._cdb = val
        else:
            self._cdb = sg_lib.SCSICommand(bytes(val))

    @property
    def sense(self):
        return self._sense

    @sense.setter
    def sense(self, val):
        set_scsi_pt_sense(self._pt_obj, val)
        self._sense = val

    @property
    def data_in(self):
        return self._data_in

    @data_in.setter
    def data_in(self, val):
        set_scsi_pt_data_in(self._pt_obj, val)
        self._data_in = val

    @property
    def data_out(self):
        return self._data_out

    @data_out.setter
    def data_out(self, val):
        set_scsi_pt_data_out(self._pt_obj, val)
        self._data_out = val

    @property
    def packet_id(self):
        return self._packet_id

    @packet_id.setter
    def packet_id(self, val):
        set_scsi_pt_packet_id(self._pt_obj, val)
        self._packet_id = val

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, val):
        set_scsi_pt_tag(self._pt_obj, val)
        self._tag = val

    @property
    def task_management(self):
        return self._task_management

    @task_management.setter
    def task_management(self, val):
        set_scsi_pt_task_management(self._pt_obj, val)
        self._task_management = val

    @property
    def result_category(self):
        return get_scsi_pt_result_category(self._pt_obj)

    @property
    def resid(self):
        return get_scsi_pt_resid(self._pt_obj)

    @property
    def status_response(self):
        return get_scsi_pt_status_response(self._pt_obj)

    @property
    def sense_len(self):
        return get_scsi_pt_sense_len(self._pt_obj)

    @property
    def os_err(self):
        return get_scsi_pt_os_err(self._pt_obj)

    @property
    def os_err_str(self):
        return get_scsi_pt_os_err_str(self._pt_obj)

    @property
    def transport_err(self):
        return get_scsi_pt_transport_err(self._pt_obj)

    @property
    def transport_err_str(self):
        return get_scsi_pt_transport_err_str(self._pt_obj)

    @property
    def duration_ms(self):
        return get_scsi_pt_duration_ms(self._pt_obj)

    @property
    def win32_direct(self):
        return self._win32_direct

    @win32_direct.setter
    def win32_direct(self, val):
        scsi_pt_win32_direct(self._pt_obj, val)
        self._win32_direct = val

    def do_scsi_pt(self, timeout=None, device=None, verbose=False):
        if device is None:
            device = SCSIPTDevice.current()
        if device is None:
            raise ValueError("Device is not specified")
        if timeout is None:
            timeout = self.timeout
        do_scsi_pt(self._pt_obj, device._fd, timeout, verbose)
        return self.result_category
