import unittest

from naive import compiler

class CompilerTestCase(unittest.TestCase):
    def setUp(self):
        self.c = compiler.Compiler('Hello, {{person.first_name}}, how are you?')
    def tearDown(self):
        pass

    def test_tokenize(self):
        wanted = ['Hello, ', compiler.NameToken('person.first_name'), ', how are you?']
        self.assertListEqual(self.c.tokenize(), wanted)

    def test_name_token(self):
        co = compiler.Compiler('Hello, {{name}}!').compile()
        self.assertEqual(eval(co, {'name': 'Asaka'}), 'Hello, Asaka!')

    def test_strip_name_token(self):
        co = compiler.Compiler('Hello, {{ name }}!').compile()
        self.assertEqual(eval(co, {'name': 'Asaka'}), 'Hello, Asaka!')
        co = compiler.Compiler('Hello, {{name }}!').compile()
        self.assertEqual(eval(co, {'name': 'Asaka'}), 'Hello, Asaka!')
        co = compiler.Compiler('Hello, {{ name}}!').compile()
        self.assertEqual(eval(co, {'name': 'Asaka'}), 'Hello, Asaka!')

    def test_dot_access_name_token(self):
        wanted = 'Hello, Jim, how are you?'
        person = {'first_name': 'Jim', 'last_name': 'Green'}
        ret = eval(self.c.compile(), {'person': person})
        self.assertEqual(wanted, ret)
