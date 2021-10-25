import os
import sys
from huffman import Huffman, compress_folder, get_listing

HELP_STRING = """
A program for archiving and unzipping files using the Huffman algorithm.
USAGE:
    main.py -c, --compress   [path] (-p password)
    main.py -d, --decompress [path] (-p password)
    main.py -l, --listing    [path]
    main.py -h, --help
"""


def is_path_correct(func):
    def wrapper(path, *args):
        if os.path.exists(path):
            func(path, *args)
        else:
            print("The path is incorrect")
    return wrapper


@is_path_correct
def compress(path: str, password: str = None) -> None:
    if os.path.isfile(path):
        huffman = Huffman()
        huffman.compress(path, password=password)
    else:
        compress_folder(path, password=password)


@is_path_correct
def decompress(path: str, password: str = None) -> None:
    huffman = Huffman()
    huffman.decompress(path, password=password)


@is_path_correct
def print_listing(path: str):
    files = get_listing(path)
    print(*files, sep='\n')


def main():
    arguments = sys.argv
    password = None
    if len(arguments) < 2:
        print("Enter arguments to get started")

    elif arguments[1] == "-h" or arguments[1] == "--help":
        print(HELP_STRING)

    elif arguments[1] == "-c" or arguments[1] == "--compress":
        if len(arguments) < 3:
            print("File path required")
        elif len(arguments) >= 3:
            if len(arguments) >= 5 and (arguments[3] == "-p" or arguments[3] == "--password"):
                password = arguments[4]
            compress(arguments[2], password)

    elif arguments[1] == "-d" or arguments[1] == "--decompress":
        if len(arguments) < 3:
            print("File path required")
        elif len(arguments) >= 3:
            if len(arguments) >= 5 and (arguments[3] == "-p" or arguments[3] == "--password"):
                password = arguments[4]
            decompress(arguments[2], password)

    elif arguments[1] == "-l" or arguments[1] == "--listing":
        if len(arguments) < 3:
            print("File path required")
        elif len(arguments) == 3:
            print_listing(arguments[2])

    else:
        print("Something went wrong")


if __name__ == "__main__":
    main()
