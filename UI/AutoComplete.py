from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit, QCompleter


class CodeTextEdit(QTextEdit):
    def __init__(self, searchWords_dict=dict, matchWords_list=list, parent=None):
        super(CodeTextEdit, self).__init__(parent)

        self.movecursor = None
        self.textChangedSign = True
        self.textChanged.connect(self.dealTextChanged)
        self._completer = None
        self.searchWords_dict = searchWords_dict
        self.matchWords_list = matchWords_list
        # print(list(searchWords_dict.keys()))
        # 将传入的搜索词语匹配词整合 , 成为自动匹配选词列表
        self.initAutoCompleteWords()
        # 用户已经完成的前缀
        self.completion_prefix = ''
        self.last_known_content = ''
        self.last_cursor_position = 0  # 记录上一次光标的位置

    def initAutoCompleteWords(self):
        """
        处理autoCompleteWords_list,以及specialCursorDict
        """
        self.autoCompleteWords_list = []
        self.specialCursorDict = {}  # 记录待选值的特殊光标位置
        for i in self.searchWords_dict:
            if "$CURSOR$" in self.searchWords_dict[i]:
                cursorPosition = len(self.searchWords_dict[i]) - len("$CURSOR$") - self.searchWords_dict[i].find(
                    "$CURSOR$")
                self.searchWords_dict[i] = self.searchWords_dict[i].replace("$CURSOR$", '')
                self.specialCursorDict[i] = cursorPosition
        for i in self.matchWords_list:
            if "$CURSOR$" in i:
                cursorPosition = len(i) - len("$CURSOR$") - i.find("$CURSOR$")
                self.matchWords_list[self.matchWords_list.index(i)] = i.replace("$CURSOR$", '')
                self.specialCursorDict[i.replace("$CURSOR$", '')] = cursorPosition

        self.autoCompleteWords_list = list(self.searchWords_dict.keys()) + self.matchWords_list

    def setCompleter(self, c):
        self._completer = c
        c.setWidget(self)  # 设置Qcomplete 要关联的窗口小部件。在QLineEdit上设置QCompleter时，会自动调用此函数。在为自定义小部件提供Qcomplete时，需要手动调用。
        # 更改样式
        c.popup().setStyleSheet('''
        QListView {
            color: #3D3D3D;
            background-color: #FFFFFF;
        }
        QListView::item:selected //选中项
        {
            background-color: #9C9C9C;
            border: 20px solid #9C9C9C;
        }
        QListView::item:selected:active //选中并处于激活状态时
        {
            background-color: #9C9C9C;
            border: 20px solid #9C9C9C;
        }

        QListView::item {
            color: red;
            padding-top: 5px;
            padding-bottom: 5px;
        }

        QListView::item:hover {
            background-color: #9C9C9C;
        }
        QScrollBar::handle:vertical{ //滑块属性设置
            background:#4F4F4F;
            width:2px;
            height:9px;
            border: 0px;
            border-radius:100px;
            }
        QScrollBar::handle:vertical:normal{
            background-color:#4F4F4F;
            width:2px;
            height:9px;
            border: 0px;
            border-radius:100px;
            }
        QScrollBar::handle:vertical:hover{
            background:#E6E6E6;
            width:2px;
            height:9px;
            border: 0px solid #E5E5E5;
            border-radius:100px;
            }
        QScrollBar::handle:vertical:pressed{
            background:#CCCCCC;
            width:2px;
            height:9px;
            border: 0px solid #E5E5E5;
            border-radius:100px;
            }
        ''')

        '''下面是completer的一些属性设置,可以自行修改'''
        # setModelSorting此方法指定模型中项目的排序方式。值为枚举值
        # 分别为QCompleter.UnsortedModel QCompleter.CaseSensitivelySortedModel QCompleter.CaseInsensitivelySortedModel
        # 内容                                      值     描述
        # QCompleter.UnsortedModel                 0  该模型是未排序的。
        # QCompleter.CaseSensitivelySortedModel    1  该模型是大小写敏感的。
        # QCompleter.CaseInsensitivelySortedModel  2  模型不区分大小写。
        self._completer.setModelSorting(QCompleter.CaseSensitivelySortedModel)
        # self.completer.setCaseSensitivity 和 上述 self.completer.setModelSorting 一样 ,同时设置且不对应时setCaseSensitivity不生效
        # Qt.CaseSensitivity 该属性保持匹配的大小写敏感性。
        # self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        # 如果filterMode设置为Qt.MatchStartsWith，则只会显示以类型化字符开头的条目。 Qt.MatchContains将显示包含类型字符的条目，并且Qt.MatchEnds以类型字符结尾的条目显示。
        # 目前，只有这三种模式得以实施。 将filterMode设置为任何其他Qt :: MatchFlag将发出警告，并且不会执行任何操作。
        # 默认模式是Qt :: MatchStartsWith。
        # 这个属性是在Qt 5.2中引入的。
        self._completer.setFilterMode(Qt.MatchContains)

        # 此属性在导航项目时包含完成项。默认True 这个属性是在Qt 4.3中引入的。
        self._completer.setWrapAround(False)

        # 设置补全模式  有三种枚举值： QCompleter.PopupCompletion（默认）  QCompleter.InlineCompletion   QCompleter.UnfilteredPopupCompletion
        # QCompleter.PopupCompletion（默认） 当前完成显示在一个弹出窗口中。
        # QCompleter.InlineCompletion  完成内联显示（作为选定的文本）。
        # QCompleter.UnfilteredPopupCompletion 所有可能的完成都显示在弹出窗口中，最有可能的建议显示为当前。
        c.setCompletionMode(QCompleter.PopupCompletion)

        # QCompleter.setModel(QAbstractItemModel *model)
        # 设置为模型提供QCompleter的模型。 该模型可以是列表模型或树模型。 如果一个模型已经被预先设置好了，并且它有QCompleter作为它的父项，它将被删除。
        # self.completer.setModel(completer_model)
        self._completer.setModel(QStringListModel(self.autoCompleteWords_list, self._completer))

        '''
        当用户激活popup（）中的项目时发送此信号。 （通过点击或按回车）
        QCompleter.activated；如果文本框的当前项目发生更改，则会发出两个信号currentIndexChanged()
        和activated()。无论以编程方式或通过用户交互完成更改，currentIndexChanged()
        总是被发射，而只有当更改是由用户交互引起时才activated()

        注意: 这里的文本框项目发生改变是指QCompleter的项目添加到文本框造成的改变
        '''
        c.activated.connect(self.insertCompletion)  # 为 用户更改项目文档事件 绑定 函数

    def insertCompletion(self, completion):
        """
        当用户激活popup（）中的项目时调用。(通过点击或按回车）
        @completion::添加 QCompleter
        """

        if self._completer.widget() is not self:  # 如果没有绑定completer跳过此事件
            return
        '''
        俩种补全方式
        1. 搜索添加 在searchWords_dict键中的对应项,删除用户输入的匹配项,自动补全其键值
        2. 匹配添加 在
        '''
        tc = self.textCursor()
        # 判断是搜索添加 还是 直接匹配添加
        if completion in self.searchWords_dict:  # 搜索添加
            # 删除输入的搜索词
            for i in self._completer.completionPrefix():
                tc.deletePreviousChar()
            # 让光标移到删除后的位置
            self.setTextCursor(tc)

            # 插入对应的键值
            insertText = self.searchWords_dict[completion]
            tc.insertText(insertText)
            # 关闭自动补全选项面板
            self._completer.popup().hide()

        else:  # 直接匹配添加
            # 计算用户输入和匹配项差值,并自动补全
            extra = len(completion) - len(
                self._completer.completionPrefix())  # self._completer.completionPrefix() 为 当前匹配项中,用户已输入的值 , 如输入 ab 匹配到 ABORT 则返回 ab

            # 判断用户输入单词 与 需要补全内容是否一致,一致就不用操作
            if not self.completion_prefix == completion[-extra:]:
                # 自动补全
                tc.insertText(completion[-extra:])
                # 关闭自动补全选项面板
                self._completer.popup().hide()
        '''更改光标位置'''
        # 移动光标 ,光标位置枚举值
        # cursor_pos = QTextCursor.NoMove #光标不移动
        # cursor_pos = QTextCursor.Start #文档开头
        # cursor_pos = QTextCursor.End #文档结尾
        # cursor_pos = QTextCursor.Up #上一行
        # cursor_pos = QTextCursor.Down #下一行
        # cursor_pos = QTextCursor.Left #向左移动一字符
        # cursor_pos = QTextCursor.Right #向右移动一字符
        # cursor_pos = QTextCursor.StartOfLine  # 行首
        # cursor_pos = QTextCursor.StartOfBlock #段首
        # cursor_pos = QTextCursor.StartOfWord #单词首
        # cursor_pos = QTextCursor.EndOfLine #行末
        # cursor_pos = QTextCursor.EndOfBlock #段末
        # cursor_pos = QTextCursor.EndOfWord #单词末
        # cursor_pos = QTextCursor.PreviousCharacter #上一个字符
        # cursor_pos = QTextCursor.PreviousBlock #上一个段落
        # cursor_pos = QTextCursor.PreviousWord #上一个单词
        # cursor_pos = QTextCursor.NextCharacter #下一个字符
        # cursor_pos = QTextCursor.NextBlock #下一个段落
        # cursor_pos = QTextCursor.NextWord #下一个单词

        # 判断自动补全后是否需要更改特定光标位置
        tc.movePosition(QTextCursor.EndOfWord)  # 先移动到单词尾部,避免错误
        if completion in self.specialCursorDict.keys():  # 存在特殊位置
            for i in range(self.specialCursorDict[completion]):
                tc.movePosition(QTextCursor.PreviousCharacter)
            self.setTextCursor(tc)
            self.movecursor = True
        else:  # 不存在特殊位置,移动到单词末尾
            tc.movePosition(QTextCursor.EndOfWord)
            self.setTextCursor(tc)

    def focusInEvent(self, e):
        # 当edit获取焦点时激活completer
        # Open the widget where you are at in the edit
        if self._completer is not None:
            self._completer.setWidget(self)
        super(CodeTextEdit, self).focusInEvent(e)

    def dealTextChanged(self):
        """
        内容改变处理信号处理
        """

        '''下面是对keyPressEvent面对中文输入法输入时没反应的补充'''
        current_content = self.toPlainText()

        class QKeyEvent:

            def key(self=None):
                return 0

            def text(self=None):
                return current_content  # connect.split('\n')[-1].split(' ')[-1]


            def modifiers(self=None):
                return Qt.AltModifier

        self.keyPressEvent(type('QKeyEvent', (QKeyEvent,), {}))

    def getLastPhrase(self):
        """
        获取新输入的内容
        """
        # 获取全部文本
        current_content = self.toPlainText()
        cursor = self.textCursor()
        current_position = cursor.position()
        # 确定新增文本的起始位置
        start_position = max(self.last_cursor_position, 0)
        # 获取新增的文本
        if self.movecursor:
            start_position = start_position-1  # 如果是特殊光标位置,则需要减1
            self.movecursor = False
        new_content = current_content[start_position:current_position]

        # 更新 last_known_content 和 last_cursor_position
        self.last_cursor_position = current_position
        self.last_known_content = current_content
        # lastPhrase = connect.split('\n')[-1].split(' ')[-1]
        return new_content.strip()

    def mousePressEvent(self, event):
        super(CodeTextEdit, self).mousePressEvent(event)
        cursor = self.textCursor()
        self.last_cursor_position = cursor.position()

    def keyPressEvent(self, e):
        """
        按键按下事件
        @e::<PyQt5.QtGui.QKeyEvent object at 0x000001577FAE8048>
        e.text()输入的文本 , 像换行,tab这样的键是没有文本的
        e.key(),键盘上每个键都对应一个编码 如 换行 16777220,j 74
        """
        isShortcut = False  # 判断是否是快捷键的标志

        # self._completer.popup().isVisible()) 判断 completer 是否弹出
        if self._completer is not None and self._completer.popup().isVisible():
            # print('Popup is up')
            # The following keys are forwarded by the completer to the widget.
            # 如果键入的是特殊键则忽略这次事件
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                return

        if e.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            super(CodeTextEdit, self).keyPressEvent(e)
            cursor = self.textCursor()
            self.last_cursor_position = cursor.position()
            return

        # Ctrl + e 快捷键
        if e.key() == Qt.Key_E and e.modifiers() == Qt.ControlModifier:
            words = self.autoCompleteWords_list
            self._completer.setModel(QStringListModel(words))  # 设置数据
            isShortcut = True
        '''
        if e.key() == Qt.Key_Period:
            #This is how I will do the lookup functionality. Show when period is his, open the list of options.
            self.textCursor().insertText('.')
            self.moveCursor(QtGui.QTextCursor.PreviousWord)
            self.moveCursor(QtGui.QTextCursor.PreviousWord, QtGui.QTextCursor.KeepAnchor)
            dict_key = self.textCursor().selectedText().upper()
            #print('Dict Key' , dict_key)
            self.moveCursor(QtGui.QTextCursor.NextWord)
            self.moveCursor(QtGui.QTextCursor.NextWord)

            #print(dict_key)
            words = self.searchWords_dict[dict_key]
            self._completer.setModel(QStringListModel(words, self._completer))
            isShortcut = True
        '''
        # 当不存在关联的 completer 以及 当前键不是快捷键的时候执行父操作
        if (self._completer is None or not isShortcut) and e.key() != 0:
            # Do not process the shortcut when we have a completer.
            super(CodeTextEdit, self).keyPressEvent(e)

        # 当不存在关联的 completer 或者 有修饰符(ctrl或shift)和输入字符为空时 , 直接返回不进行任何操作
        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)  # 是ctrl或shift这样的修饰词
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        # eow = "~!@#$%^&*()_+{}|:\"<>?,./;\'[]\\-="
        eow = '~!@#$%^&*()_+{}|:\"<>?,./;\'[]\\-='
        # 有修饰符 但 不是ctrl 或者 shift,例如alt出现 hasModifier 就为True
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift  # 判断是否有ctrl与shift外的修饰符

        lastPhrase = self.getLastPhrase()  # 当前出现的单词
        self.completion_prefix = lastPhrase

        # 限制最少输入1个字符后才进行匹配 , 且不满足条件自动关闭界面
        # not isShortcut 确保快捷键可以操作显示自动补全窗口
        # 不是快捷键,同时满足(没有修饰符 或者 文本为空 或者 输入字符少于指定长度 或者 输入文本最后以eow中一个字符结尾)
        if not isShortcut and (len(lastPhrase) == 0 or len(lastPhrase) < 2):
            self._completer.popup().hide()
            return

        # if not isShortcut:
        #     if hasModifier or len(e.text()) == 0 or len(lastPhrase) < 1 or e.text()[-1] in eow:
        #         self._completer.popup().hide()
        #         return

        # 选中第一项
        if lastPhrase != self._completer.completionPrefix():
            # Puts the Prefix of the word youre typing into the Prefix
            self._completer.setCompletionPrefix(lastPhrase)
            self._completer.popup().setCurrentIndex(  # QCompleter.popup().setCurrentIndex 设置选中项
                self._completer.completionModel().index(0,
                                                        0))  # QCompleter.completionModel() 返回QCompleter模型。 QCompleter模型是一个只读列表模型，它包含当前QCompleter前缀的所有可能匹配项。

        cr = self.cursorRect()
        # 设置 completer 尺寸
        cr.setWidth(self._completer.popup().sizeHintForColumn(
            0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)
