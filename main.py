import sys,os,shutil,time
import v,key
from util import *
   
class tfmApp:
    """终端文件管理器"""
    def __init__(self,path:str) -> None:
        self.status = 0 # 0:正常 1:退出
        self.action = self
        self.path = path
        self.dp = displayer(self)
        try:
            self.pager = pager(self,os.listdir(path))
        except PermissionError as e:
            self.dp.printStatus("打开失败:权限不足")
            self.path = os.getcwd()
            self.pager = pager(self,os.listdir(self.path))
        self.fam = fileActionMenu(self)
        self.mm = mainMenu(self)
        self.rd = renameDialog(self)
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
        try:
            self.pager.updatePage(os.listdir(self.path))
        except PermissionError as e:
            self.dp.printStatus("打开失败:权限不足")
            self.path = os.getcwd()
            self.pager.updatePage(os.listdir(self.path))
    def run(self):
        """运行程序"""
        self.dp.hideCursor()
        self.dp.updateScreen()
        #self.pager.print()
        while self.status == 0:
            self.action.runLoop()
        self.dp.showCursor()
    def runLoop(self):
        """运行循环"""
        k = key.get()
        if k:
            if k == 'esc':
                self.mm.show()
            elif k == 'up':
                self.pager.itemLast()
            elif k == 'down':
                self.pager.itemNext()
            elif k == 'left':
                self.pager.pageLast()
            elif k == 'right':
                self.pager.pageNext()
            elif k == 'enter':
                if self.pager.countAll == 0:
                    return
                if os.path.isdir(os.path.join(self.path,self.pager.item[self.pager.chosing - 1])):
                    self.changePath(self.pager.item[self.pager.chosing - 1])
                else:
                    self.fam.start()
            elif k == 'backspace':
                self.changePath("..")
            elif k == 't':
                self.rd.show()
            #self.pager.print()
        else:
            # 没有按键时休眠，降低CPU占用
            time.sleep(0.2)  # 200ms

class displayer:
    """终端显示器"""
    def __init__(self,app:tfmApp) -> None:
        self.app = app
        self.mainBarWidth = 0.7
        self.surfaces = []
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
        for i in self.surfaces:
            i.print()
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
        if os.name == 'nt':
        # Windows 10+ 支持 ANSI
            if hasattr(sys, 'getwindowsversion') and sys.getwindowsversion().build >= 10586:
                sys.stdout.write('\033[2J\033[3J\033[H')
            else:
                os.system('cls')
        else:
            sys.stdout.write('\033[2J\033[H')
        #sys.stdout.flush()
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
        self.print()
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
        self.print()
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
        self.print()
    def itemLast(self):
        """上一项"""
        if self.countAll == 0:
            return
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
    def print(self):
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
        self.print()
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
            try:
                self.app.pager.updatePage(os.listdir(self.app.path))
            except PermissionError as e:
                self.app.dp.printStatus("打开失败:权限不足")
                self.app.path = os.getcwd()
                self.app.pager.updatePage(os.listdir(self.app.path))
        elif action == "rename":
            pass
        self.app.dp.surfaces.remove(self)
    def last(self):
        """选择上一项"""
        if self.chosing > 1:
            self.chosing -= 1
        else:
            self.chosing = len(self.keys)
        self.print()
    def next(self):
        """选择下一项"""
        if self.chosing < len(self.keys):
            self.chosing += 1
        else:
            self.chosing = 1
        self.print()
    def chose(self,n):
        """选择指定项"""
        if n < 1 or n > len(self.keys):
            return None
        self.app.dp.printRightItem(self.action[self.keys[self.chosing - 1]], self.chosing, False)
        self.chosing = n
        self.app.dp.printRightItem(self.action[self.keys[self.chosing - 1]], self.chosing, True)
    def print(self):
        """打印文件操作菜单"""
        for i in range(len(self.keys)):
            self.app.dp.printRightItem(self.action[self.keys[i]], i + 1, i + 1 == self.chosing)
        for i in range(len(self.keys), 10):
            self.app.dp.printRightItem("", i + 1, False)

