import unittest
from dis import dis

from naive import compiler

class CompilerTestCase(unittest.TestCase):
    def setUp(self):
        pass
        #self.c = compiler.Compiler('Hello, {{person.first_name}}, how are you?')
    def tearDown(self):
        pass

    def test_tokenize(self):
        c = compiler.Compiler('Hello, {{person.first_name}}, how are you?')
        wanted = ['Hello, ', compiler.NameToken('person.first_name'), ', how are you?']
        self.assertListEqual(c.tokenize(), wanted)
        c = compiler.Compiler('Hello, {% if a %}, how are you?{% endif %}')
        wanted = ['Hello, ', compiler.ExprToken('if a'), ', how are you?', compiler.ExprToken('endif')]
        self.assertListEqual(c.tokenize(), wanted)

    def test_expr_token(self):
        c = compiler.Compiler('Hi!, {%if True%}True{%endif%}')
        tokens = c.tokenize()
        self.assertEqual(type(tokens[1]), compiler.IfToken)
        self.assertEqual(type(tokens[3]), compiler.EndIfToken)

    def test_codes_length(self):
        c = compiler.Compiler('Hi!, {{name}}!')
        self.assertEqual(len(c.codes), c.codes_length)

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
        co = compiler.Compiler('Hello, {{person.first_name}}, how are you?').compile()
        ret = eval(co, {'person': person})
        self.assertEqual(wanted, ret)

    #def test_simple_if_expr(self):
    #    c = compiler.Compiler('Hey,{%if fact%}it\'s true!{%endif%}oh!')
    #    co = c.compile()
    #    self.assertEqual(eval(co, {'fact': True}), 'Hey,it\'s true!oh!')
    #    self.assertEqual(eval(co, {'fact': False}), 'Hey,oh!')

    #def test_elif_expr(self):
    #    co = compiler.Compiler('{%if a%}a{%elif b%}b{%endif%}').compile()
    #    self.assertEqual(eval(co, {'a': 1, 'b': 1}), 'a')
    #    self.assertEqual(eval(co, {'a': 0, 'b': 1}), 'b')
    #    self.assertEqual(eval(co, {'a': 0, 'b': 0}), '')
    #    co = compiler.Compiler('{%if a%}a{%elif b%}b{%elif c%}c{%endif%}').compile()
    #    self.assertEqual(eval(co, {'a': 1, 'b': 1}), 'a')
    #    self.assertEqual(eval(co, {'a': 0, 'b': 1}), 'b')
    #    self.assertEqual(eval(co, {'a': 0, 'b': 0, 'c': 1}), 'c')
    #    self.assertEqual(eval(co, {'a': 0, 'b': 0, 'c': 0}), '')

    def test_else_expr(self):
        co = compiler.Compiler('{%if a%}a{%else%}b{%endif%}').compile()
        self.assertEqual(eval(co, {'a': 1}), 'a')
        self.assertEqual(eval(co, {'a': 0}), 'b')