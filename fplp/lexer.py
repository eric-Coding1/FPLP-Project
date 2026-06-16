"""FPLP Language - Lexer / Tokenizer"""

import re


# --- Token Types ---
# Literals
INT = "INT"
FLOAT = "FLOAT"
STRING = "STRING"
IDENT = "IDENT"

# Keywords
LET = "LET"
TRUE = "TRUE"
FALSE = "FALSE"
NIL = "NIL"
IF = "IF"
ELSE = "ELSE"
LOOP = "LOOP"
FOR = "FOR"
IN = "IN"
FN = "FN"
BREAK = "BREAK"
CONTINUE = "CONTINUE"
RETURN = "RETURN"
AND = "AND"
OR = "OR"
NOT = "NOT"

# Operators
PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
DIV = "DIV"
MOD = "MOD"
ASSIGN = "ASSIGN"
EQ = "EQ"
NE = "NE"
LT = "LT"
GT = "GT"
LE = "LE"
GE = "GE"

# Delimiters
LPAREN = "LPAREN"
RPAREN = "RPAREN"
LBRACE = "LBRACE"
RBRACE = "RBRACE"
LBRACKET = "LBRACKET"
RBRACKET = "RBRACKET"
COMMA = "COMMA"
COLON = "COLON"
DOT = "DOT"
ARROW = "ARROW"

NEWLINE = "NEWLINE"
EOF = "EOF"
ILLEGAL = "ILLEGAL"


KEYWORDS = {
    "let": LET,
    "true": TRUE,
    "false": FALSE,
    "nil": NIL,
    "if": IF,
    "else": ELSE,
    "loop": LOOP,
    "for": FOR,
    "in": IN,
    "fn": FN,
    "return": RETURN,
    "break": BREAK,
    "continue": CONTINUE,
    "and": AND,
    "or": OR,
    "not": NOT,
}


class Token:
    def __init__(self, type_, literal, line=1, col=1):
        self.type = type_
        self.literal = literal
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, '{self.literal}', L{self.line}:{self.col})"


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self._tokens_cache = None

    def _current(self):
        if self.pos >= len(self.source):
            return ''
        return self.source[self.pos]

    def _peek(self, offset=1):
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ''

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_whitespace(self):
        while self._current() in (' ', '\t', '\r'):
            self._advance()

    def _skip_comment(self):
        """Skip line comment starting with #"""
        while self._current() and self._current() != '\n':
            self._advance()

    def _read_number(self):
        start = self.pos
        is_float = False
        while self._current() and (self._current().isdigit() or self._current() == '.'):
            if self._current() == '.':
                # Check for .. range, which is not a float
                if self._peek() == '.':
                    break
                is_float = True
            self._advance()
        num_str = self.source[start:self.pos]
        if is_float:
            return Token(FLOAT, float(num_str), self.line, self.col - len(num_str))
        # Support hex/binary
        if num_str.startswith('0x') or num_str.startswith('0X'):
            return Token(INT, int(num_str, 16), self.line, self.col - len(num_str))
        if num_str.startswith('0b') or num_str.startswith('0B'):
            return Token(INT, int(num_str, 2), self.line, self.col - len(num_str))
        return Token(INT, int(num_str), self.line, self.col - len(num_str))

    def _read_string(self, quote_char='"'):
        start_line = self.line
        start_col = self.col
        self._advance()  # skip opening quote
        result = []
        escape_map = {'n': '\n', 't': '\t', 'r': '\r', '0': '\0', '\\': '\\', '"': '"', "'": "'"}
        while self._current() and self._current() != quote_char:
            ch = self._current()
            if ch == '\\':
                self._advance()
                esc = self._current()
                result.append(escape_map.get(esc, esc))
            else:
                result.append(ch)
            self._advance()
        if self._current() == quote_char:
            self._advance()  # skip closing quote
        return Token(STRING, ''.join(result), start_line, start_col)

    def _read_identifier(self):
        start = self.pos
        while self._current() and (self._current().isalnum() or self._current() == '_'):
            self._advance()
        word = self.source[start:self.pos]
        tok_type = KEYWORDS.get(word, IDENT)
        return Token(tok_type, word, self.line, self.col - len(word))

    def next_token(self):
        """Yield one token at a time."""
        self._skip_whitespace()

        if self.pos >= len(self.source):
            return Token(EOF, "", self.line, self.col)

        ch = self._current()
        tok_line, tok_col = self.line, self.col

        # Comments
        if ch == '#':
            self._skip_comment()
            return self.next_token()

        # Newlines (significant for statement separation)
        if ch == '\n':
            self._advance()
            # Skip consecutive blank lines
            while self._current() == '\n':
                self._advance()
            return Token(NEWLINE, '\n', tok_line, tok_col)

        # Numbers
        if ch.isdigit() or (ch == '.' and self._peek().isdigit()):
            return self._read_number()

        # Identifiers and keywords
        if ch.isalpha() or ch == '_':
            return self._read_identifier()

        # Strings (double or single)
        if ch in ('"', "'"):
            return self._read_string(ch)

        # Multi-char operators
        next_ch = self._peek()
        two_char = ch + next_ch

        if two_char == '==':
            self._advance(); self._advance()
            return Token(EQ, '==', tok_line, tok_col)
        if two_char == '!=':
            self._advance(); self._advance()
            return Token(NE, '!=', tok_line, tok_col)
        if two_char == '<=':
            self._advance(); self._advance()
            return Token(LE, '<=', tok_line, tok_col)
        if two_char == '>=':
            self._advance(); self._advance()
            return Token(GE, '>=', tok_line, tok_col)
        if two_char == '=>':
            self._advance(); self._advance()
            return Token(ARROW, '=>', tok_line, tok_col)
        # Single-char tokens
        single_map = {
            '+': PLUS, '-': MINUS, '*': MUL, '/': DIV, '%': MOD,
            '=': ASSIGN,
            '<': LT, '>': GT,
            '(': LPAREN, ')': RPAREN,
            '{': LBRACE, '}': RBRACE,
            '[': LBRACKET, ']': RBRACKET,
            ',': COMMA, ':': COLON, '.': DOT,
        }

        if ch in single_map:
            self._advance()
            return Token(single_map[ch], ch, tok_line, tok_col)

        # Unknown
        self._advance()
        return Token(ILLEGAL, ch, tok_line, tok_col)

    def tokenize(self):
        """Tokenize the entire source and return a list of tokens."""
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == EOF:
                break
        return tokens
