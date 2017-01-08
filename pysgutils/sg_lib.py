"""
:mod:`pysgutils.sg_lib`
~~~~~~~~~~~~~~~~~~~~~~~

Python port of sg_lib.h from sg3_utils

Comments from sg_lib.h:

Copyright (c) 2004-2016 Douglas Gilbert.
All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the BSD_LICENSE file.

On 5th October 2004 a FreeBSD license was added to this file.
The intention is to keep this file and the related sg_lib.c file
as open source and encourage their unencumbered use.

Current version number is in the sg_lib.c file and can be accessed
with the sg_lib_version() function.

This header file contains defines and function declarations that may
be useful to applications that communicate with devices that use a
SCSI command set. These command sets have names like SPC-4, SBC-3,
SSC-3, SES-2 and draft standards defining them can be found at
http://www.t10.org . Virtually all devices in the Linux SCSI subsystem
utilize SCSI command sets. Many devices in other Linux device subsystems
utilize SCSI command sets either natively or via emulation (e.g. a
parallel ATA disk in a USB enclosure).
"""
import six
import ctypes
import struct
import enum
import threading
from . import libsgutils2, libc, _impl_check

_thread_store = threading.local()


def _get_buffer(size):
    if size == 0:
        return None
    if not hasattr(_thread_store, 'buffer'):
        if size < 4096:
            size_ = 4096
        else:
            size_ = size
        _thread_store.buffer = ctypes.create_string_buffer(size_)
    elif size > ctypes.sizeof(_thread_store.buffer):
        ctypes.resize(_thread_store.buffer, size)
    return (ctypes.c_char * size).from_buffer(_thread_store.buffer)


def _copy_buffer(data):
    if not data:
        return None
    size = len(data)
    if not hasattr(_thread_store, 'buffer'):
        if size < 4096:
            size_ = 4096
        else:
            size_ = size
        _thread_store.buffer = ctypes.create_string_buffer(size_)
    elif size > ctypes.sizeof(_thread_store.buffer):
        ctypes.resize(_thread_store.buffer, size)
    ctypes.memmove(_thread_store.buffer, data, size)
    return (ctypes.c_char * size).from_buffer(_thread_store.buffer)



@six.python_2_unicode_compatible
class PeripheralDeviceTypes(enum.IntEnum):
    """ SCSI Peripheral Device Types (PDT) [5 bit field] """
    DISK = 0x0  #: direct access block device (disk)
    TAPE = 0x1  #: sequential access device (magnetic tape)
    PRINTER = 0x2  #: printer device (see SSC-1)
    PROCESSOR = 0x3  #: processor device (e.g. SAFTE device)
    WO = 0x4  #: write once device (some optical disks)
    MMC = 0x5  #: CD/DVD/BD (multi-media)
    SCANNER = 0x6  #: obsolete
    OPTICAL = 0x7  #: optical memory device (some optical disks)
    MCHANGER = 0x8  #: media changer device (e.g. tape robot)
    COMMS = 0x9  #: communications device (obsolete)
    SAC = 0xc  #: storage array controller device
    SES = 0xd  #: SCSI Enclosure Services (SES) device
    RBC = 0xe  #: Reduced Block Commands (simplified PDT_DISK)
    OCRW = 0xf  #: optical card read/write device
    BCC = 0x10  #: bridge controller commands
    OSD = 0x11  #: Object Storage Device (OSD)
    ADC = 0x12  #: Automation/drive commands (ADC)
    SMD = 0x13  #: Security Manager Device (SMD)
    ZBC = 0x14  #: Zoned Block Commands (ZBC)
    WLUN = 0x1e  #: Well known logical unit (WLUN)
    UNKNOWN = 0x1f  #: Unknown or no device type

    def __str__(self):
        return sg_get_pdt_str(self)

    @property
    def decay(self):
        return sg_lib_pdt_decay(self)


@six.python_2_unicode_compatible
class SCSIStatusCode(enum.IntEnum):
    """ The SCSI status codes as found in SAM-4 at www.t10.org """
    GOOD = 0x0
    CHECK_CONDITION = 0x2
    CONDITION_MET = 0x4
    BUSY = 0x8
    INTERMEDIATE = 0x10  #: obsolete in SAM-4
    INTERMEDIATE_CONDITION_MET = 0x14  #: obsolete in SAM-4
    RESERVATION_CONFLICT = 0x18
    COMMAND_TERMINATED = 0x22  #: obsolete in SAM-3
    TASK_SET_FULL = 0x28
    ACA_ACTIVE = 0x30
    TASK_ABORTED = 0x40

    def __str__(self):
        return sg_get_scsi_status_str(self)


