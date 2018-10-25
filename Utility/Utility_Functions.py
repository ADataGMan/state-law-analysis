def char_to_num(char_to_convert):
    if len(char_to_convert) != 1:
        return 0
    converted_char = ord(char_to_convert)
    if 65 <= converted_char <= 90:
        # Upper case letter
        return converted_char - 64
    elif 97 <= converted_char <= 122:
        # Lower case letter
        return converted_char - 96
    # Unrecognized character
    return 0