from unittest.mock import Mock


class MockFile(Mock):
    def __init__(self):
        super().__init__()
        self.file = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self):
        return 'test'

    def write(self, content):
        self.file += content

    def __str__(self):
        return self.file