@six.python_2_unicode_compatible
class SCSISenseKeyCode(enum.IntEnum):
    """ The SCSI sense key codes as found in SPC-4 at www.t10.org """
    NO_SENSE = 0x0
    RECOVERED_ERROR = 0x1
    NOT_READY = 0x2
    MEDIUM_ERROR = 0x3
    HARDWARE_ERROR = 0x4
    ILLEGAL_REQUEST = 0x5
    UNIT_ATTENTION = 0x6
    DATA_PROTECT = 0x7
    BLANK_CHECK = 0x8
    VENDOR_SPECIFIC = 0x9
    COPY_ABORTED = 0xa
    ABORTED_COMMAND = 0xb
    RESERVED = 0xc
    VOLUME_OVERFLOW = 0xd
    MISCOMPARE = 0xe
    COMPLETED = 0xf

    def __str__(self):
        return sg_get_sense_key_str(self)


@six.python_2_unicode_compatible
class TransportProtocol(enum.IntEnum):
    """ Transport protocol identifiers or just Protocol identifiers """
    FCP = 0
    SPI = 1
    SSA = 2
    IEEE1394 = 3
    SRP = 4  #: SCSI over RDMA 
    ISCSI = 5
    SAS = 6
    ADT = 7
    ATA = 8
    UAS = 9  #: USB attached SCSI 
    SOP = 0xa  #: SCSI over PCIe 
    PCIE = 0xb  #: includes NVMe 
    NONE = 0xf

    def __str__(self):
        return sg_get_trans_proto_str(self)


def sg_lib_version():
    """ The format of the version string is like this: "1.87 20130731" """
    return libsgutils2.sg_lib_version().decode('utf-8')


@_impl_check
def sg_get_command_size(cdb_byte0):
    """
    Returns length of SCSI command given the opcode (first byte).
    Yields the wrong answer for variable length commands (opcode=0x7f)
    and potentially some vendor specific commands. """
    if isinstance(cdb_byte0, six.integer_types):
        cdb_byte0_ = cdb_byte0
    else:
        cdb_byte0_ = cdb_byte0[0]
    return libsgutils2.sg_get_command_size(cdb_byte0_)


@_impl_check
def sg_get_command_name(cdb, peri_type):
    """
    Command name given pointer to the cdb. Certain command names
    depend on peripheral type (give 0 or -1 if unknown). Places command
    name into buff and will write no more than buff_len bytes.
    """
    buff = _get_buffer(128)
    libsgutils2.sg_get_command_name(cdb, peri_type, 128, ctypes.byref(buff))
    return buff.value.decode('utf-8')


@_impl_check
def sg_get_opcode_name(cdb_byte0, peri_type):
    """
    Command name given only the first byte (byte 0) of a cdb and
    peripheral type (give 0 or -1 if unknown).
    """
    if isinstance(cdb_byte0, six.integer_types):
        cdb_byte0_ = cdb_byte0
    else:
        cdb_byte0_ = cdb_byte0[0]
    buff = _get_buffer(80)
    libsgutils2.sg_get_opcode_name(cdb_byte0_, peri_type, 80, ctypes.byref(buff))
    return buff.value.decode('utf-8')


@_impl_check
def sg_get_opcode_sa_name(cdb_byte0, service_action, peri_type):
    """
    Command name given opcode (byte 0), service action and peripheral type.
    If no service action give 0, if unknown peripheral type give 0 or -1 .
    """
    if isinstance(cdb_byte0, six.integer_types):
        cdb_byte0_ = cdb_byte0
    else:
        cdb_byte0_ = cdb_byte0[0]
    buff = _get_buffer(128)
    libsgutils2.sg_get_opcode_sa_name(cdb_byte0_, service_action, peri_type, 128, ctypes.byref(buff))
    return buff.value.decode('utf-8')


@_impl_check
def sg_get_scsi_status_str(scsi_status):
    """ Fetch scsi status string. """
    buff = _get_buffer(128)
    libsgutils2.sg_get_scsi_status_str(scsi_status, 128, ctypes.byref(buff))
    return buff.value.decode('utf-8')


