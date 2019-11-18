import token_type

# lexer
id_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
               '_']

mapPair = {
    '[': ']',
    '{': '}',
    '<': '>',
    '(': ')',
    '\'': '\'',
    '"': '"',
}

num_alphabet = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']

op_alphabet1 = [':', ';', ',',
                '+', '-', '*', '/', '%',
                '=', '<', '>', '!', '?',
                '~',
                '[', ']', '{', '}', '<', '>', '(', ')']

op_alphabet2 = ['+=', '-=', '*=', '/=', '%=',
                '++', '--',
                '>=', '<=', '!=', '==',
                '||', '&&',
                '&=', '|=', '^=']

op_alphabet3 = ['<<=', '>>=']

reserved_ids = ["bool", "char", "short", "int", "long",
                "signed", "unsigned",
                "if", "else", "return",
                "while", "do", "for", "break", "continue"]

# parse
unary_op = ['!', '~', '-',
            '++', '--']

assign_op = ['=',
             ',',
             '+=', '-=', '*=', '/=', '%=',
             '<<=', '>>=', '&=', '|=', '^=']


def read_src(file='return_2.c'):
    with open(file) as f:
        return f.read()


class ClauseCounter:
    def __init__(self):
        self.cnt = 0

    def next(self):
        self.cnt += 1
        return '_clause{}'.format(self.cnt)


def match(tokens, idx, type, value):
    tok = tokens[idx]
    if (tok.type != type or tok.value != value):
        raise "no {}:{}".format(type, value)
    idx += 1
    return idx, tok


def match_type(tokens, idx, type):
    tok = tokens[idx]
    if (tok.type != type):
        raise "no {}".format(type)
    idx += 1
    return idx, tok


def match_value(tokens, idx, value):
    tok = tokens[idx]
    if (tok.value != value):
        raise "no {}".format(value)
    idx += 1
    return idx, tok


def match_type_values(tokens, idx, type, values):
    tok = tokens[idx]
    if (tok.type != type or tok.value not in values):
        raise "no {}:{}".format(type, str(values))
    idx += 1
    return idx, tok
