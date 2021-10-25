import os
import heapq
from io import BytesIO
from hashlib import md5
from aes import AESCipher
from huffman_tree import Node
from collections import Counter


def compress_folder(folder: str, password=None) -> None:
    data = bytearray()
    huffman = Huffman()
    for root, dirs, files in os.walk(folder):
        for f in files:
            data += huffman.compress(os.path.join(root, f), False, password)
    huffman.write_to_file(folder.removesuffix('\\') + '.huf', data)


def get_listing(filename: str) -> list:
    files = []
    with open(filename, 'rb') as f:
        while byte := f.read(1):
            len_filename = int.from_bytes(byte, "big")
            files.append(f.read(len_filename).decode('utf-8'))
            f.read(4)
            real_len = 0
            for i in f.read(4):
                real_len <<= 8
                real_len += int(i)
            f.read(256 + 32 + real_len)
    return files


class Huffman:

    __slots__ = {"filename", "frequency", "codes", "root"}

    def __init__(self):
        self.filename = ""
        self.frequency = Counter()
        self.codes = {}
        self.root = None

    def compress(self, filename: str, write_to_file=True, password=None) -> None | bytearray:
        self.filename = filename
        data = self._read_bytes()
        hash_data = md5(data).hexdigest()
        self._get_frequency(data)
        self.frequency = Counter({code: self.frequency[code] for code in range(256)})
        self._create_tree()
        compress_data = [self.codes[i] for i in list(data)]
        body = self._get_binary_body_from_string(''.join(compress_data))
        if password is not None:
            cipher = AESCipher(password)
            body = cipher.encrypt(body)
        headers = self._create_headers(len(data), len(body), hash_data)
        if write_to_file:
            self.write_to_file(self.filename + '.huf', headers + body)
        else:
            return headers + body

    @staticmethod
    def write_to_file(filename: str, data: bytearray) -> None:
        folder = os.path.split(filename)[0]
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        with open(filename, 'wb') as binary_file:
            binary_file.write(data)

    def _create_headers(self, length_body: int, real_length: int, hash_data: str) -> bytearray:
        byte_filename = bytearray(self.filename.encode('utf-8'))
        len_filename = bytearray([len(byte_filename)]) + byte_filename

        length_body = self._int_to_bytes(length_body)
        real_length = self._int_to_bytes(real_length)

        frequencies = [0] * 256
        for i in range(256):
            frequencies[i] = self.frequency[i]
        return len_filename + length_body + real_length + bytearray(frequencies) + bytearray(hash_data.encode('utf-8'))

    @staticmethod
    def _get_binary_body_from_string(binary_string: str) -> bytearray:
        leftover_bits = len(binary_string) % 8
        if leftover_bits != 0:
            binary_string += '0' * (8 - leftover_bits)

        return bytearray(int(binary_string[i:i + 8], 2) for i in range(0, len(binary_string), 8))

    def decompress(self, filename: str, password=None) -> None:
        with open(filename, 'rb') as f:
            while byte := f.read(1):
                len_filename = int.from_bytes(byte, "big")
                header_filename = f.read(len_filename)
                length_body = f.read(4)
                real_len = 0
                for i in f.read(4):
                    real_len <<= 8
                    real_len += int(i)

                start_bytes = bytearray([len_filename]) + header_filename + length_body

                bytes_io = BytesIO(start_bytes + f.read(256 + 32 + real_len))
                self.decompress_from_bytes(bytes_io, password)

    def decompress_from_bytes(self, bytes_io: BytesIO, password=None) -> None:
        with bytes_io as f:
            length_body = 0
            symbol = ""
            bit_string = ""
            decoded_str = ""

            header_filename = f.read(int.from_bytes(f.read(1), "big"))

            for i in f.read(4):
                length_body <<= 8
                length_body += int(i)

            self.frequency = Counter({code: count for code, count in enumerate(f.read(256))})
            hash_data = f.read(32).decode('utf-8')
            self._create_tree()
            decodes = {value: key for key, value in self.codes.items()}

            body = f.read()
            if password is not None:
                cipher = AESCipher(password)
                body = cipher.decrypt(body)
                if len(body) == 0:
                    print("Incorrect password")
                    return
            for byte in body:
                bit_string += format(byte, '08b')

            count = 0
            for char in bit_string:
                if count == length_body:
                    break
                symbol += char
                if symbol in decodes:
                    decoded_str += chr(decodes[symbol])
                    symbol = ""
                    count += 1

        if hash_data != md5(decoded_str.encode('utf-8')).hexdigest():
            print("The file is damaged or incorrect password")
            return
        self.write_to_file(header_filename, decoded_str.encode('utf-8'))

    def _normalize_frequencies(self) -> None:
        max_item = self.frequency.most_common()[0][1]
        if max_item <= 255:
            return
        for i in range(256):
            if self.frequency[i] > 0:
                self.frequency[i] = 1 + self.frequency[i] * 255 // (max_item + 1)

    def _get_dict_from_tree(self, node: Node, code="") -> None:
        if node.value is not None:
            self.codes[node.value] = code
        if node.left is not None:
            self._get_dict_from_tree(node.left, code + "0")
        if node.right is not None:
            self._get_dict_from_tree(node.right, code + "1")

    def _create_tree(self) -> Node:
        self._normalize_frequencies()
        h = []
        for value, freq in self.frequency.items():
            h.append(Node(freq, value))
        heapq.heapify(h)

        while len(h) > 1:
            node1 = heapq.heappop(h)
            node2 = heapq.heappop(h)
            new_node = Node(node1.frequency + node2.frequency, None, node1, node2)
            heapq.heappush(h, new_node)

        if h:
            self.root = h[0]
            self._get_dict_from_tree(self.root)
            return
        raise ValueError()

    def _get_frequency(self, data: bytes) -> None:
        for byte in data:
            self.frequency.update({byte: 1})

    def _read_bytes(self) -> bytes:
        with open(self.filename, 'rb') as f:
            return f.read()

    @staticmethod
    def _int_to_bytes(num: int):
        len_bytes = f"{bin(num)[2:]:0>32}"
        return bytearray(int(len_bytes[i:i + 8], 2) for i in range(0, len(len_bytes), 8))