class SCSISenseHdr:
    """
    This is a slightly stretched SCSI sense "descriptor" format header.
    The addition is to allow the 0x70 and 0x71 response codes. The idea
    is to place the salient data of both "fixed" and "descriptor" sense
    format into one structure to ease application processing.
    The original sense buffer should be kept around for those cases
    in which more information is required (e.g. the LBA of a MEDIUM ERROR).
    """
    def __init__(self, response_code, sense_key, asc, ascq, byte4, byte5, byte6, additional_length):
        self.response_code = response_code  # permit: 0x0, 0x70, 0x71, 0x72, 0x73
        self.sense_key = sense_key
        self.asc = asc
        self.ascq = ascq
        self.byte4 = byte4
        self.byte5 = byte5
        self.byte6 = byte6
        self.additional_length = additional_length


@_impl_check
def sg_scsi_normalize_sense(sense):
    """
    Maps the salient data from a sense buffer which is in either fixed or
    descriptor format into a structure mimicking a descriptor format
    header (i.e. the first 8 bytes of sense descriptor format).
    If zero response code returns 0. Otherwise returns 1 and if 'sshp' is
    non-NULL then zero all fields and then set the appropriate fields in
    that structure. sshp::additional_length is always 0 for response
    codes 0x70 and 0x71 (fixed format).
    """
    buff = _get_buffer(8)
    ret = libsgutils2.sg_scsi_normalize_sense(sense, len(sense), ctypes.byref(buff))
    if ret == 0:
        return None
    else:
        response_code, sense_key, asc, ascq, byte4, byte5, byte6, additional_length = struct.unpack("8B", bytes(buff))
        return SCSISenseHdr(response_code=response_code, sense_key=sense_key, asc=asc, ascq=ascq,
                            byte4=byte4, byte5=byte5, byte6=byte6, additional_length=additional_length)


@_impl_check
def sg_scsi_sense_desc_find(sense, desc_type):
    """
    Attempt to find the first SCSI sense data descriptor that matches the
    given 'desc_type'. If found return pointer to start of sense data
    descriptor; otherwise (including fixed format sense data) returns NULL.
    """
    buffer = _copy_buffer(sense)
    ret = libsgutils2.sg_scsi_sense_desc_find(buffer, len(buffer), desc_type)
    if ret == 0:
        return None
    else:
        return sense[ret - ctypes.addressof(buffer):]


@_impl_check
def sg_get_sense_key(sense):
    """
    Get sense key from sense buffer. If successful returns a sense key value
    between 0 and 15. If sense buffer cannot be decode, returns -1 .
    """
    ret = libsgutils2.sg_get_sense_key(sense, len(sense))
    if ret == -1:
        return None
    else:
        try:
            return SCSISenseKeyCode(ret)
        except ValueError:
            return ret


@_impl_check
def sg_get_sense_key_str(sense_key):
    """ Yield string associated with sense_key value. Returns 'buff'. """
    buff = _get_buffer(80)
    libsgutils2.sg_get_sense_key_str(sense_key, 80, ctypes.byref(buff))
    return buff.value.decode('utf-8')


@_impl_check
def sg_get_asc_ascq_str(asc, ascq):
    """ Yield string associated with ASC/ASCQ values. Returns 'buff'. """
    buff = _get_buffer(128)
    libsgutils2.sg_get_asc_ascq_str(asc, ascq, 128, ctypes.byref(buff))
    return buff.value.decode('utf-8')


@_impl_check
def sg_get_sense_info_fld(sense):
    """
    Returns 1 if valid bit set, 0 if valid bit clear. Irrespective the
    information field is written out via 'info_outp' (except when it is
    NULL). Handles both fixed and descriptor sense formats.
    """
    info = ctypes.c_uint64()
    ret = libsgutils2.sg_get_sense_info_fld(sense, len(sense), ctypes.byref(info))
    return ret, info.value


