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
    """终端文件管理器"""
    def __init__(self,path:str) -> None:
        self.status = 0 # 0:正常 1:退出
        self.action = self
        self.path = path
        self.dp = displayer(self)
        self.pager = pager(self,os.listdir(path))
        self.fam = fileActionMenu(self)
    def changePath(self,path):
        """改变当前路径"""
        if path == "":
            return
        elif path == '..':
            # 上级目录
            self.path = os.path.dirname(self.path)
        elif path[0] == '/' or (len(path) >= 2 and path[1] == ':'):
            if os.path.isdir(path):
                self.path = path
            else:
                self.path = os.getcwd()
        else:
            path = os.path.join(self.path,path)
            if os.path.isdir(path):
                self.path = path
            else:
                self.path = os.getcwd()
        self.pager.updatePage(os.listdir(self.path))
    def run(self):
        """运行程序"""
        self.dp.hideCursor()
        self.dp.updateScreen()
        self.pager.printPage()
        while self.status == 0:
            self.action.runLoop()
        self.dp.showCursor()
    def runLoop(self):
        """运行循环"""
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
                else:
                    self.fam.start()
            elif k == 'backspace':
                self.changePath("..")
            #self.pager.printPage()
        else:
            # 没有按键时休眠，降低CPU占用
            time.sleep(0.2)  # 200ms

class displayer:
    """终端显示器"""
    def __init__(self,app:tfmApp) -> None:
        self.app = app
        self.mainBarWidth = 0.7
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
    def hideCursor(self):
        """隐藏光标"""
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
    def showCursor(self):
        """显示光标"""
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    def moveCursor(self,x,y):
        """移动光标到指定位置"""
        sys.stdout.write(f"\033[{x};{y}H")
        sys.stdout.flush()
    def updateScreen(self):
        """更新屏幕显示"""
        self.clearScreen()
        self.moveCursor(1,1)
        self.set_color(v.COLORS['red'],v.BG_COLORS['blue'],v.STYLES['bold'])
        sys.stdout.write(f" TFM ")
        sys.stdout.write(v.RESET)
        sys.stdout.write(f"\n{" "*self.w}"*10)
        sys.stdout.write(str2long("",self.w))
        sys.stdout.write("\n")
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
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    def printLeftItem(self,item:str,n:int,selected:bool):
        """打印左侧条目"""
        self.moveCursor(n + 1,1)
        if selected:
            self.set_color(v.COLORS['bright_white'],v.BG_COLORS['blue'],v.STYLES['bold'])
        else:
            self.set_color(v.COLORS['white'],v.BG_COLORS['black'],v.STYLES['normal'])
        sys.stdout.write(str2long(str(n)+"|"+item,self.askValue("lw")))
        sys.stdout.write(v.RESET)
        sys.stdout.write("\n")
        sys.stdout.flush()
    def printRightItem(self,item:str,n:int,selected:bool):
        """打印右侧条目"""
        self.moveCursor(n + 1,self.askValue("lw") + 1)
        if selected:
            self.set_color(v.COLORS['bright_white'],v.BG_COLORS['blue'],v.STYLES['bold'])
        else:
            self.set_color(v.COLORS['white'],v.BG_COLORS['black'],v.STYLES['normal'])
        sys.stdout.write(str2long(str(n)+"|"+item,self.askValue("rw")))
        sys.stdout.write(v.RESET)
        sys.stdout.write("\n")
        sys.stdout.flush()
    def printStatus(self,status:str):
        """打印状态栏"""
        self.moveCursor(12,1)
        self.set_color(v.COLORS['red'],v.BG_COLORS['green'],v.STYLES['bold'])
        #self.set_color(v.COLORS['bright_white'],v.BG_COLORS['black'],v.STYLES['bold'])
        sys.stdout.write(str2long(status,self.w))
        sys.stdout.write(v.RESET)
        sys.stdout.flush()
    def printTitleBar(self,message:str):
        """打印标题栏"""
        self.moveCursor(1,6)
        self.set_color(v.COLORS['bright_red'],v.BG_COLORS['cyan'],v.STYLES['dim'])
        sys.stdout.write(str2long(message,self.w - 5))
        sys.stdout.write(v.RESET)
        sys.stdout.flush()
    def askValue(self,q):
        """获取值"""
        if q == "lw":
            return int(self.w * self.mainBarWidth)
        elif q == "rw":
            return int(self.w - int(self.w * self.mainBarWidth))
        else:
            return 0
         