class renameDialog:
    def __init__(self,app:tfmApp) -> None:
        self.app = app
        self.title = "Rename"
        self.w = 25
        self.h = 4
        self.x = 4
        self.y = app.dp.askValue("cx",self.w)
        self.context = ""
        self.cursorPos = 0
    def runLoop(self):
        k = key.get()
        if k == None:
            time.sleep(0.1)
        elif k != None and len(k) == 1:
            self.context = self.context[:self.cursorPos] + k + self.context[self.cursorPos:]
            self.cursorPos += 1
            self.printContext()
        elif k == 'space':
            self.context = self.context[:self.cursorPos] + " " + self.context[self.cursorPos:]
            self.cursorPos += 1
            self.printContext()
        elif k[:6] == 'shift+':
            char = k[6:].upper()
            self.context = self.context[:self.cursorPos] + char + self.context[self.cursorPos:]
            self.cursorPos += 1
            self.printContext()
        elif k == 'left':
            # 光标左移
            if self.cursorPos > 0:
                self.cursorPos -= 1
                # 这里应该移动终端光标位置
                self.printContext()
        elif k == 'right':
            # 光标右移
            if self.cursorPos < len(self.context):
                self.cursorPos += 1
                # 这里应该移动终端光标位置
                self.printContext()
        elif k == 'enter':
            self.do(self.context)
            self.app.action = self.app
            self.app.dp.surfaces.remove(self)
            self.app.dp.updateScreen()
        elif k == 'esc':
            self.app.action = self.app
            self.app.dp.surfaces.remove(self)
            self.app.dp.updateScreen()
        elif k == 'backspace':
            # 删除光标前的字符
            if self.cursorPos > 0:
                self.context = self.context[:self.cursorPos-1] + self.context[self.cursorPos:]
                self.cursorPos -= 1
                self.printContext()
        elif k == 'ctrl+v':  # 检测 Ctrl+V
            # 获取剪贴板内容
            clip_text = clipboard.get_clipboard_text()
            if clip_text:
                # 过滤掉不可见字符（如换行符等）
                clip_text = ''.join(c for c in clip_text if c.isprintable() or c == ' ')
                # 在光标位置插入
                self.context = (self.context[:self.cursorPos] + 
                              clip_text + 
                              self.context[self.cursorPos:])
                self.cursorPos += len(clip_text)
                self.printContext()
    def show(self):
        self.context = self.app.pager.item[self.app.pager.chosing - 1]
        self.focu = None
        self.cursorPos = len(self.context)
        self.print()
        self.app.action = self # type: ignore
        self.app.dp.surfaces.append(self)
        self.app.dp.updateScreen()
        self.app.dp.showCursor()
    def print(self):
        self.printWindow()
        self.printContext()
    def printWindow(self) -> None:
        self.app.dp.moveCursor(self.x,self.y)
        self.app.dp.set_color(v.COLORS['bright_white'],v.BG_COLORS['magenta'],v.STYLES['bold'])
        sys.stdout.write(str2long(self.title,self.w,direction=0))
        self.app.dp.moveCursor(self.x,self.y + 1)
        self.app.dp.moveCursor(self.x + 1,self.y)
        self.app.dp.set_color(v.COLORS['bright_white'],v.BG_COLORS['cyan'],v.STYLES['bold'])
        sys.stdout.write(str2long("",self.w))
        self.app.dp.moveCursor(self.x + 2,self.y)
        sys.stdout.write(str2long("",self.w))
        self.app.dp.moveCursor(self.x + 3,self.y)
        sys.stdout.write(str2long("",self.w))
        sys.stdout.write(v.RESET)
    def printContext(self):
        self.app.dp.set_color(v.COLORS['bright_white'],v.BG_COLORS['blue'],v.STYLES['bold'])
        self.app.dp.moveCursor(self.x + 2,self.y + 1)
        sys.stdout.write(str2long(self.context[::-1],self.w - 2,direction=-1)[::-1])
        sys.stdout.write(v.RESET)
        cursor_col = min(self.y + 1 + self.cursorPos, self.y + 1 + self.w - 3)
        self.app.dp.moveCursor(self.x + 2, cursor_col)
    def do(self,name:str):
        if name == "":
            self.app.dp.printStatus("重命名失败:名称不能为空")
            return
        try:
            os.rename(os.path.join(self.app.path,self.app.pager.item[self.app.pager.chosing - 1]),os.path.join(self.app.path,name))
            self.app.dp.printStatus(f"重命名成功: {self.app.pager.item[self.app.pager.chosing - 1]} -> {name}")
            self.app.pager.updatePage(os.listdir(self.app.path))
        except Exception as e:
            self.app.dp.printStatus(f"重命名失败: {str(e)}")
        
