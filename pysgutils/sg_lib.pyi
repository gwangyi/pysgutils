from typing import Union, Optional, Tuple, List, Iterable
from . import Buffer, AlignedBuffer
import enum

class PeripheralDeviceTypes(enum.IntEnum):
    @property
    def decay(self) -> 'PeripheralDeviceTypes':
        return self

class SCSIStatusCode(enum.IntEnum):
    ...

class SCSISenseKeyCode(enum.IntEnum):
    ...

class TransportProtocol(enum.IntEnum):
    ...

def sg_lib_version() -> str:
    ...

def sg_get_command_size(cdb_byte0: Union[int, bytes]) -> int:
    ...

def sg_get_command_name(cdb: Union[bytes, Buffer], peri_type: PeripheralDeviceTypes) -> str:
    ...

def sg_get_opcode_name(cdb_byte0: Union[int, bytes, Buffer], peri_type: PeripheralDeviceTypes) -> str:
    ...

def sg_get_opcode_sa_name(cdb_byte0: Union[int, bytes, Buffer], service_action: int, peri_type: PeripheralDeviceTypes) -> str:
    ...

def sg_get_scsi_status_str(scsi_status: SCSIStatusCode) -> str:
    ...

class SCSISenseHdr:
    def __init__(self, response_code: int, sense_key: int, asc: int, ascq: int,
                 byte4: int, byte5: int, byte6: int, additional_length: int):
        self.response_code = response_code  # permit: 0x0, 0x70, 0x71, 0x72, 0x73
        self.sense_key = sense_key
        self.asc = asc
        self.ascq = ascq
        self.byte4 = byte4
        self.byte5 = byte5
        self.byte6 = byte6
        self.additional_length = additional_length

    @staticmethod
    def from_sense(sense: Union[bytes, Buffer]) -> 'SCSISenseHdr':
        ...


def sg_scsi_normalize_sense(sense: bytes) -> SCSISenseHdr:
    ...

def sg_scsi_sense_desc_find(sense: Union[bytes, Buffer], desc_type: int) -> bytes:
    ...

def sg_get_sense_key(sense: Union[bytes, Buffer]) -> Union[SCSISenseKeyCode, int]:
    ...

def sg_get_sense_key_str(sense_key: SCSISenseKeyCode) -> str:
    ...

def sg_get_asc_ascq_str(asc: int, ascq: int) -> str:
    ...

def sg_get_sense_info_fld(sense: Union[bytes, Buffer]) -> Tuple[bool, int]:
    ...

def sg_get_sense_filemark_eom_ili(sense: Union[bytes, Buffer]) -> Tuple[bool, bool, bool, bool]:
    ...

def sg_get_sense_progress_fld(sense: Union[bytes, Buffer]) -> Tuple[bool, int]:
    ...

def sg_get_sense_str(leadin: Optional[str], sense: Union[bytes, Buffer], raw_sinfo: bool) -> str:
    ...

def sg_get_sense_descriptors_str(leadin: Optional[str], sense: Union[bytes, Buffer]) -> str:
    ...

def sg_get_designation_descriptor_str(leadin: Optional[str], ddp: bytes,
                                      print_assoc: bool=False, do_long: bool=False) -> str:
    ...

def sg_get_pdt_str(pdt: PeripheralDeviceTypes) -> str:
    ...

def sg_lib_pdt_decay(pdt: PeripheralDeviceTypes) -> PeripheralDeviceTypes:
    ...

def sg_get_trans_proto_str(tpi: TransportProtocol) -> str:
    ...

def sg_decode_transportid_str(leadin: Optional[str], bp: bytes, only_one: bool=True) -> str:
    ...

class DesignatorType(enum.IntEnum):
    ...

def sg_get_desig_type_str(val: DesignatorType) -> str:
    ...

class DesignatorCodeSet(enum.IntEnum):
    ...

def sg_get_desig_code_set_str(val: DesignatorCodeSet) -> str:
    ...

class DesignatorAssociation(enum.IntEnum):
    ...

