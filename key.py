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
        """获取单个字符"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd) # type: ignore
        try:
            tty.setraw(sys.stdin.fileno()) # type: ignore
            if blocking:
                ch = sys.stdin.read(1)
                return ch
            else:
                rlist, _, _ = select.select([sys.stdin], [], [], 0.001)
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
    # 先获取第一个字符
    key = getch(blocking=blocking)
    
    if not key:
        return None
    
    # Windows 处理
    if isinstance(key, bytes):
        if len(key) == 2:
            prefix, code = key[0], key[1]
            if prefix in (0x00, 0xE0):
                key_map = {
                    0x48: 'up', 0x50: 'down', 0x4B: 'left', 0x4D: 'right',
                    0x47: 'home', 0x4F: 'end', 0x53: 'delete', 0x52: 'insert',
                    0x3B: 'f1', 0x3C: 'f2', 0x3D: 'f3', 0x3E: 'f4',
                    0x3F: 'f5', 0x40: 'f6', 0x41: 'f7', 0x42: 'f8',
                    0x43: 'f9', 0x44: 'f10', 0x85: 'f11', 0x86: 'f12',
                }
                if code in key_map:
                    return key_map[code]
                return f'ext_{code:02x}'
        return f'unknown_{key.hex()}'
    
    # Unix/Linux/Mac - 处理转义序列
    if key == '\x1b':
        # 读取完整的转义序列
        # 先读取下一个字符（阻塞），判断是否是 '['
        next_char = getch(blocking=True)
        
        if not next_char:
            return 'esc'
        
        # 如果是 '['，继续读取命令字符
        if next_char == '[':
            cmd = getch(blocking=True)
            if not cmd:
                return 'esc'
            
            # 方向键: [A, [B, [C, [D
            if cmd == 'A':
                return 'up'
            elif cmd == 'B':
                return 'down'
            elif cmd == 'C':
                return 'right'
            elif cmd == 'D':
                return 'left'
            elif cmd == 'H':
                return 'home'
            elif cmd == 'F':
                return 'end'
            
            # 功能键: [2~, [3~, [5~, [6~ 等
            elif cmd.isdigit():
                # 读取 '~' 或更多数字
                next_char2 = getch(blocking=True)
                if not next_char2:
                    return f'csi_{cmd}'
                
                if next_char2 == '~':
                    # 单数字功能键
                    key_map = {
                        '1': 'home',
                        '2': 'insert',
                        '3': 'delete',
                        '4': 'end',
                        '5': 'pageup',
                        '6': 'pagedown',
                        '7': 'home',
                        '8': 'end',
                    }
                    if cmd in key_map:
                        return key_map[cmd]
                    if cmd.isdigit():
                        f_num = int(cmd)
                        if 1 <= f_num <= 12:
                            return f'f{f_num}'
                    return f'csi_{cmd}~'
                else:
                    # 多数字功能键，如 [15~, [17~ 等
                    # 继续读取直到遇到 '~'
                    seq = cmd + next_char2
                    while True:
                        ch = getch(blocking=False)
                        if not ch:
                            break
                        seq += ch
                        if ch == '~':
                            break
                    
                    if seq.endswith('~'):
                        num_str = seq[:-1]
                        if num_str.isdigit():
                            f_num = int(num_str)
                            if 1 <= f_num <= 12:
                                return f'f{f_num}'
                    return f'csi_{seq}'
            else:
                return f'csi_{cmd}'
        
        # SS3 序列: O ...
        elif next_char == 'O':
            cmd = getch(blocking=True)
            if not cmd:
                return 'esc'
            
            if cmd == 'P':
                return 'f1'
            elif cmd == 'Q':
                return 'f2'
            elif cmd == 'R':
                return 'f3'
            elif cmd == 'S':
                return 'f4'
            elif cmd == 'A':
                return 'up'
            elif cmd == 'B':
                return 'down'
            elif cmd == 'C':
                return 'right'
            elif cmd == 'D':
                return 'left'
            else:
                return f'ss3_{cmd}'
        
        else:
            # 其他以 ESC 开头的序列
            return f'esc'
    
    # 特殊键
    special_keys = {
        '\r': 'enter',
        '\n': 'enter',
        '\x7f': 'backspace',
        '\x08': 'backspace',
        '\t': 'tab',
        ' ': 'space',
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