from values import Pair, nil, valueToString

def test_value_to_string_nested_pair():
    p = Pair(1, Pair(2, Pair(3, nil)))
    assert valueToString(p) == "(1 2 3)"