@_impl_check
def sg_get_sense_filemark_eom_ili(sense):
    """
    Returns 1 if any of the 3 bits (i.e. FILEMARK, EOM or ILI) are set.
    In descriptor format if the stream commands descriptor not found
    then returns 0. Writes 1 or 0 corresponding to these bits to the
    last three arguments if they are non-NULL.
    """
    filemark = ctypes.c_int()
    eom = ctypes.c_int()
    ili = ctypes.c_int()
    ret = libsgutils2.sg_get_sense_filemark_eom_ili(
        sense, len(sense), ctypes.byref(filemark), ctypes.byref(eom), ctypes.byref(ili))

    return ret, filemark.value != 0, eom.value != 0, ili.value != 0


@_impl_check
def sg_get_sense_progress_fld(sense):
    """
    Returns 1 if SKSV is set and sense key is NO_SENSE or NOT_READY. Also
    returns 1 if progress indication sense data descriptor found. Places
    progress field from sense data where progress_outp points. If progress
    field is not available returns 0. Handles both fixed and descriptor
    sense formats. N.B. App should multiply by 100 and divide by 65536
    to get percentage completion from given value.
    """
    progress = ctypes.c_int()
    ret = libsgutils2.sg_get_sense_progress_fld(sense, len(sense), ctypes.byref(progress))
    return ret, progress.value


@_impl_check
def sg_get_sense_str(leadin, sense, raw_sinfo):
    """
    Closely related to sg_print_sense(). Puts decoded sense data in 'buff'.
    Usually multiline with multiple '\n' including one trailing. If
    'raw_sinfo' set appends sense buffer in hex. 'leadin' is string prepended
    to each line written to 'buff', NULL treated as "". Returns the number of
    bytes written to 'buff' excluding the trailing '\0'.
    N.B. prior to sg3_utils v 1.42 'leadin' was only prepended to the first
    line output. Also this function returned type void.
    """
    if leadin is None:
        leadin_ = None
    else:
        leadin_ = leadin.encode('utf-8')
    buff = _get_buffer(2048)
    # In some version of sg3_utils, sg_get_sense_str returns void, not the length of returned string
    ret = libsgutils2.sg_get_sense_str(leadin_, sense, len(sense), raw_sinfo, 2048, ctypes.byref(buff))
    if ret == 0:
        return buff.value.decode('utf-8')
    else:
        return buff[:ret].decode('utf-8')


@_impl_check
def sg_get_sense_descriptors_str(leadin, sense):
    """
    Decode descriptor format sense descriptors (assumes sense buffer is
    in descriptor format). 'leadin' is string prepended to each line written
    to 'b', NULL treated as "". Returns the number of bytes written to 'b'
    excluding the trailing '\0'.
    """
    if leadin is None:
        leadin_ = None
    else:
        leadin_ = leadin.encode('utf-8')
    buff = _get_buffer(2048)
    ret = libsgutils2.sg_get_sense_descriptors_str(leadin_, sense, len(sense), 2048, ctypes.byref(buff))
    return buff[:ret].decode('utf-8')


@_impl_check
def sg_get_designation_descriptor_str(leadin, ddp, print_assoc=False, do_long=False):
    """
    Decodes a designation descriptor (e.g. as found in the Device
    Identification VPD page (0x83)) into string 'b' whose maximum length is
    blen. 'leadin' is string prepended to each line written to 'b', NULL
    treated as "". Returns the number of bytes written to 'b' excluding the
    trailing '\0'.
    """
    if leadin is None:
        leadin_ = None
    else:
        leadin_ = leadin.encode('utf-8')
    buff = _get_buffer(2048)
    ret = libsgutils2.sg_get_designation_descriptor_str(leadin_, ddp, len(ddp),
                                                        print_assoc, do_long, 2048, ctypes.byref(buff))
    return buff[:ret].decode('utf-8')


@_impl_check
def sg_get_pdt_str(pdt):
    """
    Yield string associated with peripheral device type (pdt). Returns
    'buff'. If 'pdt' out of range yields "bad pdt" string.
    """
    buff = _get_buffer(48)
    libsgutils2.sg_get_pdt_str(pdt, 48, ctypes.byref(buff))
    return buff.value.decode('utf-8')


@_impl_check
def sg_lib_pdt_decay(pdt):
    """
    Some lesser used PDTs share a lot in common with a more used PDT.
    Examples are PDT_ADC decaying to PDT_TAPE and PDT_ZBC to PDT_DISK.
    If such a lesser used 'pdt' is given to this function, then it will
    return the more used PDT (i.e. "decays to"); otherwise 'pdt' is returned.
    Valid for 'pdt' 0 to 31, for other values returns 0.
    """
    return PeripheralDeviceTypes(libsgutils2.sg_lib_pdt_decay(pdt))


