from lambdora.tokenizer import lambTokenize

def test_simple_tokens():
    assert lambTokenize("(λx. x)") == ['(', 'λ', 'x', '.', 'x', ')']

def test_comments_are_ignored():
    code = "(+ 1 2) ; this is a comment"
    assert lambTokenize(code) == ['(', '+', '1', '2', ')']
