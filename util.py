import unicodedata

def get_display_width(text: str) -> int:
    """
    使用 unicodedata 计算显示宽度
    """
    width = 0
    for char in text:
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

def str2long(string: str, target_width: int, ellipsis: str = "", 
             padding_char: str = " ", direction: int = 1) -> str:
    """
    调整字符串到指定显示宽度
    
    参数:
        string: 原始字符串
        target_width: 目标显示宽度
        ellipsis: 截断时添加的省略号
        padding_char: 填充字符（可以是多字符字符串）
        direction: 对齐方向
            1   = 右填充（左对齐）
            -1  = 左填充（右对齐）
            0   = 居中对齐
    
    返回:
        调整后的字符串
    """
    if target_width <= 0:
        return ""
    current_width = get_display_width(string)
    # 宽度正好
    if current_width == target_width:
        return string
    # 需要填充
    elif current_width < target_width:
        padding_needed = target_width - current_width
        padding_char_width = get_display_width(padding_char)
        if padding_char_width == 0:
            return string  # 避免死循环
        # 计算需要多少个填充字符
        count = padding_needed // padding_char_width
        remainder = padding_needed % padding_char_width
        # 如果有余数，需要多补一个字符（可能会略超）
        if remainder > 0:
            count += 1
        padding_str = padding_char * count
        # 根据方向决定填充位置
        if direction == 1:  # 右填充（左对齐）
            return string + padding_str
        elif direction == -1:  # 左填充（右对齐）
            return padding_str + string
        else:  # 居中对齐 (direction == 0)
            # 计算左右填充数量
            total_padding_width = padding_needed
            left_padding_width = total_padding_width // 2
            right_padding_width = total_padding_width - left_padding_width
            # 计算左右填充字符数
            left_count = left_padding_width // padding_char_width
            if left_padding_width % padding_char_width > 0:
                left_count += 1
            right_count = right_padding_width // padding_char_width
            if right_padding_width % padding_char_width > 0:
                right_count += 1
            # 如果总宽度超出，从右侧截断
            left_padding = padding_char * left_count
            right_padding = padding_char * right_count
            # 检查实际总宽度，如果超出则从右侧减少
            result = left_padding + string + right_padding
            result_width = get_display_width(result)
            if result_width > target_width:
                # 超出时，减少右侧填充
                excess = result_width - target_width
                right_padding = padding_char * (right_count - 1)
                result = left_padding + string + right_padding
                # 如果还超出（极少情况），尝试减少左侧
                if get_display_width(result) > target_width:
                    left_padding = padding_char * (left_count - 1)
                    result = left_padding + string + right_padding
            return result
    # 需要截断
    else:
        result = ""
        width = 0
        ellipsis_width = get_display_width(ellipsis)
        # 如果省略号本身宽度就超过目标，直接返回省略号
        if ellipsis_width > target_width:
            return ellipsis[:target_width] if target_width > 0 else ""
        # 逐个字符添加，预留省略号空间
        for char in string:
            char_width = get_display_width(char)
            if width + char_width + ellipsis_width <= target_width:
                result += char
                width += char_width
            else:
                break
        return result + ellipsis