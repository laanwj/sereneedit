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
- Show style palette when pressing CTRL
- Links, ancohors (see kjots)
  - Multiple pages, hyperlinks
  - Anchors/labels
    http://qt.nokia.com/doc/4.6/qtextedit.html#anchorAt
    QTextEdit::scrollToAnchor
    http://doc.trolltech.com/4.6/qtextcursor.html
    http://doc.trolltech.com/4.6/qtextdocumentfragment.html
    http://doc.trolltech.com/4.6/qtextformat.html
      Insert format with:
      QTextFormat::IsAnchor	0x2030
      QTextFormat::AnchorHref	0x2031	 
      QTextFormat::AnchorName	0x2032	 
    http://doc.trolltech.com/4.6/qtextcharformat.html#isAnchor

- Paste special (without formatting)

- Bullets / indentation (see kjots)
  Is already possible, but I want ident right/left icons
    http://lists.kde.org/?l=kde-pim&m=120649844920238&w=2
    QTextBlockFormat::indent () 

- Sometimes, space between line appears when copy/pasting from HTML. What is this, paragraph mode?
  - BlockFormat?
  - need a way to clear BlockFOrmat too

- Simple synchronisation between multiple instances (if style file changes, reload, must be easily possible with qt4)

- Position independent links/anchors: 
  - If text is moved, links should still be able to find the document
  - Global database index? [anchor id]->[subdocument]
    [subdocument contains position of anchors]
    anchor id must be globally unique
    +additional name/description
  - Anchor ID should uniquely identify a certain piece of information
    everywhere.
  - ANchors must be visible object in text

See also other outlining software:
- kjots (can get icons from here)
- WIXI
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from textedit import TextEdit
import sys

if __name__=="__main__":
    a = QApplication(sys.argv)
    mw = TextEdit()

    # Set some defaults
    mw.setDefaults(QColor(0xC0,0xC0,0xC0),QColor(0x10,0x10,0x10),"Monospace",9)
    mw.resize( 700, 800 )
    
    mw.show()
    a.exec_()

