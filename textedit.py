"""
Simple rich text editor based on QT4 QTextEdit and
http://doc.trolltech.com/4.5/demos-textedit.html
(C) W. J. van der Laan 2009
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import resources
from CustomStyles import CustomStyles 


# TODO: printing; don't care about that for now

def tr(s):
    """Translate string"""
    return s

rsrcPath = ":/images/win"
TITLE = tr("SereneEdit")

import os

# TODO move these to separate implementation file
def config_file():
    return os.path.join(os.getenv("HOME"), ".sereneedit")

def load_config():
    global customStyles
    cfgfile = config_file()
    try:
        import cPickle as pickle
        f = open(cfgfile,"rb")
        customStyles = pickle.load(f)
        f.close()
    except Exception,e:
        print "Error loading ",cfgfile, " assuming an empty file"

def save_config():
    cfgfile = config_file()
    global customStyles
    try:
        import cPickle as pickle
        f = open(cfgfile,"wb")
        pickle.dump(customStyles, f, -1)
        f.close()
    except Exception,e:
        print "Error writing ",cfgfile
        print e

customStyles = CustomStyles()
load_config()

class TextEdit(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupFileActions()
        self.setupEditActions()
        self.setupTextActions()
        self.setupFindBar()
                
        self.helpMenu = QMenu(tr("Help"), self)
        self.menuBar().addMenu(self.helpMenu)
        self.helpMenu.addAction(tr("About"), self.about)
        
        self.textEdit = QTextEdit(self)
        
        self.connect(self.textEdit, SIGNAL("currentCharFormatChanged(const QTextCharFormat &)"), self.currentCharFormatChanged)
        self.connect(self.textEdit, SIGNAL("cursorPositionChanged()"), self.cursorPositionChanged)
        
        # Set central widget etc
        self.setCentralWidget(self.textEdit)
        self.textEdit.setFocus()
        self.setCurrentFileName(QString())
        
        # Call own change notifiers
        self.fontChanged(self.textEdit.font())
        self.colorChanged(self.textEdit.textColor())
        self.colorChanged(self.textEdit.textBackgroundColor())
        self.alignmentChanged(self.textEdit.alignment())
        
        # Connect document signals
        doc = self.textEdit.document()
        self.connect(doc, SIGNAL("modificationChanged(bool)"), self.actionSave, SLOT("setEnabled(bool)"))
        self.connect(doc, SIGNAL("modificationChanged(bool)"), self.setWindowModified)
        self.connect(doc, SIGNAL("undoAvailable(bool)"), self.actionUndo, SLOT("setEnabled(bool)"))
        self.connect(doc, SIGNAL("redoAvailable(bool)"), self.actionRedo, SLOT("setEnabled(bool)"))
        
        # Initial values
        self.setWindowModified(doc.isModified())
        self.actionSave.setEnabled(doc.isModified())
        self.actionUndo.setEnabled(doc.isUndoAvailable())
        self.actionRedo.setEnabled(doc.isRedoAvailable())
        
        # Undo and redo
        self.connect(self.actionUndo, SIGNAL("triggered()"), self.textEdit, SLOT("undo()"))
        self.connect(self.actionRedo, SIGNAL("triggered()"), self.textEdit, SLOT("redo()"))
        
        # Copy/paste
        self.actionCut.setEnabled(False)
        self.actionCopy.setEnabled(False)
        self.connect(self.actionCut, SIGNAL("triggered()"), self.textEdit, SLOT("cut()"))
        self.connect(self.actionCopy, SIGNAL("triggered()"), self.textEdit, SLOT("copy()"))
        self.connect(self.actionPaste, SIGNAL("triggered()"), self.textEdit, SLOT("paste()"))
        self.connect(self.actionFind, SIGNAL("triggered()"), self.textFind)
        self.connect(self.textEdit, SIGNAL("copyAvailable(bool)"), self.actionCut, SLOT("setEnabled(bool)"))
        self.connect(self.textEdit, SIGNAL("copyAvailable(bool)"), self.actionCopy, SLOT("setEnabled(bool)"))
        self.connect(QApplication.clipboard(), SIGNAL("dataChanged()"), self.clipboardDataChanged)
        


        # Load initial file
        #initialFile = ":/example.html"
        initialFile = None
        args = QCoreApplication.arguments()
        if args.count() == 2:
            initialFile = args[1]
        if initialFile is None or not self.load(initialFile):
            self.fileNew()
            
            
    def closeEvent(self, e):
        if self.maybeSave():
            e.accept()
        else:
            e.ignore()
        
    def maybeSave(self):
        if not self.textEdit.document().isModified():
            return True
        if self.fileName.startsWith(QLatin1String(":/")):
            return True
        ret = QMessageBox.warning(self, tr("Application"),
                                   tr("The document has been modified.\n"
                                      "Do you want to save your changes?"),
                                   QMessageBox.Save | QMessageBox.Discard
                                   | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            return self.fileSave()
        elif ret == QMessageBox.Cancel:
            return False
        return True
        
    def setCurrentFileName(self, fileName):
        self.fileName = QString(fileName)
        self.textEdit.document().setModified(False)

        self.setWindowModified(False)

    def setWindowModified(self, modified):
        self.updateTitle()
        
    def updateTitle(self):
        if self.fileName.isEmpty():
            shownName = "Untitled document"
        else:
            shownName = QFileInfo(self.fileName).fileName()
        if self.textEdit.document().isModified():
            shownName += "*"

        self.setWindowTitle("%s - %s" % (shownName, TITLE))    

    def setupFileActions(self):
        tb = QToolBar(self)
        tb.setWindowTitle(tr("File Actions"))
        self.addToolBar(tb)
        
        menu = QMenu(tr("File"), self)
        self.menuBar().addMenu(menu)
        
        a = QAction(QIcon(rsrcPath + "/filenew.png"), tr("&New"), self)
        a.setShortcut(QKeySequence.New)
        self.connect(a, SIGNAL("triggered()"), self.fileNew)
        tb.addAction(a)
        menu.addAction(a)

        a = QAction(QIcon(rsrcPath + "/fileopen.png"), tr("&Open..."), self)
        a.setShortcut(QKeySequence.Open)
        self.connect(a, SIGNAL("triggered()"), self.fileOpen)
        tb.addAction(a)
        menu.addAction(a)

        menu.addSeparator()

        a = QAction(QIcon(rsrcPath + "/filesave.png"), tr("&Save"), self)
        self.actionSave = a
        a.setShortcut(QKeySequence.Save)
        self.connect(a, SIGNAL("triggered()"), self.fileSave)
        a.setEnabled(False)
        tb.addAction(a)
        menu.addAction(a)

        a = QAction(tr("Save &As..."), self)
        self.connect(a, SIGNAL("triggered()"), self.fileSaveAs)
        menu.addAction(a)
        menu.addSeparator()

        a = QAction(tr("&Quit"), self)
        a.setShortcut(Qt.CTRL + Qt.Key_Q)
        self.connect(a, SIGNAL("triggered()"), self.close)
        menu.addAction(a)

    def setupEditActions(self):
        tb = QToolBar(self)
        tb.setWindowTitle(tr("Edit Actions"))
        self.addToolBar(tb)

        menu = QMenu(tr("&Edit"), self)
        self.menuBar().addMenu(menu)

        a = self.actionUndo = QAction(QIcon(rsrcPath + "/editundo.png"), tr("&Undo"), self)
        a.setShortcut(QKeySequence.Undo)
        tb.addAction(a)
        menu.addAction(a)
        a = self.actionRedo = QAction(QIcon(rsrcPath + "/editredo.png"), tr("&Redo"), self)
        a.setShortcut(QKeySequence.Redo)
        tb.addAction(a)
        menu.addAction(a)
        menu.addSeparator()
        a = self.actionCut = QAction(QIcon(rsrcPath + "/editcut.png"), tr("Cu&t"), self)
        a.setShortcut(QKeySequence.Cut)
        tb.addAction(a)
        menu.addAction(a)
        a = self.actionCopy = QAction(QIcon(rsrcPath + "/editcopy.png"), tr("&Copy"), self)
        a.setShortcut(QKeySequence.Copy)
        tb.addAction(a)
        menu.addAction(a)
        a = self.actionPaste = QAction(QIcon(rsrcPath + "/editpaste.png"), tr("&Paste"), self)
        a.setShortcut(QKeySequence.Paste)
        tb.addAction(a)
        menu.addAction(a)
        self.actionPaste.setEnabled(not QApplication.clipboard().text().isEmpty())
        
        menu.addSeparator()
        
        a = self.actionFind = QAction(QIcon(), tr("&Find"), self)
        a.setShortcut(Qt.CTRL + Qt.Key_F)
        tb.addAction(a)
        menu.addAction(a)
        

    def setupTextActions(self):
        tb = QToolBar(self)
        tb.setWindowTitle(tr("Format Actions"))
        self.addToolBar(tb)

        menu = QMenu(tr("F&ormat"), self)
        self.menuBar().addMenu(menu)
        
        self.actionTextClear = QAction(QIcon(rsrcPath + "/textclear.png"), tr("&Clear formatting"), self)
        #self.actionTextBold.setShortcut(Qt.CTRL + Qt.Key_B)
        self.connect(self.actionTextClear, SIGNAL("triggered()"), self.clearFormatting)
        tb.addAction(self.actionTextClear)
        menu.addAction(self.actionTextClear)

        self.actionTextBold = QAction(QIcon(rsrcPath + "/textbold.png"), tr("&Bold"), self)
        self.actionTextBold.setShortcut(Qt.CTRL + Qt.Key_B)
        bold = QFont()
        bold.setBold(True)
        self.actionTextBold.setFont(bold)
        self.connect(self.actionTextBold, SIGNAL("triggered()"), self.textBold)
        tb.addAction(self.actionTextBold)
        menu.addAction(self.actionTextBold)
        self.actionTextBold.setCheckable(True)

        self.actionTextItalic = QAction(QIcon(rsrcPath + "/textitalic.png"), tr("&Italic"), self)
        self.actionTextItalic.setShortcut(Qt.CTRL + Qt.Key_I)
        italic = QFont()
        italic.setItalic(True)
        self.actionTextItalic.setFont(italic)
        self.connect(self.actionTextItalic, SIGNAL("triggered()"), self.textItalic)
        tb.addAction(self.actionTextItalic)
        menu.addAction(self.actionTextItalic)
        self.actionTextItalic.setCheckable(True)

        self.actionTextUnderline = QAction(QIcon(rsrcPath + "/textunder.png"), tr("&Underline"), self);
        self.actionTextUnderline.setShortcut(Qt.CTRL + Qt.Key_U)
        underline = QFont()
        underline.setUnderline(True)
        self.actionTextUnderline.setFont(underline)
        self.connect(self.actionTextUnderline, SIGNAL("triggered()"), self.textUnderline)
        tb.addAction(self.actionTextUnderline)
        menu.addAction(self.actionTextUnderline)
        self.actionTextUnderline.setCheckable(True)

        menu.addSeparator()

        grp = QActionGroup(self)
        self.connect(grp, SIGNAL("triggered(QAction *)"), self.textAlign)

        # Make sure the alignLeft  is always left of the alignRight
        if QApplication.isLeftToRight():
            self.actionAlignLeft = QAction(QIcon(rsrcPath + "/textleft.png"), tr("&Left"), grp)
            self.actionAlignCenter = QAction(QIcon(rsrcPath + "/textcenter.png"), tr("C&enter"), grp)
            self.actionAlignRight = QAction(QIcon(rsrcPath + "/textright.png"), tr("&Right"), grp)
        else:
            self.actionAlignRight = QAction(QIcon(rsrcPath + "/textright.png"), tr("&Right"), grp)
            self.actionAlignCenter = QAction(QIcon(rsrcPath + "/textcenter.png"), tr("C&enter"), grp)
            self.actionAlignLeft = QAction(QIcon(rsrcPath + "/textleft.png"), tr("&Left"), grp)
        self.actionAlignJustify = QAction(QIcon(rsrcPath + "/textjustify.png"), tr("&Justify"), grp)

        self.actionAlignLeft.setShortcut(Qt.CTRL + Qt.Key_L)
        self.actionAlignLeft.setCheckable(True)
        self.actionAlignCenter.setShortcut(Qt.CTRL + Qt.Key_E)
        self.actionAlignCenter.setCheckable(True)
        self.actionAlignRight.setShortcut(Qt.CTRL + Qt.Key_R)
        self.actionAlignRight.setCheckable(True)
        self.actionAlignJustify.setShortcut(Qt.CTRL + Qt.Key_J)
        self.actionAlignJustify.setCheckable(True)

        tb.addActions(grp.actions())
        menu.addActions(grp.actions())

        menu.addSeparator()

        pix = QPixmap(16, 16)
        pix.fill(Qt.black)
        self.actionTextColor = QAction(QIcon(pix), tr("&Foreground color..."), self)
        self.actionTextColor.setShortcut(Qt.ALT + Qt.Key_X)
        self.connect(self.actionTextColor, SIGNAL("triggered()"), self.textColor)
        tb.addAction(self.actionTextColor)
        menu.addAction(self.actionTextColor)

        pix = QPixmap(16, 16)
        pix.fill(Qt.black)
        self.actionBackgroundColor = QAction(QIcon(pix), tr("&Background color..."), self)
        self.actionBackgroundColor.setShortcut(Qt.ALT + Qt.Key_Z)
        self.connect(self.actionBackgroundColor, SIGNAL("triggered()"), self.backgroundColor)
        tb.addAction(self.actionBackgroundColor)
        menu.addAction(self.actionBackgroundColor)


        tb = QToolBar(self)
        tb.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tb.setWindowTitle(tr("Format Actions"))
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(tb)

        self.comboStyle = QComboBox(tb)
        tb.addWidget(self.comboStyle)
        self.comboStyle.addItem("Standard")
        self.comboStyle.addItem("Bullet List (Disc)")
        self.comboStyle.addItem("Bullet List (Circle)")
        self.comboStyle.addItem("Bullet List (Square)")
        self.comboStyle.addItem("Ordered List (Decimal)")
        self.comboStyle.addItem("Ordered List (Alpha lower)")
        self.comboStyle.addItem("Ordered List (Alpha upper)")
        self.connect(self.comboStyle, SIGNAL("activated(int)"), self.textStyle)

        self.comboFont = QFontComboBox(tb)
        tb.addWidget(self.comboFont)
        self.connect(self.comboFont, SIGNAL("activated(const QString &)"), self.textFamily)

        self.comboSize = QComboBox(tb)
        self.comboSize.setObjectName("comboSize")
        tb.addWidget(self.comboSize)
        self.comboSize.setEditable(True)

        db = QFontDatabase()
        for size in db.standardSizes():
            self.comboSize.addItem(QString.number(size))

        self.connect(self.comboSize, SIGNAL("activated(const QString &)"), self.textSize)
        self.comboSize.setCurrentIndex(self.comboSize.findText(QString.number(QApplication.font().pointSize())))
        
        # Custom style
        tb = QToolBar(self)
        tb.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tb.setWindowTitle(tr("Custom style"))
        self.addToolBar(tb)
        
        self.comboCustomStyle = QComboBox(tb)        
        #self.comboCustomStyle.setWidth(300) TODO
        tb.addWidget(self.comboCustomStyle)
        self.buildCustomStyleMenu()
        
        self.connect(self.comboCustomStyle, SIGNAL("activated(int)"), self.textCustomStyle)

        self.actionNewStyle = QAction(QIcon(), tr("New..."), self)
        self.connect(self.actionNewStyle, SIGNAL("triggered()"), self.newCustomStyle)
        tb.addAction(self.actionNewStyle)
        
    # File loading etc
    def load(self, f):
        if not QFile.exists(f):
             return False
        file = QFile(f)
        if not file.open(QFile.ReadOnly):
            return False

        data = file.readAll()
        codec = QTextCodec.codecForHtml(data)
        str = codec.toUnicode(data)
        if Qt.mightBeRichText(str):
            self.textEdit.setHtml(str)
        else:
            str = QString.fromLocal8Bit(data)
            self.textEdit.setPlainText(str)
        self.setCurrentFileName(f)
        return True
    def fileNew(self):
        if self.maybeSave():
            self.textEdit.clear()
            self.clearFormatting()
            self.setCurrentFileName("")
    def fileOpen(self):
        fn = QFileDialog.getOpenFileName(self, tr("Open File..."),
                                                       QString(), tr("HTML-Files (*.htm *.html);;All Files (*)"))
        if not fn.isEmpty():
            self.load(fn)
    def fileSave(self):
        if self.fileName.isEmpty():
           return self.fileSaveAs()

        writer = QTextDocumentWriter(self.fileName, "html")
        success = writer.write(self.textEdit.document())
        if success:
            self.textEdit.document().setModified(False)
        return success

    def fileSaveAs(self):
        fn = QFileDialog.getSaveFileName(self, tr("Save as..."),
                                               QString(), tr("HTML-Files (*.htm *.html);;All Files (*)"))
        # ODF files (*.odt);; ?? don't care about these for now
        if fn.isEmpty():
            return False
        #if not (fn.endsWith(".odt", Qt.CaseInsensitive) or fn.endsWith(".htm", Qt.CaseInsensitive) or fn.endsWith(".html", Qt.CaseInsensitive)):
        #    fn += ".html"
        self.setCurrentFileName(fn)
        return self.fileSave()

    # Slots
    def about(self):
        QMessageBox.about(self, tr("About"), tr("Simple rich text editor for making notes\n(C) W. J. van der Laan 2009"))
 
    def currentCharFormatChanged(self, format):
        self.fontChanged(format.font())
        self.colorChanged(format.foreground().color())
        self.backgroundChanged(format.background().color())

        fmt = self.comboCustomStyle.itemData(self.comboCustomStyle.currentIndex())
        fmt = fmt.toPyObject()
        if fmt is not None and format != fmt:
            # Not the currently selected style, revert
            self.comboCustomStyle.setCurrentIndex(0)
        
    def cursorPositionChanged(self):
        self.alignmentChanged(self.textEdit.alignment())

    def fontChanged(self, f):
        self.comboFont.setCurrentIndex(self.comboFont.findText(QFontInfo(f).family()))
        self.comboSize.setCurrentIndex(self.comboSize.findText(QString.number(f.pointSize())))
        self.actionTextBold.setChecked(f.bold())
        self.actionTextItalic.setChecked(f.italic())
        self.actionTextUnderline.setChecked(f.underline())

    def colorChanged(self, color):
        pix = QPixmap(16, 16)
        pix.fill(color)
        self.actionTextColor.setIcon(QIcon(pix))

    def backgroundChanged(self, color):
        pix = QPixmap(16, 16)
        pix.fill(color)
        self.actionBackgroundColor.setIcon(QIcon(pix))

    def alignmentChanged(self, a):
        if (a & Qt.AlignLeft):
            self.actionAlignLeft.setChecked(True)
        elif (a & Qt.AlignHCenter):
            self.actionAlignCenter.setChecked(True)
        elif (a & Qt.AlignRight):
            self.actionAlignRight.setChecked(True)
        elif (a & Qt.AlignJustify):
            self.actionAlignJustify.setChecked(True)

    def clipboardDataChanged(self):
        self.actionPaste.setEnabled(not QApplication.clipboard().text().isEmpty())
    #
    def textBold(self):
        fmt = QTextCharFormat()
        if self.actionTextBold.isChecked():
            fmt.setFontWeight(QFont.Bold)
        else:
            fmt.setFontWeight(QFont.Normal)
        self.mergeFormatOnWordOrSelection(fmt)

    def textItalic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.actionTextItalic.isChecked())
        self.mergeFormatOnWordOrSelection(fmt)

    def textUnderline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.actionTextUnderline.isChecked())
        self.mergeFormatOnWordOrSelection(fmt)
        
    def textAlign(self, a):
        if a == self.actionAlignLeft:
            self.textEdit.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)
        elif a == self.actionAlignCenter:
            self.textEdit.setAlignment(Qt.AlignHCenter)
        elif a == self.actionAlignRight:
            self.textEdit.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        elif a == self.actionAlignJustify:
            self.textEdit.setAlignment(Qt.AlignJustify)

    def textColor(self):
        col = QColorDialog.getColor(self.textEdit.textColor(), self)
        if not col.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setForeground(col)
        self.mergeFormatOnWordOrSelection(fmt)
        self.colorChanged(col)

    def backgroundColor(self):
        col = QColorDialog.getColor(self.textEdit.textColor(), self)
        if not col.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setBackground(col)
        self.mergeFormatOnWordOrSelection(fmt)
        self.backgroundChanged(col)

    def textStyle(self, styleIndex):
        cursor = self.textEdit.textCursor()

        if styleIndex != 0:
            styles = [QTextListFormat.ListDisc,
                      QTextListFormat.ListCircle,
                      QTextListFormat.ListSquare,
                      QTextListFormat.ListDecimal,
                      QTextListFormat.ListLowerAlpha,
                      QTextListFormat.ListUpperAlpha
                      ]
            style = styles[styleIndex-1]
            
            cursor.beginEditBlock()

            blockFmt = cursor.blockFormat()
            listFmt = QTextListFormat()
            if cursor.currentList():
                listFmt = cursor.currentList().format()
            else:
                listFmt.setIndent(blockFmt.indent() + 1)
                blockFmt.setIndent(0)
                cursor.setBlockFormat(blockFmt)

            listFmt.setStyle(style)
            cursor.createList(listFmt)
            cursor.endEditBlock()
        else:
            #### TODO
            bfmt = QTextBlockFormat()
            bfmt.setObjectIndex(-1)
            cursor.mergeBlockFormat(bfmt)

    def textFamily(self, family):
        fmt = QTextCharFormat()
        fmt.setFontFamily(family)
        self.mergeFormatOnWordOrSelection(fmt)
                
    def textSize(self, size):
        try:
            size = float(size)
        except ValueError:
            size = 0
        if size > 0:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)
            self.mergeFormatOnWordOrSelection(fmt)

    def mergeFormatOnWordOrSelection(self, format):
       #cursor = self.textEdit.textCursor()
       #if not cursor.hasSelection():
       #    cursor.select(QTextCursor.WordUnderCursor)
       #cursor.mergeCharFormat(format)
       self.textEdit.mergeCurrentCharFormat(format)
       #self.textEdit.setCurrentCharFormat(format)

    def setDefaults(self, fg, bg, font, fontsize):
        p = self.textEdit.palette()
        p.setColor(QPalette.Text, fg)
        p.setColor(QPalette.Base, bg)
        self.textEdit.setPalette(p)
        self.comboCustomStyle.setPalette(p)

        fnt = QFont(font)
        fnt.setPointSize(fontsize)
        self.textEdit.document().setDefaultFont(fnt)
        self.textEdit.setCurrentFont(fnt)

    def clearFormatting(self):
        format = QTextCharFormat()
        self.textEdit.setCurrentCharFormat(format)
        
    def buildCustomStyleMenu(self):
        # TODO Should do this using a custom model, but heh, this is so simple
        self.comboCustomStyle.clear()
        self.comboCustomStyle.addItem("[None]")
        idx = 1
        for (name, fmt) in customStyles:
            self.comboCustomStyle.addItem(name)
            self.comboCustomStyle.setItemData(idx, fmt.background(), Qt.BackgroundRole)
            self.comboCustomStyle.setItemData(idx, fmt.font(), Qt.FontRole)
            self.comboCustomStyle.setItemData(idx, fmt.foreground(), Qt.ForegroundRole)
            self.comboCustomStyle.setItemData(idx, fmt, Qt.UserRole)
            idx += 1
        
    def textCustomStyle(self, s):
        if s != 0:
            fmt = self.comboCustomStyle.itemData(s)
            fmt = fmt.toPyObject()
            self.textEdit.setCurrentCharFormat(fmt)
            self.textEdit.setFocus()

    def newCustomStyle(self):
        # Ask for name (and ok/cancel)
        text,ok = QInputDialog.getText(self, TITLE, "Enter name for new custom style")
        if ok and not text.isEmpty():
            # then add to customStyles[...] using given name
            fmt = self.textEdit.currentCharFormat()
            customStyles.add_style(str(text),fmt)
            self.buildCustomStyleMenu()
            # Save altered configuration
            save_config()

    def setupFindBar(self):
        tb = self.findBar = QToolBar(self)
        tb.setWindowTitle(tr("Find..."))
        tb.setAllowedAreas(Qt.BottomToolBarArea)
        self.addToolBar(Qt.BottomToolBarArea, tb)
        tb.hide()

        w = QLabel("Find: ", self)
        tb.addWidget(w)
        
        w = self.findEdit = QLineEdit(self)
        self.connect(w, SIGNAL("returnPressed()"), self.findForward)
        tb.addWidget(w)
        
        a = QAction(QIcon(), tr("&Previous"), self)
        #a.setShortcut(Qt.ALT + Qt.Key_Z)
        self.connect(a, SIGNAL("triggered()"), self.findBackward)
        tb.addAction(a)

        a =  QAction(QIcon(), tr("&Next"), self)
        a.setShortcut(Qt.CTRL + Qt.Key_G)
        self.connect(a, SIGNAL("triggered()"), self.findForward)
        tb.addAction(a)
        
        a = self.findCase = QAction(QIcon(), tr("Mat&ch case"), self)
        #a.setShortcut(Qt.CTRL + Qt.Key_G)
        a.setCheckable(True)
        tb.addAction(a)
        
        s = QShortcut(Qt.Key_Escape, self.findEdit, self.closeFind, self.closeFind, Qt.WidgetShortcut)
        
    def closeFind(self):
        self.findBar.setVisible(False)

    def textFind(self):
        """Toggle find bar visibility"""
        self.findBar.setVisible(True)
        self.findEdit.setSelection(0, len(self.findEdit.text()))
        self.findEdit.setFocus()
        
    def findText(self, text, flags):
        if len(text)==0:
            return
        if self.findCase.isChecked():
            flags += QTextDocument.FindCaseSensitively
        self.textEdit.find(text, flags)
    
    def findForward(self):
        self.findText(self.findEdit.text(), QTextDocument.FindFlags())

    def findBackward(self):
        self.findText(self.findEdit.text(), QTextDocument.FindBackward)
        
