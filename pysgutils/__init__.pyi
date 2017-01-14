from typing import Union, Iterable, Optional
import ctypes


class Buffer(object):
    def __init__(self, init: Union[int, bytes, Iterable[int]], size: Optional[int]=None):
        self._buffer = ...  # type: ctypes.Array
        self._as_parameter_ = ... # type: ctypes.Array

    def resize(self, size: int) -> 'Buffer':
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, item: Union[int, slice]) -> bytes:
        ...

    def __setitem__(self, key: Union[int, slice], value: bytes):
        ...

    def __iter__(self) -> Iterable[bytes]:
        ...

    def __bytes__(self) -> bytes:
        ...


class AlignedBuffer(Buffer):
    alignment = None  # type: Optional[int]

    def __init__(self, init: Union[int, bytes, Iterable[int]], size: Optional[int]=None,
                 alignment: Optional[int]=None):
        super().__init__(init, size)
        ...

    @staticmethod
    def _align(buffer: ctypes.Array, size: int, alignment: int) -> ctypes.Array:
        ...