# 颜色代码格式: \033[样式;前景色;背景色m

# 基本颜色代码
COLORS = {
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'bright_black': 90,
    'bright_red': 91,
    'bright_green': 92,
    'bright_yellow': 93,
    'bright_blue': 94,
    'bright_magenta': 95,
    'bright_cyan': 96,
    'bright_white': 97,
}

# 背景颜色
BG_COLORS = {
    'black': 40,
    'red': 41,
    'green': 42,
    'yellow': 43,
    'blue': 44,
    'magenta': 45,
    'cyan': 46,
    'white': 47,
}

# 样式
STYLES = {
    'normal': 0,
    'bold': 1,
    'dim': 2,
    'italic': 3,
    'underline': 4,
    'blink': 5,
    'reverse': 7,
    'hidden': 8,
    'strike': 9,
}

RESET = '\033[0m'  # 重置所有样式
CLEAR_SCREEN = "\033[2J"      # 清除整个屏幕
CLEAR_LINE = "\033[2K"        # 清除当前行
CLEAR_TO_END = "\033[0J"      # 从光标位置清除到屏幕末尾
CLEAR_TO_START = "\033[1J"    # 从屏幕开头清除到光标位置
CLEAR_LINE_TO_END = "\033[0K" # 从光标位置清除到行尾
CLEAR_LINE_TO_START = "\033[1K" # 从行首清除到光标位置
CURSOR_HOME = "\033[H"        # 移动光标到左上角