def sg_get_desig_assoc_str(val: DesignatorAssociation) -> str:
    ...

def sg_set_warnings_strm(fd):
    ...

def sg_print_command(command: bytes):
    ...

def sg_print_scsi_status(scsi_status: int):
    ...

def sg_print_sense(leadin: Optional[str], sense_buffer: bytes, raw_info: bool=False):
    ...

class SGLibErrorCode(enum.IntEnum):
    ...

class SGLibCategory(enum.IntEnum):
    ...

def sg_err_category_sense(sense_buffer: Union[bytes, Buffer]) -> SGLibCategory:
    ...

def sg_get_category_sense_str(sense_cat: SGLibCategory, verbose: bool=False) -> str:
    ...

def sg_vpd_dev_id_iter(initial_desig_desc: bytes, m_assoc: Optional[DesignatorAssociation]=None,
                       m_desig_type:Optional[DesignatorType]=None,
                       m_codeset:Optional[DesignatorCodeSet]=None) -> Iterable[bytes]:
    ...

def safe_strerror(errnum: int) -> str:
    ...

class StrHexFormat(enum.IntEnum):
    ...

def dStrHex(str: bytes, no_ascii: StrHexFormat=StrHexFormat.WithAscii):
    ...

def dStrHexErr(str: bytes, no_ascii: StrHexFormat=StrHexFormat.WithAscii):
    ...

def dStrHexStr(str: bytes, leadin: Optional[str]=None, format:StrHexFormat=StrHexFormat.WithAscii):
    ...

def sg_is_big_endian() -> bool:
    ...

def sg_ata_get_chars(word_arr: Optional[bytes, List[int]], start_word: int=0, num_words: Optional[int]=None,
                     is_big_endian=None) -> bytes:
    ...

def dWordHex(words: List[int], no_ascii: StrHexFormat=StrHexFormat.WithAscii, swapb: Optional[bool]=None):
    ...

def sg_get_num(buf: str) -> int:
    ...

def sg_get_num_nomult(buf: str) -> int:
    ...

def sg_get_llnum(buf: str) -> int:
    ...

def sg_set_text_mode(fd):
    ...

def sg_set_binary_mode(fd):
    ...

class SCSICommand(AlignedBuffer):
    alignment = 64

    def __init__(self, seq: Union[bytes, Iterable[int]], peri_type: PeripheralDeviceTypes=PeripheralDeviceTypes.DISK,
                 service_action: Optional[int]=None):
        super().__init__(seq)
        self.service_action = service_action

    @property
    def size(self) -> int:
        return 0

    @property
    def name(self) -> str:
        return ''

    @property
    def opcode_name(self) -> str:
        return ''

    @property
    def opcode_sa_name(self) -> str:
        return ''

    @property
    def peri_type(self) -> PeripheralDeviceTypes:
        return PeripheralDeviceTypes.DISK

    @peri_type.setter
    def peri_type(self, val: PeripheralDeviceTypes):
        ...


class SCSISense(AlignedBuffer):
    alignment = 64

    def __init__(self, init, size=None):
        super(SCSISense, self).__init__(init, size)
        self.header = SCSISenseHdr.from_sense(self)
        self._dirty = False

    def find_desc(self, desc_type: int) -> bytes:
        ...

    def update_header(self) -> None:
        ...

    @property
    def sense_key(self) -> SCSISenseKeyCode:
        return SCSISenseKeyCode.NO_SENSE_CODE

    @property
    def asc_ascq_str(self) -> str:
        return ''

    @property
    def info(self) -> Optional[int]:
        return None

    @property
    def filemark_eom_ili(self) -> Tuple[bool, bool, bool, bool]:
        return False, False, False, False

    @property
    def filemark(self) -> bool:
        return False

    @property
    def eom(self) -> bool:
        return False

    @property
    def ili(self) -> bool:
        return False

    @property
    def progress(self) -> Optional[int]:
        return None

    @property
    def descriptors(self) -> str:
        return ''

    @property
    def err_category(self) -> SGLibCategory:
        return SGLibCategory.CLEAN