import unittest

from naive import compiler

class CompilerTestCase(unittest.TestCase):
    def setUp(self):
        self.c = compiler.Compiler('Hello, {{name}}, how are you?')
    def tearDown(self):
        pass

    def test_tokenize(self):
        wanted = ['Hello, ', compiler.NameToken('name'), ', how are you?']
        self.assertListEqual(self.c.tokenize(), wanted)

    def test_name_token(self):
        print eval(self.c.compile())
