import os
import random
import shutil
import unittest
from hashlib import md5
from huffman import Huffman


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        path = 'tests'
        if not os.path.exists(path):
            os.mkdir(path)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree('tests')

    def test_1a(self):
        self._create_file_with_data('1a.txt', 'a')
        self._huffman_test('1a.txt')

    def test_10a(self):
        self._create_file_with_data('10a.txt', 'a' * 10)
        self._huffman_test('10a.txt')

    def test_1000a(self):
        self._create_file_with_data('1000a.txt', 'a' * 1000)
        self._huffman_test('1000a.txt')

    def test_compress_really(self):
        self._create_file_with_data('comp.txt', 'a' * 100000)
        self._huffman_test('comp.txt')
        uncompress = os.path.getsize(self._test_path('comp.txt'))
        compress = os.path.getsize(self._test_path('comp.txt.huf'))
        self.assertTrue(compress * 1.1 < uncompress)

    def test_password(self):
        name = 'password.txt'
        self._create_file_with_data(name, 'a' * 1000)
        Huffman().compress(self._test_path(name), password='abcd')
        os.rename(self._test_path(name), self._test_path("copy_" + name))
        Huffman().decompress(self._test_path(f'{name}.huf'), password='incorrect password')
        self.assertFalse(os.path.exists(self._test_path(name)))
        Huffman().decompress(self._test_path(f'{name}.huf'), password='abcd')
        self._is_correct_decompress(self._test_path(name), self._test_path("copy_" + name))

    def test_100_random(self):
        for _ in range(100):
            self._random_test()

    def _random_test(self):
        alphabet = "qwertyuioplkjhgfdsazxcvbnm1234567890"
        data = ''.join(random.choices(alphabet, k=1000))
        name = ''.join(random.choices(alphabet, k=16)) + '.txt'
        with open(self._test_path(name), 'w', encoding='utf-8') as f:
            f.write(data)
        self._huffman_test(name)

    def _huffman_test(self, name: str):
        Huffman().compress(self._test_path(name))
        os.rename(self._test_path(name), self._test_path("copy_" + name))
        Huffman().decompress(self._test_path(f'{name}.huf'))
        self._is_correct_decompress(self._test_path(name), self._test_path("copy_" + name))

    def _create_file_with_data(self, filename: str, data: str):
        with open(self._test_path(filename), 'w', encoding='utf-8') as f:
            f.write(data)

    def _is_correct_decompress(self, start_filename: str, end_filename: str):
        with open(start_filename, 'rb') as sf, open(end_filename, 'rb') as ef:
            self.assertTrue(sf.read() == ef.read())

    @staticmethod
    def _test_path(path):
        return os.path.join('tests', path)


if __name__ == '__main__':
    unittest.main()
