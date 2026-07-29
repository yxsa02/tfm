# key.py
import sys
import time

try:
    # Windows
    import msvcrt
    
    def getch(blocking=True): # type: ignore
        """Windows 下的按键获取"""
        if blocking:
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                return ch + ch2
            try:
                return ch.decode('utf-8', errors='ignore')
            except:
                return ''
        else:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b'\x00', b'\xe0'):
                    ch2 = msvcrt.getch()
                    return ch + ch2
                try:
                    return ch.decode('utf-8', errors='ignore')
                except:
                    return ''
            return ''
            
except ImportError:
    # Unix/Linux/Mac
    import tty
    import termios
    import select
    
    def getch(blocking=True):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd) # type: ignore
        try:
            tty.setraw(sys.stdin.fileno())  # type: ignore
            if blocking:
                ch = sys.stdin.read(1)
                return ch
            else:
                rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
                if rlist:
                    ch = sys.stdin.read(1)
                    return ch
                return ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) # type: ignore

def get(blocking=True):
    """
    获取按键输入
    blocking=True: 阻塞直到有按键
    blocking=False: 非阻塞，无按键返回 None
    """
    key = getch(blocking=blocking)
    
    if not key:
        return None
    
    # Windows 扩展按键处理
    if isinstance(key, bytes) and len(key) == 2:
        prefix, code = key[0], key[1]
        if prefix in (0x00, 0xE0):
            # 方向键和编辑键
            key_map = {
                0x48: 'up',
                0x50: 'down',
                0x4B: 'left',
                0x4D: 'right',
                0x47: 'home',
                0x4F: 'end',
                0x53: 'delete',
                0x52: 'insert',
                0x37: 'printscreen',
                0x45: 'pause',
                # 功能键 F1-F12
                0x3B: 'f1',
                0x3C: 'f2',
                0x3D: 'f3',
                0x3E: 'f4',
                0x3F: 'f5',
                0x40: 'f6',
                0x41: 'f7',
                0x42: 'f8',
                0x43: 'f9',
                0x44: 'f10',
                0x85: 'f11',
                0x86: 'f12',
            }
            if code in key_map:
                return key_map[code]
            return f'ext_{code:02x}'
        return f'unknown_{key.hex()}'
    
    # 处理 ESC 转义序列（Unix/Linux/Mac）
    if key == '\x1b':
        next_char = getch(blocking=False)
        
        if next_char == '':
            return 'esc'
        
        elif next_char == '[':
            direction = getch(blocking=False)
            
            if direction == '':
                return 'esc'
            
            if direction == 'A':
                return 'up'
            elif direction == 'B':
                return 'down'
            elif direction == 'C':
                return 'right'
            elif direction == 'D':
                return 'left'
            elif direction == 'H':
                return 'home'
            elif direction == 'F':
                return 'end'
            elif direction == '2':
                next_char = getch(blocking=False)
                if next_char == '~':
                    return 'insert'
                return f'csi_{direction}{next_char}'
            elif direction == '3':
                next_char = getch(blocking=False)
                if next_char == '~':
                    return 'delete'
                return f'csi_{direction}{next_char}'
            elif direction == '5':
                next_char = getch(blocking=False)
                if next_char == '~':
                    return 'pageup'
                return f'csi_{direction}{next_char}'
            elif direction == '6':
                next_char = getch(blocking=False)
                if next_char == '~':
                    return 'pagedown'
                return f'csi_{direction}{next_char}'
            elif direction in '12345':
                next_char = getch(blocking=False)
                if next_char == '~':
                    return f'f{direction}'
                return f'csi_{direction}{next_char}'
            else:
                return f'csi_{direction}'
        
        elif next_char == 'O':
            direction = getch(blocking=False)
            if direction == 'P':
                return 'f1'
            elif direction == 'Q':
                return 'f2'
            elif direction == 'R':
                return 'f3'
            elif direction == 'S':
                return 'f4'
            return f'ss3_{direction}'
        
        else:
            return f'esc_{next_char}'
    
    # 处理特殊键
    special_keys = {
        '\r': 'enter',
        '\n': 'enter',
        '\x7f': 'backspace',
        '\x08': 'backspace',
        '\t': 'tab',
        ' ': 'space',
        '\x1b': 'esc',
    }
    if key in special_keys:
        return special_keys[key]
    
    # Ctrl 组合键
    if isinstance(key, str) and 1 <= ord(key) <= 26:
        ctrl_char = chr(ord(key) + 64)
        # 排除已经被处理的键
        excluded = {'H', 'J', 'M', 'I', '['}
        if ctrl_char in excluded:
            return special_keys.get(key, f'ctrl+{ctrl_char.lower()}')
        return f'ctrl+{ctrl_char.lower()}'
    
    # Shift + 字母
    if isinstance(key, str) and key.isupper():
        return f'shift+{key.lower()}'
    
    # 普通可打印字符
    if isinstance(key, str):
        if key.isprintable():
            return key.lower() if key.isalpha() else key
        return f'0x{ord(key):02x}'
    
    return f'unknown_{key}'

# 测试代码
if __name__ == '__main__':
    print("按键测试工具 (按 ESC 或 q 退出)")
    print("-" * 40)
    
    while True:
        k = get()
        if k:
            print(f"按下: {k}")
            if k == 'esc' or k == 'q':
                print("退出")
                break