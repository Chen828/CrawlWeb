from tkinter import *       # 引入tk模块
from crawlweb.CrawlCNKI import crawlCNKI      # 引入CrawlCNKI模块
from crawlweb.CrawlSD import crawlSD      # 引入CrawlSD模块
from crawlweb.CrawlSpringer import crawlSpringer      # 引入CrawlSpringer模块
from crawlweb.CrawlWoS import crawlWoS      # 引入CrawlWoS模块


class crawlerGUI:

    def __init__(self, r):
        self.root = r

        self.root.title("Literature Crawler")  # 窗口标题
        self.root.geometry('600x430')  # 窗口大小(宽x高)，是x（艾克斯） 不是*
        self.root.resizable(width=True, height=True)  # 高、宽不可变,默认为True

        """一级frame_top"""
        frame_top = Frame(self.root)
        # 间隔行
        label1 = Label(frame_top, text=" ")
        label1.pack(side=TOP)       # 包装label1

        # 提示标签
        label = Label(frame_top, text="请输入关键词:")  # 提示语
        # label = Label(root, text="请输入关键词", bg="green", font=("Arial", 12), width=5, height=2)
        label.pack(side=LEFT)    # 这里的side可以赋值为LEFT  RTGHT TOP  BOTTOM

        # 输入框
        key = StringVar()  # 绑定变量
        self.key_value = Entry(frame_top, textvariable=key, width=35)  # key_value=Entry(根对象, textvariable = key)
        self.key_value.focus()      # 聚焦key_value
        key.set(" ")  # 设置文本框中的值   var.set(item)
        self.key_value.pack(side=RIGHT)       # 包装

        frame_top.pack(side=TOP)       # 包装
        self.frame()    # 调用frame()函数
        self.root.mainloop()  # 进入消息循环，mainloop则是主窗口的成员函数，也就是表示让这个root工作起来，开始接收鼠标的和键盘的操作。

    def frame(self):

        """一级frame：left、right"""
        frame_bottom = Frame(self.root)  # Frame(根对象, [属性列表])

        # 间隔行
        label = Label(frame_bottom, text=" ")
        label.pack(side=TOP)       # 包装

        """二级frame（选库），left"""
        frame_left = Frame(frame_bottom)       # 嵌入到frame_bottom
        # 各个button按钮及相应的映射
        label_space1 = Label(frame_left, text="")       # 嵌入到frame_left
        label_space1.pack()       # 包装
        # 调用CNKI_click方法，不能加()
        Button(frame_left, text="CNKI", command=self.CNKI_click).pack()

        label_space2 = Label(frame_left, text="")       # 嵌入到frame_left
        label_space2.pack()       # 包装
        # 调用WoS_click方法，不能加()
        Button(frame_left, text="Web of Science", command=self.WoS_click).pack()

        label_space3 = Label(frame_left, text="")       # 嵌入到frame_left
        label_space3.pack()       # 包装
        #  调用SD_click方法，不能加()
        Button(frame_left, text="Science Direct", command=self.SD_click).pack()

        label_space5 = Label(frame_left, text="")       # 嵌入到frame_left
        label_space5.pack()       # 包装
        # 调用Springer_click方法，不能加()
        Button(frame_left, text="Springer", command=self.Springer_click).pack()

        frame_left.pack(side=LEFT)       # 包装

        """二级frame_right（返回值）：text(left),scrollbar(right)"""
        frame_right = Frame(frame_bottom)       # 嵌入到frame_bottom
        text = Text(frame_right)       # 嵌入到frame_right
        text.insert(1.0, 'Hello,Welcome to Literature Crawler!\n')  # 1.0:这个Textbuffer的第一个字符

        # Scrollbar滚轮
        scrollbar = Scrollbar(frame_right)       # 嵌入到frame_right
        scrollbar.pack(side=RIGHT, fill=Y)       # 包装
        text.configure(yscrollcommand=scrollbar.set)
        text.pack(side=LEFT, fill=BOTH)  # 包装、充满整个窗体(只有pack的组件实例才能显示)
        scrollbar['command'] = text.yview
        frame_right.pack(side=RIGHT)       # 包装

        frame_bottom.pack(side=TOP)

    # 各个button响应

    def CNKI_click(self):
        word = self.key_value.get()  # 获取文本框中的值
        crawlCNKI(word)

    def WoS_click(self):
        word = self.key_value.get()  # 获取文本框中的值
        crawlWoS(word)

    def SD_click(self):
        word = self.key_value.get()  # 获取文本框中的值
        crawlSD(word)

    def Springer_click(self):
        word = self.key_value.get()  # 获取文本框中的值
        crawlSpringer(word)
