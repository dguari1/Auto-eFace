# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 22:44:03 2017

@author: diego
"""

import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets


class TestListView(QtWidgets.QListWidget):
    
    dropped = QtCore.pyqtSignal(list)
    
    def __init__(self, type, parent=None):
        super(TestListView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(72, 72))
        
        

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
            

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.dropped.emit(links)
            #self.emit(QtCore.SIGNAL("dropped"), links)
        else:
            event.ignore()

class MainForm(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.view = TestListView(self)
        self.view.dropped.connect(self.pictureDropped)
        #self.connect(self.view, QtCore.SIGNAL("dropped"), self.pictureDropped)
        self.setCentralWidget(self.view)

    def pictureDropped(self, l):
        for url in l:
            if os.path.exists(url):
                print(url)                
                icon = QtGui.QIcon(url)
                pixmap = icon.pixmap(72, 72)                
                icon = QtGui.QIcon(pixmap)
                item = QtWidgets.QListWidgetItem(url, self.view)
                item.setIcon(icon)        
                #item.setStatusTip(url)   
                
                

def main():
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    form = MainForm()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()