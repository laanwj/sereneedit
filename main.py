#!/usr/bin/python
"""
Simple rich text editor based on QT4 QTextEdit and
http://doc.trolltech.com/4.5/demos-textedit.html
(C) W. J. van der Laan 2009

SereneEdit

I just wanted a simple editor in which I can use colors and simple markup
for implementation notes, to-do lists, and so on.

TODO:
- delete/manage custom styles
- detect changed configuration file and auto-reload
  rebuild custom styles list
- move configuration file stuff to separate file
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from textedit import TextEdit
import sys

if __name__=="__main__":
    a = QApplication(sys.argv)
    mw = TextEdit()

    # Set some defaults
    mw.setDefaults(QColor(0xC0,0xC0,0xC0),QColor(0,0,0),"Monospace",9)
    mw.resize( 700, 800 )
    
    mw.show()
    a.exec_()
