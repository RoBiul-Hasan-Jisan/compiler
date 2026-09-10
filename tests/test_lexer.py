import pytest

from mcpp.lexer import Lexer
from mcpp.tokens import TokenType
from mcpp.errors import LexError


def types_of(source):
    return [t.type for t in Lexer(source).tokenize()]


def test_empty_source_yields_only_eof():
    assert types_of("") == [TokenType.EOF]


def test_int_and_float_literals():
    tokens = Lexer("42 3.14").tokenize()
    assert tokens[0].type == TokenType.INT_LIT and tokens[0].value == 42
    assert tokens[1].type == TokenType.FLOAT_LIT and tokens[1].value == 3.14


def test_string_literal_with_escapes():
    tokens = Lexer(r'"hi\n\"there\""').tokenize()
    assert tokens[0].type == TokenType.STRING_LIT
    assert tokens[0].value == 'hi\n"there"'


def test_char_literal():
    tokens = Lexer("'a'").tokenize()
    assert tokens[0].type == TokenType.CHAR_LIT
    assert tokens[0].value == "a"


def test_keywords_recognised():
    types = types_of("int float if else while for return true false")
    assert types == [
        TokenType.INT, TokenType.FLOAT, TokenType.IF, TokenType.ELSE,
        TokenType.WHILE, TokenType.FOR, TokenType.RETURN, TokenType.TRUE,
        TokenType.FALSE, TokenType.EOF,
    ]


def test_two_character_operators():
    types = types_of("== != <= >= && || ++ --")
    assert types == [
        TokenType.EQ, TokenType.NEQ, TokenType.LTE, TokenType.GTE,
        TokenType.AND, TokenType.OR, TokenType.PLUS_PLUS, TokenType.MINUS_MINUS,
        TokenType.EOF,
    ]


def test_line_comment_is_skipped():
    tokens = Lexer("int a; // trailing comment\nint b;").tokenize()
    types = [t.type for t in tokens]
    assert types.count(TokenType.INT) == 2


def test_block_comment_is_skipped():
    tokens = Lexer("int /* skip me */ a;").tokenize()
    assert [t.type for t in tokens] == [TokenType.INT, TokenType.IDENTIFIER, TokenType.SEMICOLON, TokenType.EOF]


def test_unterminated_string_raises():
    with pytest.raises(LexError):
        Lexer('"never closed').tokenize()


def test_unknown_character_raises():
    with pytest.raises(LexError):
        Lexer("int a = 5 @ 3;").tokenize()


def test_line_and_column_tracking():
    tokens = Lexer("int a;\nfloat b;").tokenize()
    float_tok = next(t for t in tokens if t.type == TokenType.FLOAT)
    assert float_tok.line == 2
    assert float_tok.column == 1
