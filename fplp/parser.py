"""FPLP Language - Recursive Descent / Pratt Parser"""

from .lexer import *
from .ast_nodes import *


# --- Precedence levels ---
_LOWEST = 1
_ASSIGN = 2
_OR = 3
_AND = 4
_EQUALS = 5
_COMP = 6      # < > <= >=
_TERM = 7      # + -
_FACTOR = 8    # * / %
_PREFIX = 9
_CALL = 10     # () []


_PRECEDENCES = {
    ASSIGN: _ASSIGN,
    OR: _OR,
    AND: _AND,
    EQ: _EQUALS,
    NE: _EQUALS,
    LT: _COMP,
    GT: _COMP,
    LE: _COMP,
    GE: _COMP,
    PLUS: _TERM,
    MINUS: _TERM,
    MUL: _FACTOR,
    DIV: _FACTOR,
    MOD: _FACTOR,
    LPAREN: _CALL,
    LBRACKET: _CALL,
    DOT: _CALL,
}


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = []
        self.pos = 0
        self._tokenize()

    def _tokenize(self):
        """Collect all tokens from lexer."""
        while True:
            tok = self.lexer.next_token()
            self.tokens.append(tok)
            if tok.type == EOF:
                break

    def _current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(EOF, "", 0, 0)

    def _peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(EOF, "", 0, 0)

    def _advance(self):
        tok = self._current()
        self.pos += 1
        return tok

    def _expect(self, type_, msg=None):
        tok = self._current()
        if tok.type != type_:
            raise ParserError(
                msg or f"Expected {type_}, got {tok.type} ('{tok.literal}') at L{tok.line}:{tok.col}"
            )
        return self._advance()

    def _check(self, type_):
        return self._current().type == type_

    def _check_peek(self, type_):
        return self._peek().type == type_

    def _skip_newlines(self):
        while self._check(NEWLINE):
            self._advance()

    def _precedence(self, tok_type):
        return _PRECEDENCES.get(tok_type, _LOWEST)

    # ========== Top Level ==========

    def parse_program(self):
        stmts = []
        self._skip_newlines()
        while not self._check(EOF):
            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)
            self._skip_newlines()
        return Program(stmts)

    # ========== Statements ==========

    def _parse_statement(self):
        tok = self._current()

        if tok.type == LET:
            return self._parse_let()
        if tok.type == RETURN:
            return self._parse_return()
        if tok.type == LOOP:
            return self._parse_loop()
        if tok.type == FOR:
            return self._parse_for()
        if tok.type == IF:
            return self._parse_if_expression()
        if tok.type == FN:
            # Named function: fn name(params) { body }
            # Desugar to: let name = fn(params) { body }
            return self._parse_let_fn()

        # Expression statement (may end at newline/eof/semicolon-like boundaries)
        expr = self._parse_expression(_LOWEST)

        # Check for assignment (re-assign) — parsed as InfixExpression due to ASSIGN in infix table
        if isinstance(expr, InfixExpression) and expr.operator == '=':
            if isinstance(expr.left, Identifier):
                return AssignStatement(expr.left.value, expr.right)
            raise ParserError("Left side of assignment must be an identifier")
            return AssignStatement(expr.value, value)

        return ExpressionStatement(expr)

    def _parse_let_fn(self):
        """fn name(params) -> body  OR  fn name(params) { body }
           Desugars to: let name = fn(params) -> body/block
        """
        self._advance()  # consume 'fn'
        ident_tok = self._expect(IDENT, "Expected function name after 'fn'")
        name = Identifier(ident_tok.literal)
        params = self._parse_fn_params()
        body = self._parse_fn_body()
        return LetStatement(name, FnLiteral(params, body))

    def _parse_let(self):
        self._advance()  # consume 'let'
        ident_tok = self._expect(IDENT, "Expected identifier after 'let'")
        self._expect(ASSIGN, "Expected '=' after identifier in let statement")
        value = self._parse_expression(_LOWEST)
        return LetStatement(Identifier(ident_tok.literal), value)

    def _parse_return(self):
        self._advance()  # consume 'return'
        value = self._parse_expression(_LOWEST)
        return ReturnStatement(value)

    def _parse_loop(self):
        """loop identifier in expr { body }  OR  loop condition { body }"""
        self._advance()  # consume 'loop'

        # Check if it's a 'for-each' style: loop x in expr
        first = self._parse_expression(_LOWEST)

        if self._check(IN):
            # for-each: loop identifier in iterable { body }
            ident = first
            if not isinstance(ident, Identifier):
                raise ParserError("Expected identifier before 'in' in loop")
            self._advance()  # consume 'in'
            iterable = self._parse_expression(_LOWEST)
            self._skip_newlines()
            body = self._parse_block()
            return LoopExpression(ident.value, iterable, body, is_while=False)
        else:
            # while-style: loop condition { body }
            self._skip_newlines()
            body = self._parse_block()
            return LoopExpression(None, first, body, is_while=True)

    def _parse_for(self):
        """for identifier in expr { body }  (always for-each style)"""
        self._advance()  # consume 'for'
        ident = self._parse_expression(_LOWEST)
        if not isinstance(ident, Identifier):
            raise ParserError("Expected identifier after 'for'")
        self._expect(IN, "Expected 'in' after identifier in for loop")
        iterable = self._parse_expression(_LOWEST)
        self._skip_newlines()
        body = self._parse_block()
        return LoopExpression(ident.value, iterable, body, is_while=False)

    def _parse_block(self):
        self._expect(LBRACE, "Expected '{' to start block")
        stmts = []
        self._skip_newlines()
        while not self._check(RBRACE) and not self._check(EOF):
            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)
            self._skip_newlines()
        self._expect(RBRACE, "Expected '}' to end block")
        return BlockStatement(stmts)

    # ========== Expressions (Pratt) ==========

    def _parse_expression(self, precedence):
        tok = self._current()

        prefix_fn = self._prefix_parse_fn(tok.type)
        if prefix_fn is None:
            raise ParserError(
                f"No prefix parser for {tok.type} ('{tok.literal}') at L{tok.line}:{tok.col}"
            )

        left = prefix_fn()

        while precedence < self._precedence(self._current().type):
            infix_fn = self._infix_parse_fn(self._current().type)
            if infix_fn is None:
                break
            left = infix_fn(left)

        return left

    def _prefix_parse_fn(self, tok_type):
        map = {
            IDENT: self._parse_identifier,
            INT: self._parse_number,
            FLOAT: self._parse_number,
            STRING: self._parse_string,
            TRUE: self._parse_boolean,
            FALSE: self._parse_boolean,
            NIL: self._parse_nil,
            MINUS: self._parse_prefix,
            NOT: self._parse_prefix,
            PLUS: self._parse_prefix,
            LPAREN: self._parse_group_or_fn_literal,
            LBRACKET: self._parse_array,
            LBRACE: self._parse_map_or_block,
            FN: self._parse_fn_literal,
            IF: self._parse_if_expression,
        }
        return map.get(tok_type)

    def _infix_parse_fn(self, tok_type):
        map = {
            PLUS: self._parse_infix,
            MINUS: self._parse_infix,
            MUL: self._parse_infix,
            DIV: self._parse_infix,
            MOD: self._parse_infix,
            EQ: self._parse_infix,
            NE: self._parse_infix,
            LT: self._parse_infix,
            GT: self._parse_infix,
            LE: self._parse_infix,
            GE: self._parse_infix,
            AND: self._parse_infix,
            OR: self._parse_infix,
            ASSIGN: self._parse_infix,
            LPAREN: self._parse_call,
            LBRACKET: self._parse_index,
            DOT: self._parse_dot,
        }
        return map.get(tok_type)

    # --- Prefix parsers ---

    def _parse_identifier(self):
        tok = self._advance()
        return Identifier(tok.literal)

    def _parse_number(self):
        tok = self._advance()
        return NumberLiteral(tok.literal)

    def _parse_string(self):
        tok = self._advance()
        return StringLiteral(tok.literal)

    def _parse_boolean(self):
        tok = self._advance()
        return BooleanLiteral(tok.literal == 'true')

    def _parse_nil(self):
        self._advance()
        return NilLiteral()

    def _parse_prefix(self):
        op = self._advance().literal
        right = self._parse_expression(_PREFIX)
        return PrefixExpression(op, right)

    def _parse_group_or_fn_literal(self):
        """Parse ( expression ) - parenthesized grouping."""
        self._advance()  # consume '('
        self._skip_newlines()
        expr = self._parse_expression(_LOWEST)
        self._skip_newlines()
        self._expect(RPAREN, "Expected ')' after expression")
        return expr

    def _parse_fn_literal(self):
        """fn (params) => expr  OR  fn (params) { body }"""
        self._advance()  # consume 'fn'
        params = self._parse_fn_params()
        body = self._parse_fn_body()
        return FnLiteral(params, body)

    def _parse_fn_params(self):
        """Parse (param1, param2, ...) - shared helper."""
        self._skip_newlines()
        self._expect(LPAREN, "Expected '(' in function parameters")
        params = []
        self._skip_newlines()
        while not self._check(RPAREN):
            if self._check(COMMA):
                self._advance()
                self._skip_newlines()
                continue
            tok = self._expect(IDENT, "Expected parameter name")
            params.append(Identifier(tok.literal))
            self._skip_newlines()
            if self._check(COMMA):
                self._advance()
                self._skip_newlines()
        self._expect(RPAREN, "Expected ')' after fn parameters")
        self._skip_newlines()
        return params

    def _parse_fn_body(self):
        """Parse function body: { block } or => expr (arrow shorthand).
        Returns a BlockStatement. Arrow form wraps the expr in a ReturnStatement."""
        if self._check(ARROW):
            self._advance()  # consume '=>'
            expr = self._parse_expression(_LOWEST)
            # Wrap in block with implicit return
            return BlockStatement([ReturnStatement(expr)])
        return self._parse_block()

    def _parse_array(self):
        self._advance()  # consume '['
        elements = []
        self._skip_newlines()
        while not self._check(RBRACKET):
            if self._check(COMMA):
                self._advance()
                self._skip_newlines()
                continue
            elements.append(self._parse_expression(_LOWEST))
            self._skip_newlines()
            if self._check(COMMA):
                self._advance()
                self._skip_newlines()
        self._expect(RBRACKET, "Expected ']' to close array")
        return ArrayLiteral(elements)

    def _parse_map_or_block(self):
        """{ key: value, ... } or { statements }.
        We disambiguate: if the first token after { is an expression followed by COLON, it's a map."""
        self._advance()  # consume '{'

        # Quick peek: if empty, it's a block or empty map
        if self._check(RBRACE):
            self._advance()
            return MapLiteral({})

        # Save position to try map first
        saved_pos = self.pos
        try:
            return self._parse_map_inner()
        except ParserError:
            self.pos = saved_pos
            # Parse as block (standalone block, not used in expression context)
            stmts = []
            self._skip_newlines()
            while not self._check(RBRACE) and not self._check(EOF):
                stmt = self._parse_statement()
                if stmt:
                    stmts.append(stmt)
                self._skip_newlines()
            self._expect(RBRACE, "Expected '}'")
            # As expression, a block returns the last expression
            return BlockStatement(stmts)

    def _parse_map_inner(self):
        pairs = {}
        self._skip_newlines()
        while not self._check(RBRACE) and not self._check(EOF):
            if self._check(COMMA):
                self._advance()
                self._skip_newlines()
                continue
            key = self._parse_expression(_LOWEST)
            self._expect(COLON, "Expected ':' in map literal")
            value = self._parse_expression(_LOWEST)
            pairs[key] = value
            self._skip_newlines()
            if self._check(COMMA):
                self._advance()
                self._skip_newlines()
        self._expect(RBRACE, "Expected '}' to close map")
        return MapLiteral(pairs)

    def _parse_if_expression(self):
        self._advance()  # consume 'if'
        condition = self._parse_expression(_LOWEST)
        self._skip_newlines()
        consequence = self._parse_block()
        self._skip_newlines()
        alternative = None
        if self._check(ELSE):
            self._advance()
            self._skip_newlines()
            if self._check(IF):
                # else if chain
                alternative = BlockStatement([ExpressionStatement(self._parse_if_expression())])
            else:
                alternative = self._parse_block()
        return IfExpression(condition, consequence, alternative)

    # --- Infix parsers ---

    def _parse_infix(self, left):
        op = self._advance().literal
        precedence = self._precedence(self.tokens[self.pos - 1].type)
        right = self._parse_expression(precedence)
        return InfixExpression(left, op, right)

    def _parse_call(self, func):
        self._advance()  # consume '('
        args = []
        self._skip_newlines()
        while not self._check(RPAREN):
            if self._check(COMMA):
                self._advance()
                self._skip_newlines()
                continue
            args.append(self._parse_expression(_LOWEST))
            self._skip_newlines()
            if self._check(COMMA):
                self._advance()
                self._skip_newlines()
        self._expect(RPAREN, "Expected ')' after call arguments")
        return CallExpression(func, args)

    def _parse_index(self, left):
        self._advance()  # consume '['
        index = self._parse_expression(_LOWEST)
        self._expect(RBRACKET, "Expected ']' after index")
        return IndexExpression(left, index)

    def _parse_dot(self, left):
        self._advance()  # consume '.'
        # Property access: left.name => IndexExpression(left, "name")
        ident = self._expect(IDENT, "Expected identifier after '.'")
        return IndexExpression(left, StringLiteral(ident.literal))
