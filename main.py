import sys,os,shutil,time,unicodedata
import v,key

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
    
class tfmApp:
    def __init__(self,path:str) -> None:
        self.status = 0 # 0:正常 1:退出
        self.path = path
        self.pager = pager(self,os.listdir(path))
        self.dp = displayer(self)
    def changePath(self,path):
        pass
    def run(self):
        self.dp.updateScreen()
        self.pager.printPage()
        while self.status == 0:
            self.runLoop()
    def runLoop(self):
        k = key.get()
        if k:
            if k == 'esc':
                self.status = 1
            elif k == 'up':
                self.pager.itemLast()
            elif k == 'down':
                self.pager.itemNext()
            elif k == 'left':
                self.pager.pageLast()
            elif k == 'right':
                self.pager.pageNext()
            elif k == 'enter':
                if os.path.isdir(os.path.join(self.path,self.pager.item[self.pager.chosing - 1])):
                    self.changePath(self.pager.item[self.pager.chosing - 1])
            elif k == 'backspace':
                self.changePath("..")
            #self.pager.printPage()
        else:
            # 没有按键时休眠，降低CPU占用
            time.sleep(0.2)  # 200ms

class displayer:
    def __init__(self,app:tfmApp) -> None:
        self.app = app
        self.get_terminal_size()
    def get_terminal_size(self):
        """获取终端大小（跨平台）"""
        try:
            # 方法1：使用 shutil（推荐）
            columns, rows = shutil.get_terminal_size()
            self.w = columns
            self.h = rows
            return
        except Exception:
            pass
        try:
            # 方法2：使用 os.get_terminal_size()
            columns, rows = os.get_terminal_size()
            self.w = columns
            self.h = rows
            return
        except (AttributeError, OSError):
            pass
        try:
            # 方法3：Windows 特定方法
            if sys.platform == "win32":
                from ctypes import windll, create_string_buffer
                h = windll.kernel32.GetStdHandle(-12)
                csbi = create_string_buffer(22)
                res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
                if res:
                    import struct
                    (_, _, _, _, _, left, top, right, bottom, _, _) = struct.unpack("hhhhHhhhhhh", csbi.raw)
                    columns = right - left + 1
                    rows = bottom - top + 1
                    self.w = columns
                    self.h = rows
                    return
        except Exception:
            pass
        try:
            # 方法4：Unix/Linux/Mac 使用 stty
            if sys.platform != "win32":
                output = os.popen('stty size 2>/dev/null').read().strip()
                if output:
                    rows, columns = output.split()
                    self.w = int(columns)
                    self.h = int(rows)
                    return
        except Exception:
            pass
        # 所有方法都失败，使用默认值
        self.w = 80
        self.h = 24
    def moveCursor(self,x,y):
        """移动光标到指定位置"""
        sys.stdout.write(f"\033[{x};{y}H")
        sys.stdout.flush()
    def updateScreen(self):
        self.clearScreen()
        self.moveCursor(1,1)
        self.set_color(v.COLORS['red'],v.BG_COLORS['blue'],v.STYLES['bold'])
        sys.stdout.write(f" TFM ")
        self.set_color(v.COLORS['red'],v.BG_COLORS['green'],v.STYLES['bold'])
        sys.stdout.write(str2long(self.app.path,self.w - 5))
        sys.stdout.write(v.RESET)
        sys.stdout.write(f"\n{" "*self.w}"*10)
        self.set_color(v.COLORS['bright_red'],v.BG_COLORS['cyan'],v.STYLES['dim'])
        sys.stdout.write("\n--" + str2long("TFM",self.w - 4,"-")+"--")
        sys.stdout.write(v.RESET)
        sys.stdout.flush()
    def set_color(self, fg=None, bg=None, style=None):
        """设置颜色和样式"""
        codes = []
        if style:
            codes.append(str(style))
        if fg:
            codes.append(str(fg))
        if bg:
            codes.append(str(bg))
        if codes:
            sys.stdout.write(f"\033[{';'.join(codes)}m")
            sys.stdout.flush()
    def clearScreen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    def printItem(self,item:str,n:int,selected:bool):
        self.moveCursor(n + 2,1)
        if selected:
            self.set_color(v.COLORS['bright_white'],v.BG_COLORS['blue'],v.STYLES['bold'])
        else:
            self.set_color(v.COLORS['white'],v.BG_COLORS['black'],v.STYLES['normal'])
        sys.stdout.write(str2long(item,self.w))
        sys.stdout.write(v.RESET)
        sys.stdout.write("\n")
        sys.stdout.flush()
    
class pager:
    def __init__(self,app,l) -> None:
        self.app = app
        self.count = 1 # 当前选中项
        self.chosing = 0 # 当前页面的选中项
        self.updatePage(l)
    def updatePage(self,dirList):
        self.dir = dirList # 总条目列表
        self.countAll = len(dirList) # 总条目数
        a = self.countAll / 10
        self.pageAll = a if int(a) == a else int(a) + 1 # 总页数
        self.page = 1 # 当前页码
        self.loadPageItems()
    def loadPageItems(self):
        self.item = self.dir[(self.page - 1) * 10 : self.page * 10] # 当前页的条目列表
    def pageLast(self):
        if self.page > 1:
            self.page -= 1
            self.count -= 10
            self.loadPageItems()
        else:
            self.page = self.pageAll
            a = (self.page - 1) * 10 + self.chosing
            self.count = a if a <= self.countAll else self.countAll
            self.loadPageItems()
    def pageNext(self):
            if self.page < self.pageAll:
                self.page += 1
                self.count += 10
                self.loadPageItems()
            else:
                self.page = 1
                self.count = self.chosing
                self.loadPageItems()
    def itemLast(self):
        if self.chosing > 1:
            self.count -= 1
            self.chosing -= 1
        else:
            self.chosing = 10
            self.count += 10
    def itemNext(self):
            if self.chosing < 10 and self.count < self.countAll:
                self.count -= 1
                self.chosing -= 1
            else:
                self.chosing = 10
                self.count += 10
    def pageChange(self,page):
        pass
    def chose(self,id):
        pass
    def printPage(self):
        for i in range(10):
            if i < len(self.item):
                self.app.dp.printItem(self.item[i],i,i + 1 == self.chosing)
            else:
                self.app.dp.printItem("",i,False)

class fileActionMenu:
    def __init__(self) -> None:
        pass
    pass

if __name__ == "__main__":
    app = tfmApp(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    app.run()
    pass