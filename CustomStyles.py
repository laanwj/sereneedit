"""Pickle-able list of Qt character styles"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class CustomStyles(object):
    """Pickle-able list of Qt character styles"""
    def __init__(self):
        self.styles = []

    def _to_bytes(self, fmt):
        """QTextCharFormat to bytes"""
        ba = QByteArray()
        out = QDataStream(ba, QIODevice.WriteOnly)
        m = fmt.properties()
        for (key, value) in m.iteritems():
            QVariant(key).save(out)        
            value.save(out)          
        return ba.data()

    def _to_style(self, data):
        """bytes to QTextCharFormat"""
        fmt = QTextCharFormat()
        ba = QByteArray(data)
        in_ = QDataStream(ba, QIODevice.ReadOnly)

        while not in_.atEnd():
            key = QVariant()
            key.load(in_)
            key = key.toInt()[0]
            value = QVariant()
            value.load(in_)
            #print key,value.toPyObject()
            fmt.setProperty(key, value)
        return fmt
        
    def add_style(self, name, fmt):
        self.styles.append([name,fmt])

    def __getstate__(self):
        data = []
        for (name, fmt) in self.styles:
            data.append([name, self._to_bytes(fmt)])
        return data
        
    def __setstate__(self, data):
        self.styles = []
        for (name, fmt) in data:
            self.styles.append([name, self._to_style(fmt)])
            
    def __iter__(self):
        return self.styles.__iter__()