@_impl_check
def sg_get_trans_proto_str(tpi):
    """
    Yield string associated with transport protocol identifier (tpi). Returns
    'buff'. If 'tpi' out of range yields "bad tpi" string.
    """
    buff = _get_buffer(128)
    libsgutils2.sg_get_trans_proto_str(tpi, 128, ctypes.byref(buff))
    return buff.value.decode('utf-8')


@_impl_check
def sg_decode_transportid_str(leadin, bp, only_one=True):
    """
    Decode TransportID pointed to by 'bp' of length 'bplen'. Place decoded
    string output in 'buff' which is also the return value. Each new line
    is prefixed by 'leadin'. If leadin NULL treat as "".
    """
    if leadin is None:
        leadin_ = None
    else:
        leadin_ = leadin.encode('utf-8')
    buff = _get_buffer(1024)
    bp_ = bytes(bp)
    libsgutils2.sg_decode_transportid_str(leadin_, bp_, len(bp_), only_one, 1024, ctypes.byref(buff))
    return buff.value


@six.python_2_unicode_compatible
class DesignatorType(enum.IntEnum):
    VendorSpecific = 0
    T10VendorIdentification = 1
    EUI64Based = 2
    NAA = 3
    RelativeTargetPort = 4
    TargetPortGroup = 5
    LogicalUnitGroup = 6
    MD5LogicalUnitIdentifier = 7
    SCSINameString = 8
    ProtocolSpecificPortIdentifier = 9
    UUIDIdentifier = 10

    def __str__(self):
        return sg_get_desig_type_str(self)


@_impl_check
def sg_get_desig_type_str(val):
    """
    Returns a designator's type string given 'val' (0 to 15 inclusive),
    otherwise returns NULL.
    """
    ret = libsgutils2.sg_get_desig_type_str(val)
    return None if ret is None else ret.decode('utf-8')


@six.python_2_unicode_compatible
class DesignatorCodeSet(enum.IntEnum):
    Binary = 1
    ASCII = 2
    UTF8 = 3

    def __str__(self):
        return sg_get_desig_code_set_str(self)


@_impl_check
def sg_get_desig_code_set_str(val):
    """
    Returns a designator's code_set string given 'val' (0 to 15 inclusive),
    otherwise returns NULL
    """
    ret = libsgutils2.sg_get_desig_code_set_str(val)
    return None if ret is None else ret.decode('utf-8')


@six.python_2_unicode_compatible
class DesignatorAssociation(enum.IntEnum):
    AddressLogicalUnit = 0
    TargetPort = 1
    TargetDeviceLU = 2

    def __str__(self):
        return sg_get_desig_assoc_str(self)


@_impl_check
def sg_get_desig_assoc_str(val):
    """
    Returns a designator's association string given 'val' (0 to 3 inclusive),
    otherwise returns NULL.
    """
    ret = libsgutils2.sg_get_desig_assoc_str(val)
    return None if ret is None else ret.decode('utf-8')


@_impl_check
def sg_set_warnings_strm(fd):
    if hasattr(fd, 'fileno'):
        fd_ = fd.fileno()
    elif isinstance(fd, six.integer_types):
        fd_ = fd
    else:
        raise ValueError("fd must be an file object or integer")

    try:
        strm = libc.fdopen(fd_, 'w')
    except AttributeError:
        strm = libc._fdopen(fd_, 'w')

    if strm == 0:
        errno = ctypes.get_errno()
        raise OSError(errno, libc.strerror(errno).decode('utf-8'))

    libc.setbuf(strm, None)
    libsgutils2.sg_set_warnings_strm(strm)


@_impl_check
def sg_print_command(command):
    """
    The following "print" functions send ACSII to 'sg_warnings_strm' file
    descriptor (default value is stderr). 'leadin' is string prepended to
    each line printed out, NULL treated as "".
    """
    libsgutils2.sg_print_command(command)


@_impl_check
def sg_print_scsi_status(scsi_status):
    """
    The following "print" functions send ACSII to 'sg_warnings_strm' file
    descriptor (default value is stderr). 'leadin' is string prepended to
    each line printed out, NULL treated as "".
    """
    libsgutils2.sg_print_scsi_status(scsi_status)


