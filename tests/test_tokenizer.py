import pytest

from lambdora.tokenizer import lambTokenize


def test_simple_tokens():
    assert lambTokenize("(lambda x. x)") == ["(", "lambda", "x", ".", "x", ")"]


def test_comments_are_ignored():
    code = "(+ 1 2) ; this is a comment"
    assert lambTokenize(code) == ["(", "+", "1", "2", ")"]


def test_tokenize_multichar_operators():
    """Test tokenizing multi-character operators and edge cases."""
    from lambdora.tokenizer import lambTokenize

    # Test cases that might hit the missing lines (50, 55)
    tokens = lambTokenize("lambda ")  # Test with 'lambda' keyword
    assert "lambda" in tokens


def test_tokenize_edge_cases():
    """Test edge cases in tokenization that might hit uncovered lines."""
    from lambdora.tokenizer import lambTokenize

    # Test empty string and whitespace edge cases
    tokens = lambTokenize("")
    assert tokens == []

    # Test string ending scenarios
    tokens = lambTokenize("test")
    assert tokens == ["test"]

    # Test with trailing whitespace and edge cases
    tokens = lambTokenize("(+ 1 2)   ")
    assert tokens == ["(", "+", "1", "2", ")"]


def test_tokenizer_unterminated_string():
    """Ensure unterminated string literals raise SyntaxError."""
    with pytest.raises(SyntaxError, match="Unterminated string literal"):
        lambTokenize('"hello')


def test_tokenizer_unexpected_char():
    """Ensure unexpected characters raise SyntaxError."""
    with pytest.raises(SyntaxError, match="Unexpected character: @"):
        lambTokenize("@")
