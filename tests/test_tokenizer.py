"""Comprehensive tests for the tokenizer module."""

import pytest

from lambdora.errors import TokenizeError
from lambdora.tokenizer import lambTokenize


def test_basic_tokenization():
    """Test basic tokenization of different input types."""
    # Test simple literals
    tokens = lambTokenize("42")
    assert tokens == ["42"]

    # Test variables
    tokens = lambTokenize("x")
    assert tokens == ["x"]

    # Test simple expressions
    tokens = lambTokenize("(+ 1 2)")
    assert tokens == ["(", "+", "1", "2", ")"]

    # Test lambda expressions
    tokens = lambTokenize("(lambda x . x)")
    assert tokens == ["(", "lambda", "x", ".", "x", ")"]


def test_complex_tokenization():
    """Test tokenization of complex expressions."""
    # Test nested expressions
    tokens = lambTokenize("(+ (* 2 3) (if true 1 0))")
    assert "(" in tokens and ")" in tokens
    assert "+" in tokens and "*" in tokens

    # Test with strings
    tokens = lambTokenize('("hello" "world")')
    assert '"hello"' in tokens
    assert '"world"' in tokens


def test_tokenizer_edge_cases():
    """Test tokenizer with various edge cases."""
    # Test with empty string (should work)
    tokens = lambTokenize("")
    assert tokens == []

    # Test with just whitespace
    tokens = lambTokenize("   \n\t  ")
    assert tokens == []

    # Test with comments
    tokens = lambTokenize("; just a comment")
    assert tokens == []

    # Test with mixed comments and code
    tokens = lambTokenize("42 ; comment")
    assert tokens == ["42"]


def test_tokenizer_error_conditions():
    """Test tokenizer error conditions."""
    # Test unterminated string
    with pytest.raises(TokenizeError):
        lambTokenize('"unterminated_string')

    # Test with unexpected characters
    with pytest.raises(TokenizeError):
        lambTokenize("unexpected_char_@")


def test_string_literals():
    """Test string literal tokenization."""
    # Test simple strings
    tokens = lambTokenize('"hello"')
    assert tokens == ['"hello"']

    # Test strings with spaces
    tokens = lambTokenize('"hello world"')
    assert tokens == ['"hello world"']

    # Test strings with special characters
    tokens = lambTokenize('"hello\nworld"')
    assert tokens == ['"hello\nworld"']


def test_whitespace_handling():
    """Test whitespace handling in tokenization."""
    # Test various whitespace characters
    tokens = lambTokenize("  (  +  1  2  )  ")
    assert tokens == ["(", "+", "1", "2", ")"]

    # Test newlines and tabs
    tokens = lambTokenize("(\n+\t1\n2\n)")
    assert tokens == ["(", "+", "1", "2", ")"]


def test_comments():
    """Test comment handling in tokenization."""
    # Test single line comments
    tokens = lambTokenize("42 ; this is a comment")
    assert tokens == ["42"]

    # Test comments with code after
    tokens = lambTokenize("42 ; comment\n(+ 1 2)")
    assert tokens == ["42", "(", "+", "1", "2", ")"]

    # Test comment only lines
    tokens = lambTokenize("; just a comment")
    assert tokens == []


def test_unterminated_string_error():
    """Test error handling for unterminated strings."""
    with pytest.raises(TokenizeError):
        lambTokenize('"unterminated')


def test_unexpected_character_error():
    """Test error handling for unexpected characters."""
    with pytest.raises(TokenizeError):
        lambTokenize("unexpected_char_@")


def test_tokenizer_with_complex_expressions():
    """Test tokenizer with complex expressions."""
    # Test nested expressions
    tokens = lambTokenize("(+ (* 2 3) (if true 1 0))")
    assert "(" in tokens and ")" in tokens
    assert "+" in tokens and "*" in tokens

    # Test with strings and variables
    tokens = lambTokenize('(define message "hello")')
    assert "define" in tokens
    assert "message" in tokens
    assert '"hello"' in tokens