@_impl_check
def sg_print_sense(leadin, sense_buffer, raw_info=False):
    """
    'leadin' is string prepended to each line printed out, NULL treated as
    "". N.B. prior to sg3_utils v 1.42 'leadin' was only prepended to the
    first line printed.
    """
    if leadin is None:
        leadin_ = None
    else:
        leadin_ = leadin.encode('utf-8')
    sense_buffer_ = bytes(sense_buffer)
    libsgutils2.sg_print_sense(leadin_, sense_buffer_, len(sense_buffer_), raw_info)


class SGLibErrorCode(enum.IntEnum):
    """
    Utilities can use these exit status values for syntax errors and
    file (device node) problems (e.g. not found or permissions).
    """
    #: command line syntax problem
    SYNTAX_ERROR = 1
    #: device or other file problem
    FILE_ERROR = 2


@six.python_2_unicode_compatible
class SGLibCategory(enum.IntEnum):
    """
    The sg_err_category_sense() function returns one of the following.
    These may be used as exit status values (from a process). Notice that
    some of the lower values correspond to SCSI sense key values.
    """
    #: No errors or other information
    CLEAN = 0

    # Value 1 left unused for utilities to use SG_LIB_SYNTAX_ERROR

    #: sense key, unit stopped? [sk,asc,ascq: 0x2,*,*]
    NOT_READY = 2

    #: medium or hardware error, blank check [sk,asc,ascq: 0x3/0x4/0x8,*,*]
    MEDIUM_HARD = 3

    #: Illegal request (other than invalid opcode) [sk,asc,ascq: 0x5,*,*]
    ILLEGAL_REQ = 5

    #: sense key, device state changed [sk,asc,ascq: 0x6,*,*]
    #: was SG_LIB_CAT_MEDIA_CHANGED earlier [sk,asc,ascq: 0x6,0x28,*]
    UNIT_ATTENTION = 6

    #: sense key, media write protected? [sk,asc,ascq: 0x7,*,*]
    DATA_PROTECT = 7

    #: (Illegal request,) Invalid opcode: [sk,asc,ascq: 0x5,0x20,0x0]
    INVALID_OP = 9

    #: sense key, some data transferred [sk,asc,ascq: 0xa,*,*]
    COPY_ABORTED = 10

    #: interpreted from sense buffer [sk,asc,ascq: 0xb,! 0x10,*]
    ABORTED_COMMAND = 11

    #: sense key, probably verify [sk,asc,ascq: 0xe,*,*]
    MISCOMPARE = 14

    #: sense data with key of "no sense" [sk,asc,ascq: 0x0,*,*]
    NO_SENSE = 20

    #: Successful command after recovered err [sk,asc,ascq: 0x1,*,*]
    RECOVERED = 21

    #: 24: this is a SCSI status, not sense.
    #: It indicates reservation by another machine blocks this command
    RES_CONFLICT = SCSIStatusCode.RESERVATION_CONFLICT

    #: SCSI status, not sense key.
    #: Only from PRE-FETCH (SBC-4)
    CONDITION_MET = 25

    #: SCSI status, not sense. Invites retry
    BUSY = 26

    #: SCSI status, not sense. Wait then retry
    TS_FULL = 27

    #: SCSI status; ACA seldom used
    ACA_ACTIVE = 28

    #: SCSI status, this command aborted by?
    TASK_ABORTED = 29

    #: subset of aborted command (for PI, DIF) [sk,asc,ascq: 0xb,0x10,*]
    PROTECTION = 40

    #: Response to SCSI command malformed
    MALFORMED = 97

    #: Something else is in the sense buffer
    SENSE = 98

    #: Some other error/warning has occurred  (e.g. a transport or driver error)
    OTHER = 99

    # Here are some additional sense data categories that are not returned
    # by sg_err_category_sense() but are returned by some related functions.

    #: Illegal request (other than invalid opcode) plus 'info' field: [sk,asc,ascq: 0x5,*,*]
    ILLEGAL_REQ_WITH_INFO = 17

    #: medium or hardware error sense key plus 'info' field: [sk,asc,ascq: 0x3/0x4,*,*]
    MEDIUM_HARD_WITH_INFO = 18

    #: aborted command sense key, protection plus 'info' field: [sk,asc,ascq: 0xb,0x10,*]
    PROTECTION_WITH_INFO = 41

    TIMEOUT = 33

    def __str__(self):
        return sg_get_category_sense_str(self)


