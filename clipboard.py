import sys
import subprocess

def get_clipboard_text():
    """获取系统剪贴板文本（跨平台）"""
    if sys.platform == "win32":
        return _get_clipboard_windows()
    elif sys.platform == "darwin":
        return _get_clipboard_macos()
    else:  # Linux
        return _get_clipboard_linux()

def _get_clipboard_windows():
    try:
        import win32clipboard
        import win32con
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data
    except:
        return ""

def _get_clipboard_macos():
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout
    except:
        return ""

def _get_clipboard_linux():
    try:
        # 尝试 xclip
        result = subprocess.run(['xclip', '-o', '-selection', 'clipboard'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
    except:
        pass
    
    try:
        # 尝试 xsel
        result = subprocess.run(['xsel', '-b'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
    except:
        pass
    
    return ""

def set_clipboard_text(text):
    """设置系统剪贴板文本（跨平台）"""
    if sys.platform == "win32":
        _set_clipboard_windows(text)
    elif sys.platform == "darwin":
        _set_clipboard_macos(text)
    else:
        _set_clipboard_linux(text)

def _set_clipboard_windows(text):
    try:
        import win32clipboard
        import win32con
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
    except:
        pass

def _set_clipboard_macos(text):
    try:
        p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
        p.communicate(text)
    except:
        pass

def _set_clipboard_linux(text):
    try:
        p = subprocess.Popen(['xclip', '-i', '-selection', 'clipboard'], 
                           stdin=subprocess.PIPE, text=True)
        p.communicate(text)
    except:
        try:
            p = subprocess.Popen(['xsel', '-b'], stdin=subprocess.PIPE, text=True)
            p.communicate(text)
        except:
            pass