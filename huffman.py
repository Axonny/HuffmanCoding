import heapq
from collections import Counter
from huffman_tree import Node


class Huffman:

    __slots__ = {"filename", "frequency", "codes", "root"}

    def __init__(self):
        self.filename = ""
        self.frequency = Counter()
        self.codes = {}
        self.root = None

    def compress(self, filename: str) -> None:
        self.filename = filename
        self._get_frequency(self._read_bytes())
        self.frequency = Counter({code: self.frequency[code] for code in range(256)})
        self._create_tree()
        data = list(self._read_bytes())
        compress_data = [self.codes[i] for i in data]
        headers = self._create_headers(len(data))
        body = self._get_binary_body_from_string(''.join(compress_data))
        self._write_to_file(self.filename + '.huf', headers + body)

    @staticmethod
    def _write_to_file(filename: str, data: bytearray) -> None:
        with open(filename, 'wb') as binary_file:
            binary_file.write(data)

    def _create_headers(self, length_body: int) -> bytearray:
        len_bytes = f"{bin(length_body)[2:]:0>32}"
        length_body = bytearray(int(len_bytes[i:i + 8], 2) for i in range(0, len(len_bytes), 8))

        frequencies = [0] * 256
        for i in range(256):
            frequencies[i] = self.frequency[i]
        return length_body + bytearray(frequencies)

    @staticmethod
    def _get_binary_body_from_string(binary_string: str) -> bytearray:
        leftover_bits = len(binary_string) % 8
        if leftover_bits != 0:
            binary_string += '0' * (8 - leftover_bits)

        return bytearray(int(binary_string[i:i + 8], 2) for i in range(0, len(binary_string), 8))

    def decompress(self, filename: str) -> None:
        with open(filename, 'rb') as f:
            length_body = 0
            symbol = ""
            bit_string = ""
            decoded_str = ""

            for i in f.read(4):
                length_body <<= 8
                length_body += int(i)
            self.frequency = Counter({code: count for code, count in enumerate(f.read(256))})
            self._create_tree()
            decodes = {value: key for key, value in self.codes.items()}

            for byte in f.read(length_body):
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

        self._write_to_file(filename.removesuffix('.huf'), decoded_str.encode('utf-8'))

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