class pager:
    """分页器"""
    def __init__(self,app,l) -> None:
        self.app = app
        self.count = 1 # 当前选中项
        self.chosing = 1 # 当前页面的选中项
        self.updatePage(l)
    def updatePage(self,dirList):
        """更新分页器"""
        self.dir = dirList # 总条目列表
        self.countAll = len(dirList) # 总条目数
        a = self.countAll / 10
        self.pageAll = a if int(a) == a else int(a) + 1 # 总页数
        self.page = 1 # 当前页码
        self.loadPageItems()
        if self.chosing > len(self.item):
            self.chosing = len(self.item)
        self.printPage()
    def loadPageItems(self):
        """加载当前页的条目"""
        self.item = self.dir[(self.page - 1) * 10 : self.page * 10] # 当前页的条目列表
    def pageLast(self):
        """上一页"""
        if self.page > 1:
            self.page -= 1
            self.count -= 10
            self.loadPageItems()
        else:
            self.page = self.pageAll
            a = (self.page - 1) * 10 + self.chosing
            self.count = a if a <= self.countAll else self.countAll
            self.loadPageItems()
        self.printPage()
    def pageNext(self):
        """下一页"""
        if self.page < self.pageAll:
            self.page += 1
            self.count += 10
        else:
            self.page = 1
            self.count = self.chosing
        self.loadPageItems()
        if self.chosing > len(self.item):
            self.chosing = len(self.item)
        self.printPage()
    def itemLast(self):
        """上一项"""
        self.app.dp.printLeftItem(self.item[self.chosing - 1],self.chosing,False)
        if self.chosing > 1:
            self.count -= 1
            self.chosing -= 1
        else:
            self.chosing = len(self.item)
            self.count += len(self.item) - 1
        self.app.dp.printLeftItem(self.item[self.chosing - 1],self.chosing,True)
    def itemNext(self):
        """下一项"""
        if self.countAll == 0:
            return
        self.app.dp.printLeftItem(self.item[self.chosing - 1],self.chosing,False)
        if self.chosing < len(self.item) and self.count < self.countAll:
            self.count += 1
            self.chosing += 1
        else:
            self.chosing = 1
            self.count -= len(self.item) - 1
        self.app.dp.printLeftItem(self.item[self.chosing - 1],self.chosing,True)
    def pageChange(self,page):
        pass
    def chose(self,id):
        pass
    def printPage(self):
        """打印当前页"""
        self.app.dp.printTitleBar(f"当前路径: {self.app.path}")
        for i in range(10):
            if i < len(self.item):
                self.app.dp.printLeftItem(self.item[i],i + 1,i + 1 == self.chosing)
            else:
                self.app.dp.printLeftItem("",i + 1,False)
        self.app.dp.printStatus(f"当前页码: {self.page}/{self.pageAll} | 当前选中项: {self.count}/{self.countAll}")

class fileActionMenu:
    """文件操作菜单"""
    action = {"open": "打开", "delete": "删除"}
    def __init__(self, app:tfmApp) -> None:
        self.app = app
        self.keys = list(self.action.keys())
    def start(self):
        """启动文件操作菜单"""
        self.app.action = self # type: ignore
        self.chosing = 1
        self.printMenu()
    def runLoop(self):
        """运行循环"""
        k = key.get()
        if not k:
            time.sleep(0.1)
            return None
        if k == 'esc':
            self.app.action = self.app
            self.app.dp.clearScreen()
            self.app.dp.updateScreen()
            self.app.pager.printPage()
        if k == 'up':
            self.last()
        if k == 'down':
            self.next()
        if k == 'enter':
            self.app.action = self.app
            self.app.dp.clearScreen()
            self.app.dp.updateScreen()
            self.app.pager.printPage()
            self.do(self.keys[self.chosing - 1])
        return None
    def do(self,action):
        """执行操作"""
        if action == "open":
            os.system(f'start "" "{os.path.join(self.app.path,self.app.pager.item[self.app.pager.chosing - 1])}"')
        elif action == "delete":
            os.remove(os.path.join(self.app.path,self.app.pager.item[self.app.pager.chosing - 1]))
            self.app.pager.updatePage(os.listdir(self.app.path))
        
        pass
    def last(self):
        """选择上一项"""
        if self.chosing > 1:
            self.chosing -= 1
        else:
            self.chosing = len(self.keys)
        self.printMenu()
    def next(self):
        """选择下一项"""
        if self.chosing < len(self.keys):
            self.chosing += 1
        else:
            self.chosing = 1
        self.printMenu()
    def chose(self,n):
        """选择指定项"""
        if n < 1 or n > len(self.keys):
            return None
        self.app.dp.printRightItem(self.action[self.keys[self.chosing - 1]], self.chosing, False)
        self.chosing = n
        self.app.dp.printRightItem(self.action[self.keys[self.chosing - 1]], self.chosing, True)
    def printMenu(self):
        """打印文件操作菜单"""
        for i in range(len(self.keys)):
            self.app.dp.printRightItem(self.action[self.keys[i]], i + 1, i + 1 == self.chosing)
        for i in range(len(self.keys), 10):
            self.app.dp.printRightItem("", i + 1, False)

if __name__ == "__main__":
    app = tfmApp(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    app.run()
    pass