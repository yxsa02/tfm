# key.py
import sys
import time

try:
    # Windows
    import msvcrt
    
    def getch(timeout=0.1):  # pyright: ignore[reportRedeclaration]
        """Windows 下的按键获取，支持超时"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                # 处理扩展按键（方向键、功能键等）
                if ch in (b'\x00', b'\xe0'):  # 扩展按键前缀
                    # 读取实际扫描码
                    ch2 = msvcrt.getch()
                    # 返回组合，用于后续识别
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
    
    def getch(timeout=0.1):
        """带超时的getch，用于检测转义序列"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd) # type: ignore
        try:
            tty.setraw(sys.stdin.fileno())  # type: ignore
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                ch = sys.stdin.read(1)
                return ch
            return ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) # type: ignore

def get():
    """
    等待用户按下按键并返回按键名称
    返回常见的按键名称，如 'up', 'down', 'enter', 'esc', 'a', '1' 等
    """
    key = getch(timeout=0.3)
    
    if not key:
        return None
    
    # Windows 扩展按键处理
    if isinstance(key, bytes) and len(key) == 2:
        prefix, code = key[0], key[1]
        # 方向键（前缀 0x00 或 0xE0）
        if prefix in (0x00, 0xE0):
            # 方向键扫描码
            if code == 0x48:   # H
                return 'up'
            elif code == 0x50: # P
                return 'down'
            elif code == 0x4B: # K
                return 'left'
            elif code == 0x4D: # M
                return 'right'
            elif code == 0x47: # G
                return 'home'
            elif code == 0x4F: # O
                return 'end'
            elif code == 0x53: # S
                return 'delete'
            elif code == 0x3B: # ;
                return 'f1'
            elif code == 0x3C: # <
                return 'f2'
            elif code == 0x3D: # =
                return 'f3'
            elif code == 0x3E: # >
                return 'f4'
            elif code == 0x3F: # ?
                return 'f5'
            elif code == 0x40: # @
                return 'f6'
            elif code == 0x41: # A
                return 'f7'
            elif code == 0x42: # B
                return 'f8'
            elif code == 0x43: # C
                return 'f9'
            elif code == 0x44: # D
                return 'f10'
            elif code == 0x85: # 
                return 'f11'
            elif code == 0x86: # 
                return 'f12'
            else:
                return f'ext_{code:02x}'
    
    # 处理 ESC 转义序列（Unix/Linux/Mac）
    if key == '\x1b':
        next_char = getch(timeout=0.05)
        
        if next_char == '':
            return 'esc'
        
        elif next_char == '[':
            direction = getch(timeout=0.05)
            
            if direction == '':
                return 'esc'
            
            # 方向键
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
            elif direction == '3':
                next_char = getch(timeout=0.05)
                if next_char == '~':
                    return 'delete'
                return f'csi_{direction}{next_char}'
            elif direction in '12345':
                next_char = getch(timeout=0.05)
                if next_char == '~':
                    return f'f{direction}'
                return f'csi_{direction}{next_char}'
            else:
                return f'csi_{direction}'
        
        elif next_char == 'O':
            direction = getch(timeout=0.05)
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
    
    # 处理普通特殊键
    elif key in ('\r', '\n'):
        return 'enter'
    elif key == '\t':
        return 'tab'
    elif key == '\x7f':
        return 'backspace'
    elif key == ' ':
        return 'space'
    
    # Ctrl组合键
    elif isinstance(key, str) and 1 <= ord(key) <= 26:
        ctrl_char = chr(ord(key) + 64)
        return f'ctrl+{ctrl_char.lower()}'
    
    # 普通可打印字符
    elif isinstance(key, str):
        if key.isprintable():
            return key.lower() if key.isalpha() else key
        return f'0x{ord(key):02x}'
    
    # 其他
    return f'unknown_{key}'

# 测试代码 - 只在直接运行此文件时执行
if __name__ == '__main__':
    print("按任意键测试 (按 ESC 退出)")
    print("方向键: ↑ ↓ ← →")
    print("特殊键: Enter, Tab, Space, Backspace")
    print("组合键: Ctrl+C, Ctrl+V 等")
    print("-" * 40)
    
    while True:
        k = get()
        if k:
            print(f"按下了: {k}")
            if k == 'esc':
                print("退出程序")
                break