@_impl_check
def sg_err_category_sense(sense_buffer):
    """
    Returns a SG_LIB_CAT_* value. If cannot decode sense_buffer or a less
    common sense key then return SG_LIB_CAT_SENSE
    """
    sense_buffer_ = bytes(sense_buffer)
    sb_len = len(sense_buffer_)

    return SGLibCategory(libsgutils2.sg_err_category_sense(sense_buffer_, sb_len))


@_impl_check
def sg_get_category_sense_str(sense_cat, verbose=False):
    """
     Yield string associated with sense category. Returns 'buff' (or pointer
    to "Bad sense category" if 'buff' is NULL). If sense_cat unknown then
    yield "Sense category: <sense_cat>" string.
    """
    buff = _get_buffer(80)
    libsgutils2.sg_get_category_sense_str(sense_cat, 80, ctypes.byref(buff), verbose)
    return buff.value.decode('utf-8')


@_impl_check
def sg_vpd_dev_id_iter(initial_desig_desc, m_assoc=None, m_desig_type=None, m_codeset=None):
    """
    Iterates to next designation descriptor in the device identification
    VPD page. The 'initial_desig_desc' should point to start of first
    descriptor with 'page_len' being the number of valid bytes in that
    and following descriptors. To start, 'off' should point to a negative
    value, thereafter it should point to the value yielded by the previous
    call. If 0 returned then 'initial_desig_desc + *off' should be a valid
    descriptor; returns -1 if normal end condition and -2 for an abnormal
    termination. Matches association, designator_type and/or code_set when
    any of those values are greater than or equal to zero.
    """
    if m_assoc is None:
        m_assoc = -1
    if m_desig_type is None:
        m_desig_type = -1
    if m_codeset is None:
        m_codeset = -1

    offset = ctypes.c_int()
    offset.value = -1

    initial_desig_desc_ = bytes(initial_desig_desc)
    page_len = len(initial_desig_desc_)
    ret = libsgutils2.sg_vpd_id_iter(initial_desig_desc_, page_len, ctypes.byref(offset),
                                     m_assoc, m_desig_type, m_codeset)
    while ret == 0:
        i_len = initial_desig_desc_[offset.value + 3]
        yield initial_desig_desc_[offset.value:(offset.value + i_len)]
        ret = libsgutils2.sg_vpd_id_iter(initial_desig_desc_, page_len, ctypes.byref(offset),
                                         m_assoc, m_desig_type, m_codeset)
        if ret == -2:
            raise ValueError("Abnormal termination")

# <<< General purpose (i.e. not SCSI specific) utility functions >>>


@_impl_check
def safe_strerror(errnum):
    """
    Always returns valid string even if errnum is wild (or library problem).
    If errnum is negative, flip its sign.
    """

    return libsgutils2.safe_strerror(errnum).decode('utf-8')


class StrHexFormat(enum.IntEnum):
    NoAscii = 1
    WithAscii = 0
    HexOnly = -1
    Hdparm = -2


@_impl_check
def dStrHex(str, no_ascii=StrHexFormat.WithAscii):
    """
    Print (to stdout) 'str' of bytes in hex, 16 bytes per line optionally
    followed at the right hand side of the line with an ASCII interpretation.
    Each line is prefixed with an address, starting at 0 for str[0]..str[15].
    All output numbers are in hex. 'no_ascii' allows for 3 output types:
        > 0     each line has address then up to 16 ASCII-hex bytes
        = 0     in addition, the bytes are listed in ASCII to the right
        < 0     only the ASCII-hex bytes are listed (i.e. without address)
    """
    str_ = bytes(str)
    libsgutils2.dStrHex(str_, len(str_), no_ascii)


@_impl_check
def dStrHexErr(str, no_ascii=StrHexFormat.WithAscii):
    """
    Print (to sg_warnings_strm (stderr)) 'str' of bytes in hex, 16 bytes per
    line optionally followed at right by its ASCII interpretation. Same
    logic as dStrHex() with different output stream (i.e. stderr).
    """
    str_ = bytes(str)
    libsgutils2.dStrHexErr(str_, len(str_), no_ascii)


