def assert_line_contains(line: str, text: str, starts_at: int = 0):
    if starts_at == 0:
        if text in line:
            return
        else:
            raise AssertionError(f"Line {line[starts_at:]}\ndoes not contain\n'{text}'")

    if starts_at > len(line) - 1:
        raise AssertionError(f"Line of length {len(line)} cannot be indexed at {starts_at}")

    if len(text) > len(line[starts_at:]):
        raise AssertionError(f"Line of length {len(line[starts_at:])} is shorter than text of length {len(text)}")

    for index, char in enumerate(line[starts_at:]):
        if not text[index] == char:
            raise AssertionError(f"Line {line[starts_at:]}\ndoes not match\n'{text}'\nat index {index}")

