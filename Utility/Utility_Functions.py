class StringUtility:

    @staticmethod
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
    
    @staticmethod
    def roman_to_num(string_input):
        import roman
        
        # Roman works with upper case text as of 3.0

        string_input_upper = string_input.upper()

        try:
            return roman.fromRoman(string_input_upper)
        except roman.RomanError:
            return 0
        
    @staticmethod
    def get_title_number(string_input):
        from Utility.Utility_Functions import StringUtility

        input_list = string_input.split('-')

        major_title = StringUtility.roman_to_num(input_list[0])
        minor_title = 0

        if len(input_list) >= 2:
            minor_title = StringUtility.char_to_num(input_list[1])

        title_number_text = str(major_title)+'.'+str(minor_title)

        return float(title_number_text)

    @staticmethod
    def month_replace_period(string_input):
        # Move to top level or create own class
        month_replace = [
            ('Jan.', 'Jan'),
            ('Feb.', 'Feb'),
            ('Mar.', 'Mar'),
            ('Apr.', 'Apr'),
            ('Aug.', 'Aug'),
            ('Sep.', 'Sep'),
            ('Oct.', 'Oct'),
            ('Nov.', 'Nov'),
            ('Dec.', 'Dec'),
            ('Sept.', 'Sept')
        ]
        _string_input = string_input
        
        for k, v in month_replace:
            _string_input = _string_input.replace(k,v)
        return _string_input