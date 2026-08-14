import unicodedata,json

def get_display_width(text: str) -> int:
    """
    使用 unicodedata 计算显示宽度
    """
    width = 0
    for char in text:
        # East Asian Width 属性
        east_asian_width = unicodedata.east_asian_width(char)
        if east_asian_width in ('F', 'W'):  # Fullwidth, Wide
            width += 2
        elif east_asian_width in ('H', 'Na'):  # Halfwidth, Narrow
            width += 1
        elif east_asian_width == 'A':  # Ambiguous (在中文环境下通常算2)
            width += 2
        else:  # Neutral
            width += 1
    return width
def str2long(string: str, long: int, b="", s=" ") -> str:
    """
    使用 unicodedata 计算显示宽度
    """
    if long <= 0:
        return ""
    current_width = get_display_width(string)
    if current_width == long:
        return string
    elif current_width < long:
        padding_needed = long - current_width
        return string + s * padding_needed
    else:
        # 截断
        result = ""
        width = 0
        for char in string:
            char_width = 2 if unicodedata.east_asian_width(char) in ('F', 'W', 'A') else 1
            if width + char_width <= long - 1:
                result += char
                width += char_width
            else:
                break
        return result + b
 