import argparse
import os

from vfs2.VFS2 import VFS2


def handle_info(vfs: VFS2, verbose: bool = False):
    (dirs, files) = vfs.read_toc()
    for file_id, f in files.items():
        print(f"file: {f.get_full_path()} (id: {file_id})")
        print(f"  offset_start: 0x{f.offset_start:08x}")
        print(f"  file_size: 0x{f.file_size:08x}")
        if verbose:
            print(f"  unknown_1: 0x{f.unknown_1:08x}")
            print(f"  unknown_2: 0x{f.unknown_2:08x}")
            print(f"  unknown_3: 0x{f.unknown_3:08x}")
            print(f"  unknown_4: 0x{f.unknown_4:08x}")
            print(f"  unknown_5: 0x{f.unknown_5:08x}")


def handle_unpack(vfs: VFS2, verbose: bool = None, output: str = None):
    os.makedirs(output, exist_ok=True)
    (dirs, files) = vfs.read_toc()
    with open(vfs.input_path, "rb") as vfs_file:
        for file_id, f in files.items():
            if verbose:
                print(
                    f"Unpacking File(id={file_id}, size={f.file_size}, "
                    f"path={f.get_full_path()}..."
                )
            vfs_file.seek(f.offset_start, os.SEEK_SET)
            data = vfs_file.read(f.file_size)

            out_path = os.path.join(output, f.get_full_path())
            out_dir = os.path.dirname(out_path)
            os.makedirs(out_dir, exist_ok=True)
            with open(out_path, "wb") as out_file:
                out_file.write(data)


def main():
    parser = argparse.ArgumentParser(description="VFS2 Info")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")
    parser_info = subparsers.add_parser("info", help="Display information")
    parser_unpack = subparsers.add_parser("unpack", help="Unpack the file")
    parser_unpack.add_argument("-o", "--output", type=str, help="Output directory")

    # TODO: pack not implemented
    # parser_pack = subparsers.add_parser("pack", help="Pack the file")

    parser.add_argument("input", type=str, help="Input file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output", default=False
    )

    args = parser.parse_args()
    vfs = VFS2(args.input)

    match args.command:
        case "info":
            handle_info(vfs, args.verbose)
        case "unpack":
            handle_unpack(vfs, verbose=args.verbose, output=args.output)
        case "pack":
            raise NotImplementedError("'pack' command not implemented")


if __name__ == "__main__":
    main()
