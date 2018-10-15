import os
import argparse

SIGNATURES = {
    'jpeg': (b'\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46', b'\xFF\xD9'),
    'png': (b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', b'\x49\x45\x4E\x44\xAE\x42\x60\x82'),
    'docx': (b'\x50\x4B\x03\x04\x14\x00\x06\x00', b'\x50\x4B\x05\x06'),
    'pdf': (b'\x25\x50\x44\x46', b'\x45\x4F\x46\x0A'),
    'html': (b'\x3C\x68\x74\x6D\x6C\x3E', b'\x3C\x2F\x68\x74\x6D\x6C\x3E')
}


class FileFinder(object):
    def __init__(self, signature: tuple, file_extension: str):
        """
        Class for find files by signatures
        :param signature:
        :param file_extension:
        """
        self._start_signature = signature[0]
        self._end_signature = signature[1]
        self._file_extension = file_extension
        self._current_buffer = b''
        self._previous_buffer = b''
        self._result_buffer = b''
        self._file_buffer = b''
        self._is_reading = False
        self._index = 0

    def process_data(self, bytes):
        """
        Process input bytes
        :param bytes:
        :return:
        """
        self._previous_buffer = self._current_buffer
        self._current_buffer = bytes
        self._result_buffer = self._previous_buffer + self._current_buffer
        if self._is_reading and self._is_signature_end():
            self._file_buffer += self._result_buffer[:self._get_signature_end_offset()]
            self._save_file()
            self._is_reading = False
            self._file_buffer = b''
        elif self._is_signature_start():
            self._file_buffer = self._result_buffer[self._get_signature_start_offset():]
            self._is_reading = True
            self._current_buffer = b''
        elif self._is_reading:
            self._file_buffer += self._previous_buffer
        if len(self._file_buffer) > 20000000:
            self._file_buffer = b''
            self._is_reading = False

    def print_result(self):
        print(f"Found {self._index} files {self._file_extension}                                 ")

    def _is_signature_start(self):
        if self._start_signature in self._result_buffer:
            return True
        else:
            return False

    def _get_signature_start_offset(self):
        return self._result_buffer.index(self._start_signature)

    def _is_signature_end(self):
        if self._end_signature in self._result_buffer:
            return True
        else:
            return False

    def _get_signature_end_offset(self):
        return self._result_buffer.index(self._end_signature) + len(self._end_signature)

    def _save_file(self):
        if not os.path.exists(f"{self._file_extension}"):
            os.makedirs(f"{self._file_extension}")
        with open(f"{self._file_extension}/{self._index}.{self._file_extension}", 'wb') as file:
            file.write(self._file_buffer)
            self._index += 1
            print(f"Found {self._index} files {self._file_extension}                                 "
                  f"    ", end='\r')
            self._is_reading = False


def main(path, extension):
    file_finder = FileFinder(SIGNATURES[extension], extension)
    data = 1
    print(f"Finding {extension} files ... Это может занять некоторое время", end='\r')
    with open(f"{path}", 'rb') as file:
        while data:
            data = file.read(100)
            file_finder.process_data(data)
        file_finder.print_result()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Search files by known signatures from binary data "
                                                 "For search new signatures, u have to add it to SIGNATURES dictionary ", add_help=True)
    parser.add_argument('-p', '--path', help="Path to binary file", required=False)
    parser.add_argument('-e', '--extension', help="Searching extension", required=False)
    args = parser.parse_args()
    try:
        if not args.path or not args.extension:
            parser.print_help()
        elif args.extension not in SIGNATURES:
            print(f"Set unavailable extension '{args.extension}'. List of known extensions:")
            for key, value in SIGNATURES.items():
                print(f"- {key}")
            parser.print_help()
        else:
            main(args.path, args.extension)
    except KeyboardInterrupt:
        exit(1)
