import struct
from typing import Dict, BinaryIO, List

VirtualDirDict = Dict[int, "VirtualDir"]
VirtualFileDict = Dict[int, "VirtualFile"]


def null_terminated(input: bytes) -> str:
    match input.index(b"\0"):
        case -1:
            return input.decode("utf-8")
        case i:
            return input[:i].decode("utf-8")


class VirtualDir:
    _dirs: VirtualDirDict
    parent: int
    name: str  # max 0x80 bytes

    def __init__(self, dirs: VirtualDirDict):
        self._dirs = dirs

    @staticmethod
    def from_file(f: BinaryIO, dirs: VirtualDirDict):
        vd = VirtualDir(dirs)
        (vd.parent,) = struct.unpack("<I", f.read(4))
        vd.name = null_terminated(f.read(0x80))
        return vd

    def get_full_path(self) -> str:
        parts: List[str] = []
        node = self
        while True:
            parts.append(node.name)
            if node.parent == 0 or node.parent not in self._dirs:
                break
            node = self._dirs[node.parent]
        return "/".join(reversed(parts))


class VirtualFile:
    _dirs: VirtualDirDict
    _files: VirtualFileDict
    parent: int  # 0x00
    name: str  # 0x04: max 0x80 bytes
    offset_start: int  # 0x84
    file_size: int  # 0x88
    unknown_1: int  # 0x8C
    unknown_2: int  # 0x90
    unknown_3: int  # 0x94
    unknown_4: int  # 0x98
    unknown_5: int  # 0x9C

    def __init__(self, dirs: VirtualDirDict, files: VirtualFileDict):
        self._dirs = dirs
        self._files = files

    @staticmethod
    def from_file(f: BinaryIO, dirs: VirtualDirDict, files: VirtualFileDict):
        vf = VirtualFile(dirs, files)
        (vf.parent,) = struct.unpack("<I", f.read(4))
        vf.name = null_terminated(f.read(0x80))
        (
            vf.offset_start,
            vf.file_size,
            vf.unknown_1,
            vf.unknown_2,
            vf.unknown_3,
            vf.unknown_4,
            vf.unknown_5,
        ) = struct.unpack("<IIIIIII", f.read(28))
        return vf

    def get_full_path(self) -> str:
        return self._dirs[self.parent].get_full_path() + "/" + self.name


class VFS2:
    dirs: VirtualDirDict
    files: VirtualFileDict
    input_path: str

    def __init__(self, input_path: str):
        self.input_path = input_path

    def read_toc(self) -> tuple[VirtualDirDict, VirtualFileDict]:
        self.dirs = {}
        self.files = {}
        self.dirs[0] = VirtualDir(self.dirs)
        self.dirs[0].name = "/"

        with open(self.input_path, "rb") as f:
            if f.read(4) != b"VFS2":
                raise ValueError("Not a VFS2 file")
            (dir_count, file_count) = struct.unpack("<II", f.read(8))

            f.read(0x0C)  # skip 0x10 (unknown) bytes

            # print(f"Directories: {dir_count}, Files: {file_count}")

            next_dir_id = 1
            for i in range(dir_count):
                vd = VirtualDir.from_file(f, self.dirs)
                self.dirs[next_dir_id] = vd
                next_dir_id += 1

            next_file_id = 1
            for i in range(file_count):
                vf = VirtualFile.from_file(f, self.dirs, self.files)
                self.files[next_file_id] = vf
                next_file_id += 1

        return (self.dirs, self.files)
