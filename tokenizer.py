import re

def lambTokenize(source: str) -> list[str]:
    tokens = []

    # Strip comments
    lines = source.splitlines()
    clean_lines = [line.split(';', 1)[0] for line in lines]
    source = ' '.join(clean_lines)

    i = 0
    while i < len(source):
        char = source[i]

        if char.isspace():
            i += 1
            continue

        if char in '().λ+-*/=<>':
            tokens.append(char)
            i += 1
            continue

        # Identifiers (alpha or underscores)
        if char.isalpha() or char == '_':
            start = i
            while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                i += 1
            tokens.append(source[start:i])
            continue

        # Numbers (integer literals)
        if char.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
            tokens.append(source[start:i])
            continue

        raise SyntaxError(f"Unexpected character: {char}")

    
    return tokens