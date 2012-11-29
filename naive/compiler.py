import re
import types
import opcode
import struct

code = types.CodeType

class Token(str):
    pass

class RawToken(Token):
    '''The raw content in template'''
    pass

class NameToken(Token):
    '''{{name}} '''
    @property
    def names(self):
        return self.split('.')

class ExprToken(Token):
    '''{%syntax%} '''
    @property
    def tokens(self):
        return self.split()
    def __init__(self, s):
        super(str, self).__init__(s)
        if self.tokens[0] == 'if': self.type = 'if'
        elif self.tokens[0] == 'else': self.type = 'else'
        elif self.tokens[0] == 'endif': self.type = 'endif'
        elif self.tokens[0] == 'for': self.type = 'for'
        elif self.tokens[0] == 'endfor': self.type = 'endfor'
        else: raise SyntaxError('Invalid expression')

class Compiler(object):
    def __init__(self, file_or_string):
        self.consts = []
        self.names = []
        self.varnames = []
        self.codes = []
        self.codes_length = 0
        if isinstance(file_or_string, file):
            self.text = file_or_string.read()
        else:
            self.text = file_or_string

    def _make_const(self, value):
        self.consts.append(value)
        return len(self.consts) - 1

    def _make_name(self, value):
        self.names.append(value)
        return len(self.names) - 1

    def _make_varname(self, value):
        self.varnames.append(value)
        return len(self.varnames) - 1

    def __getattr__(self, name):
        if name not in opcode.opmap:
            return self.__getattribute__(name)
        def opfunc(*args):
            if opcode.opname.index(name) > opcode.HAVE_ARGUMENT:
                if len(args) < 1: raise ValueError('no enough argument')
                self.codes.append(struct.pack('B' ,opcode.opmap[name]))
                self.codes.append(struct.pack('H' ,args[0]))
                self.codes_length += 3
            else:
                self.codes.append(struct.pack('B' ,opcode.opmap[name]))
                self.codes_length += 1
        return opfunc

    def tokenize(self):
        tokens = re.split(r'({[{%][\ ]?[\w_.\ ]+[\ ]?[}%]})', self.text)
        if tokens[0] == '': tokens.pop(0)
        if tokens[-1] == '': tokens.pop(-1)
        def format_token(t):
            if t.startswith('{{') and t.endswith('}}'):
                return NameToken(t[2:-2].strip())
            elif t.startswith('{%') and t.endswith('%}'):
                return ExprToken(t[2:-2].strip())
            return RawToken(t)
        return map(format_token, tokens)

    def compile(self):
        self.BUILD_LIST(0)
        pos_ret_list = self._make_varname('ret_list')
        self.STORE_FAST(pos_ret_list)
        for token in self.tokenize():
            if type(token) == RawToken:
                self.LOAD_FAST(pos_ret_list)
                self.LOAD_ATTR(self._make_name('append'))
                self.LOAD_CONST(self._make_const(token))
                self.CALL_FUNCTION(1)
                self.POP_TOP()
            elif type(token) == NameToken:
                self.LOAD_FAST(pos_ret_list)
                self.LOAD_ATTR(self._make_name('append'))
                self.LOAD_GLOBAL(self._make_name(token.names[0]))
                for name in token.names[1:]:
                    self.LOAD_CONST(self._make_const(name))
                    self.BINARY_SUBSCR()
                self.CALL_FUNCTION(1)
                self.POP_TOP()
            elif type(token) == ExprToken and token.type == 'if':
                self.LOAD_GLOBAL(self._make_name(token.tokens[1]))
                self.POP_JUMP_IF_FALSE(1)
                self.mark = len(self.codes) - 1
            elif type(token) == ExprToken and token.type == 'endif':
                self.codes[self.mark] = struct.pack('H', self.codes_length)



        self.LOAD_CONST(self._make_const(''))
        self.LOAD_ATTR(self._make_name('join'))
        self.LOAD_FAST(pos_ret_list)
        self.CALL_FUNCTION(1)
        self.RETURN_VALUE()
        return self._dump()

    def _dump(self):
        code_string = ''.join(self.codes)
        consts = tuple(self.consts)
        names = tuple(self.names)
        varnames = tuple(self.varnames)
        code_args = (
                0,             # 'argcount' arguments count of the code object
                1,             # 'nlocals' ??
                200,           # 'stack_size' max size of the stack
                75,            # 'flags' ??
                code_string,   # 'codestring' the bytecode instructions
                consts,        # 'constants' constants value for the code object
                names,         # 'names' used names in this code object
                varnames,      # 'varnames' variable names
                'test.py',     # 'filename' filename
                '<module>',    # 'name' name of the function/class/module
                1,             # 'firstlineno' the first line number of this code object
                '',            # 'lnotab' ??
                (),            # 'freevars' for closure
                (),            # 'cellvars': ??
            )
        return code(*code_args)