class Dialog:
    def __init__(self,app:tfmApp) -> None:
        self.app = app
        self.title = "Dialog"
        self.w = 25
        self.h = 6
        self.x = 4
        self.y = app.dp.askValue("cx",self.w)
    def print(self):
        self.app.dp.moveCursor(self.x,self.y)
        self.app.dp.set_color(v.COLORS['bright_white'],v.BG_COLORS['magenta'],v.STYLES['bold'])
        sys.stdout.write(str2long(self.title,self.w,direction=0))
        self.app.dp.moveCursor(self.x,self.y + 1)
        self.app.dp.moveCursor(self.x + 1,self.y)
        self.app.dp.set_color(v.COLORS['bright_white'],v.BG_COLORS['cyan'],v.STYLES['bold'])
        sys.stdout.write(str2long("",self.w))
        self.app.dp.moveCursor(self.x + 2,self.y)
        sys.stdout.write(str2long("施工中...",self.w,direction=0))
        self.app.dp.moveCursor(self.x + 3,self.y)
        sys.stdout.write(str2long("",self.w))
        self.app.dp.moveCursor(self.x + 4,self.y)
        sys.stdout.write(str2long("",self.w))
        self.app.dp.moveCursor(self.x + 5,self.y)
        sys.stdout.write(str2long("",self.w))
        self.app.dp.set_color(v.COLORS['bright_white'],v.BG_COLORS['yellow'],v.STYLES['bold'])
        self.app.dp.moveCursor(self.x + 4,self.y + 1)
        sys.stdout.write(" OK ")
        sys.stdout.write(v.RESET)
    def show(self):
        self.print()
        self.app.action = self # type: ignore
        self.app.dp.surfaces.append(self)
        self.app.dp.updateScreen()
    def runLoop(self):
        k = key.get()
        if not k:
            time.sleep(0.1)
            return None
        elif k == 'esc':
            self.app.action = self.app
            self.app.dp.surfaces.remove(self)
            self.app.dp.updateScreen()
        elif k == 'enter':
            self.app.action = self.app
            self.app.dp.surfaces.remove(self)
            self.app.dp.updateScreen()

class mainMenu:
    action = {"exit":"Exit","setting":"Setting","about":"About"}
    def __init__(self,app:tfmApp) -> None:
        self.app = app
        self.keys = list(self.action.keys())
        self.w = 0
        for i in self.keys:
            w = get_display_width(self.action[i])
            if w >= self.w:
                self.w = w + 1
    def show(self):
        self.chosing = 1
        self.print()
        self.app.action = self # type: ignore
        self.app.dp.surfaces.append(self)
        self.app.dp.updateScreen()
    def print(self):
        self.app.dp.moveCursor(2,1)
        for i in self.keys:
            if self.keys.index(i) + 1 == self.chosing:
                self.app.dp.set_color(v.COLORS['bright_white'],v.BG_COLORS['magenta'],v.STYLES['bold'])
            else:
                self.app.dp.set_color(v.COLORS['white'],v.BG_COLORS['yellow'],v.STYLES['normal'])
            sys.stdout.write(str2long(self.action[i],self.w))
            sys.stdout.write(v.RESET)
            sys.stdout.write("\n")
    def runLoop(self):
        """运行循环"""
        k = key.get()
        if not k:
            time.sleep(0.1)
            return None
        if k == 'esc':
            self.app.action = self.app
            self.app.dp.surfaces.remove(self)
            self.app.dp.updateScreen()
        if k == 'up':
            self.last()
        if k == 'down':
            self.next()
        if k == 'enter':
            self.app.action = self.app
            self.do(self.keys[self.chosing - 1])
            self.app.dp.surfaces.remove(self)
            self.app.dp.updateScreen()
        return None
    def last(self):
        """选择上一项"""
        if self.chosing > 1:
            self.chosing -= 1
        else:
            self.chosing = len(self.keys)
        self.print()
    def next(self):
        """选择下一项"""
        if self.chosing < len(self.keys):
            self.chosing += 1
        else:
            self.chosing = 1
        self.print()
    def do(self,c):
        if c == "exit":
            self.app.status = 1

if __name__ == "__main__":
    app = tfmApp(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    app.run()
    pass