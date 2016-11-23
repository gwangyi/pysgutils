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
from . import sg_lib

libsgutils2 = None


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


def scsi_pt_open_device(device_name, read_only=False, verbose=False):
    """Returns >= 0 if successful. If error in Unix returns negated errno."""
    ret = libsgutils2.scsi_pt_open_device(device_name.encode('utf-8'), read_only, verbose)
    if ret < 0:
        raise OSError(-ret, sg_lib.safe_strerror(-ret))
    return ret


def scsi_pt_open_flags(device_name, flags=os.O_RDWR, verbose=False):
    """Similar to scsi_pt_open_device() but takes Unix style open flags OR-ed
    together. Returns valid file descriptor( >= 0 ) if successful, otherwise
    returns -1 or a negated errno.
    In Win32 O_EXCL translated to equivalent."""
    ret = libsgutils2.scsi_pt_open_flags(device_name.encode('utf-8'), flags, verbose)
    if ret < 0:
        raise OSError(-ret, sg_lib.safe_strerror(-ret))
    return ret


def scsi_pt_close_device(device_fd):
    """Returns 0 if successful. If error in Unix returns negated errno."""
    ret = libsgutils2.scsi_pt_close_device(device_fd)
    if ret < 0:
        raise OSError(-ret, sg_lib.safe_strerror(-ret))


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


def clear_scsi_pt_obj(objp):
    """Clear state information held in *objp . This allows this object to be
    used to issue more than one SCSI command."""
    libsgutils2.clear_scsi_pt_obj(objp)


def set_scsi_pt_cdb(objp, cdb):
    """Set the CDB (command descriptor block)"""
    libsgutils2.set_scsi_pt_cdb(objp, cdb, len(cdb))


def set_scsi_pt_sense(objp, sense):
    """Set the sense buffer and the maximum length that it can handle"""
    libsgutils2.set_scsi_pt_sense(objp, sense, len(sense))


def set_scsi_pt_data_in(objp, dxferp):
    """Set a pointer and length to be used for data transferred from device"""
    libsgutils2.set_scsi_pt_data_in(objp, dxferp, len(dxferp))


def set_scsi_pt_data_out(objp, dxferp):
    """Set a pointer and length to be used for data transferred to device"""
    libsgutils2.set_scsi_pt_data_out(objp, dxferp, len(dxferp))


def set_scsi_pt_packet_id(objp, packet_id):
    """The following "set_"s implementations may be dummies"""
    libsgutils2.set_scsi_pt_packet_id(objp, packet_id)


def set_scsi_pt_tag(objp, tag):
    libsgutils2.set_scsi_pt_tag(objp, tag)


def set_scsi_pt_task_management(objp, tmf_code):
    libsgutils2.set_scsi_pt_task_management(objp, tmf_code)


def set_scsi_pt_task_attr(objp, attribute, priority):
    libsgutils2.set_scsi_pt_task_attr(objp, attribute, priority)


class SCSIPTFlags(enum.IntEnum):
    """Following is a guard which is defined when set_scsi_pt_flags() is
    present. Older versions of this library may not have this function.
    If neither QUEUE_AT_HEAD nor QUEUE_AT_TAIL are given, or both
    are given, use the pass-through default."""
    FUNCTION = 1
    QUEUE_AT_TAIL = 0x10
    QUEUE_AT_HEAD = 0x20


def set_scsi_pt_flags(objp, flags):
    """Set (potentially OS dependant) flags for pass-through mechanism.
    Apart from contradictions, flags can be OR-ed together."""
    libsgutils2.set_scsi_pt_flags(objp, flags)


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


def get_scsi_pt_result_category(objp):
    """highest numbered applicable category returned"""
    return SCSIPTResult(libsgutils2.get_scsi_pt_result_category(objp))


def get_scsi_pt_resid(objp):
    """If not available return 0"""
    return libsgutils2.get_scsi_pt_resid(objp)


def get_scsi_pt_status_response(objp):
    """Returns SCSI status value (from device that received the
    command)."""
    return sg_lib.SCSIStatusCode(libsgutils2.get_scsi_pt_status_response(objp))


def get_scsi_pt_sense_len(objp):
    """Actual sense length returned. If sense data is present but
    actual sense length is not known, return 'max_sense_len'"""
    return libsgutils2.get_scsi_pt_sense_len(objp)


def get_scsi_pt_os_err(objp):
    """If not available return 0"""
    return libsgutils2.get_scsi_pt_os_err(objp)


def get_scsi_pt_os_err_str(objp):
    buffer = ctypes.create_string_buffer(512)
    libsgutils2.get_scsi_pt_os_err_str(objp, 512, ctypes.byref(buffer))
    return buffer.value.decode('utf-8')


def get_scsi_pt_transport_err(objp):
    """If not available return 0"""
    return libsgutils2.get_scsi_pt_transport_err(objp)


def get_scsi_pt_transport_err_str(objp):
    buffer = ctypes.create_string_buffer(512)
    libsgutils2.get_scsi_pt_transport_err_str(objp, 512, ctypes.byref(buffer))
    return buffer.value.decode('utf-8')


def get_scsi_pt_duration_ms(objp):
    """If not available return -1"""
    ret = libsgutils2.get_scsi_pt_duration_ms(objp)
    if ret == -1:
        return None
    else:
        return ret


def destruct_scsi_pt_obj(objp):
    """Should be invoked once per objp after other processing is complete in
    order to clean up resources. For ever successful construct_scsi_pt_obj()
    call there should be one destruct_scsi_pt_obj()."""
    libsgutils2.destruct_scsi_pt_obj(objp)


def scsi_pt_win32_direct(objp, state_direct):
    """Request SPT direct interface when state_direct is 1, state_direct set
    to 0 for the SPT indirect interface. Default setting selected by build
    (i.e. library compile time) and is usually indirect."""
    try:
        libsgutils2.scsi_pt_win32_direct(objp, state_direct)
    except AttributeError:
        pass


def scsi_pt_win32_spt_state():
    try:
        return libsgutils2.scsi_pt_win32_spt_state() != 0
    except AttributeError:
        pass