@_impl_check
def dStrHexStr(str, leadin=None, format=StrHexFormat.WithAscii):
    """
    Read 'len' bytes from 'str' and output as ASCII-Hex bytes (space
    separated) to 'b' not to exceed 'b_len' characters. Each line
    starts with 'leadin' (NULL for no leadin) and there are 16 bytes
    per line with an extra space between the 8th and 9th bytes. 'format'
    is 0 for repeat in printable ASCII ('.' for non printable chars) to
    right of each line; 1 don't (so just output ASCII hex). Returns
    number of bytes written to 'b' excluding the trailing '\0'
    """
    str_ = bytes(str)
    buff = _get_buffer(len(str_) * 10)
    if leadin is None:
        leadin_ = None
    else:
        leadin_ = leadin.encode('utf-8')
    b_len = libsgutils2.dStrHexStr(str_, bytes(str_), leadin_, format, len(str_) * 10, ctypes.byref(buff))
    return buff.value[:b_len]


@_impl_check
def sg_is_big_endian():
    """
    Returns 1 when executed on big endian machine; else returns 0.
    Useful for displaying ATA identify words (which need swapping on a
    big endian machine).
    """
    return libsgutils2.sg_is_big_endian()


@_impl_check
def sg_ata_get_chars(word_arr, is_big_endian=None):
    """
    Extract character sequence from ATA words as in the model string
    in a IDENTIFY DEVICE response. Returns number of characters
    written to 'ochars' before 0 character is found or 'num' words
    are processed.
    """
    if is_big_endian is None:
        is_big_endian = sg_is_big_endian()
    word_arr_ = struct.pack("{}H".format(len(word_arr)), *word_arr)

    buff = _get_buffer(len(word_arr_))
    ret = libsgutils2.sg_ata_get_chars(word_arr_, 0, len(word_arr), is_big_endian, ctypes.byref(buff))

    return buff[:ret].decode('utf-8')


@_impl_check
def dWordHex(words, no_ascii=StrHexFormat.WithAscii, swapb=None):
    """
    Print (to stdout) 16 bit 'words' in hex, 8 words per line optionally
    followed at the right hand side of the line with an ASCII interpretation
    (pairs of ASCII characters in big endian order (upper first)).
    Each line is prefixed with an address, starting at 0.
    All output numbers are in hex. 'no_ascii' allows for 3 output types:
        > 0     each line has address then up to 8 ASCII-hex words
        = 0     in addition, the words are listed in ASCII pairs to the right
        = -1    only the ASCII-hex words are listed (i.e. without address)
        = -2    only the ASCII-hex words, formatted for "hdparm --Istdin"
        < -2    same as -1
    If 'swapb' non-zero then bytes in each word swapped. Needs to be set
    for ATA IDENTIFY DEVICE response on big-endian machines.
    """
    words_ = struct.pack("{}H".format(len(words)), *words)

    if swapb is None:
        swapb = sg_is_big_endian()
    libsgutils2.dWordHex(words_, len(words), no_ascii, swapb)


@_impl_check
def sg_get_num(buf):
    return libsgutils2.sg_get_num(buf.encode('utf-8'))


@_impl_check
def sg_get_num_nomult(buf):
    return libsgutils2.sg_get_num_nomult(buf.encode('utf-8'))


@_impl_check
def sg_get_llnum(buf):
    return libsgutils2.sg_get_llnum(buf.encode('utf-8'))


@_impl_check
def sg_set_text_mode(fd):
    if hasattr(fd, 'fileno'):
        fd_ = fd.fileno()
    elif isinstance(fd, six.integer_types):
        fd_ = fd
    else:
        raise ValueError("fd must be an file object or integer")

    ret = libsgutils2.sg_set_text_mode(fd_)
    if ret < 0:
        err_no = -ret
        raise OSError(err_no, libc.strerror(err_no).decode('utf-8'))


@_impl_check
def sg_set_binary_mode(fd):
    if hasattr(fd, 'fileno'):
        fd_ = fd.fileno()
    elif isinstance(fd, six.integer_types):
        fd_ = fd
    else:
        raise ValueError("fd must be an file object or integer")

    ret = libsgutils2.sg_set_binary_mode(fd_)
    if ret < 0:
        err_no = -ret
        raise OSError(err_no, libc.strerror(err_no).decode('utf-8'))
