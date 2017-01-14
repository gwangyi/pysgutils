from typing import Union, List, Optional, Dict
import ctypes
import os
import enum
import weakref

from . import sg_lib, Buffer

class SGPTBase(ctypes.c_void_p):
    ...

def scsi_pt_version() -> str:
    ...

def scsi_pt_open_device(device_name: str, read_only: bool=False, verbose: bool=False) -> int:
    ...

def scsi_pt_open_flags(device_name: str, flags: int=os.O_RDWR, verbose: bool=False) -> int:
    ...

def scsi_pt_close_device(device_fd: int):
    ...

def construct_scsi_pt_obj() -> SGPTBase:
    ...

def clear_scsi_pt_obj(objp: SGPTBase):
    ...

def set_scsi_pt_cdb(objp: SGPTBase, cdb: bytes):
    ...

def set_scsi_pt_sense(objp: SGPTBase, sense: bytes):
    ...

def set_scsi_pt_data_in(objp: SGPTBase, dxferp: ctypes.Array):
    ...

def set_scsi_pt_data_out(objp: SGPTBase, dxferp: Union[bytes, ctypes.Array]):
    ...

def set_scsi_pt_packet_id(objp: SGPTBase, packet_id: int):
    ...

def set_scsi_pt_tag(objp: SGPTBase, tag: int):
    ...

def set_scsi_pt_task_management(objp: SGPTBase, tmf_code: int):
    ...

def set_scsi_pt_task_attr(objp: SGPTBase, attribute: int, priority: int):
    ...

class SCSIPTFlags(enum.IntEnum):
    ...

def set_scsi_pt_flags(objp: SGPTBase, flags: int):
    ...

def do_scsi_pt(objp: SGPTBase, fd: int, timeout_secs: int, verbose: bool=False):
    ...

class SCSIPTResult(enum.IntEnum):
    ...

def get_scsi_pt_result_category(objp: SGPTBase) -> SCSIPTResult:
    ...

def get_scsi_pt_resid(objp: SGPTBase) -> int:
    ...

def get_scsi_pt_status_response(objp: SGPTBase) -> sg_lib.SCSIStatusCode:
    ...

def get_scsi_pt_sense_len(objp: SGPTBase) -> int:
    ...

def get_scsi_pt_os_err(objp: SGPTBase) -> int:
    ...

def get_scsi_pt_os_err_str(objp: SGPTBase) -> str:
    ...

def get_scsi_pt_transport_err(objp: SGPTBase) -> int:
    ...

def get_scsi_pt_transport_err_str(objp: SGPTBase) -> str:
    ...

def get_scsi_pt_duration_ms(objp: SGPTBase) -> int:
    ...

def destruct_scsi_pt_obj(objp: SGPTBase):
    ...

def scsi_pt_win32_direct(objp: SGPTBase, state_direct: bool):
    ...

def scsi_pt_win32_spt_state() -> bool:
    ...

class SCSIPTDevice(object):
    _refs = weakref.WeakValueDictionary()
    _stack = [None]  # type: List[Optional[SCSIPTDevice]]

    def __init__(self, device_name: str, read_only_or_flags: bool=False, verbose: bool=False, *,
                 flags: bool=None, read_only: bool=None):
        self._fd = 0
        self.device_name = device_name

    def close(self) -> None:
        ...

    def enter(self) -> None:
        ...

    def exit(self):
        ...

    @classmethod
    def current(cls) -> Optional['SCSIPTDevice']:
        ...

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...


class SCSIPTObject(object):
    _refs = weakref.WeakValueDictionary()
    timeout = 5

    class TaskAttr(object):
        def __init__(self, pt_obj: SCSIPTObject):
            self._pt_obj = pt_obj
            self._attrs = dict()  # type: Dict[int, int]

        def __getitem__(self, item: int) -> Optional[int]:
            ...

        def __setitem__(self, key: int, value: int):
            ...

    def __init__(self):
        self._pt_obj = ...  # type: SGPTBase
        self._cdb = ...  # type: Optional[sg_lib.SCSICommand]
        self._sense = ...  # type: Optional[sg_lib.SCSISense]
        self._data_in = ...  # type: Optional[Buffer]
        self._data_out = ...  # type: Union[type(None), bytes, Buffer]
        self._packet_id = ...  # type: Optional[int]
        self._tag = ...  # type: Optional[int]
        self._task_management = ...  # type: Optional[int]
        self.task_attr = ...  # type: SCSIPTObject.TaskAttr
        self._flags = ...  # type: SCSIPTFlags
        self._win32_direct = ...  # type: Optional[bool]

    def clear(self) -> None:
        ...

    @property
    def cdb(self) -> Optional[sg_lib.SCSICommand]:
        return self._cdb

    @cdb.setter
    def cdb(self, val: Union[bytes, sg_lib.SCSICommand]):
        ...

    @property
    def sense(self) -> Optional[sg_lib.SCSISense]:
        return self._sense

    @sense.setter
    def sense(self, val: sg_lib.SCSISense):
        ...

    @property
    def data_in(self) -> Optional[Buffer]:
        return self._data_in

    @data_in.setter
    def data_in(self, val: Buffer):
        ...

    @property
    def data_out(self) -> Union[type(None), bytes, Buffer]:
        return self._data_out

    @data_out.setter
    def data_out(self, val: Union[bytes, Buffer]):
        ...

    @property
    def packet_id(self) -> Optional[int]:
        return self._packet_id

    @packet_id.setter
    def packet_id(self, val: int):
        ...

    @property
    def tag(self) -> Optional[int]:
        return self._tag

    @tag.setter
    def tag(self, val: int):
        ...

    @property
    def task_management(self) -> Optional[int]:
        return self._task_management

    @task_management.setter
    def task_management(self, val: int):
        ...

    @property
    def result_category(self) -> SCSIPTResult:
        return get_scsi_pt_result_category(self._pt_obj)

    @property
    def resid(self) -> int:
        return get_scsi_pt_resid(self._pt_obj)

    @property
    def status_response(self) -> sg_lib.SCSIStatusCode:
        return get_scsi_pt_status_response(self._pt_obj)

    @property
    def sense_len(self) -> int:
        return get_scsi_pt_sense_len(self._pt_obj)

    @property
    def os_err(self) -> int:
        return get_scsi_pt_os_err(self._pt_obj)

    @property
    def os_err_str(self) -> str:
        return get_scsi_pt_os_err_str(self._pt_obj)

    @property
    def transport_err(self) -> int:
        return get_scsi_pt_transport_err(self._pt_obj)

    @property
    def transport_err_str(self) -> str:
        return get_scsi_pt_transport_err_str(self._pt_obj)

    @property
    def duration_ms(self) -> int:
        return get_scsi_pt_duration_ms(self._pt_obj)

    @property
    def win32_direct(self) -> Optional[bool]:
        return self._win32_direct

    @win32_direct.setter
    def win32_direct(self, val: bool):
        ...

    def do_scsi_pt(self, timeout: Optional[int]=None, device: Optional[SCSIPTDevice]=None,
                   verbose: bool=False) -> SCSIPTResult:
        ...
