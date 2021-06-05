import os
import subprocess
import time

import cv2

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QIcon, QMovie, QStandardItemModel, QStandardItem
import sys
import signal

recStatus = False


class LiveFeedThread(QThread):
    image_update_signal = pyqtSignal(QImage)

    def run(self):

        print("Live Feed started..")
        stream = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
        while True:
            success, snap = stream.read()
            if not success:
                print("Cam failed")
                break
            else:
                if recStatus == True:
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    out.write(hsv)

                rgb_image = cv2.cvtColor(snap, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_qt_format.scaled(700, 570, Qt.KeepAspectRatio)
                self.image_update_signal.emit(p)

class RecordThread(QThread):
    record_complete_signal = pyqtSignal(bool)

    def run(self):

        subproc = subprocess.Popen(
            "ffmpeg -y -f vfwcap -r 25 -i 0 out.mp4", creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        while window.start_recording:
            time.sleep(1)

        os.kill(subproc.pid, signal.CTRL_BREAK_EVENT)

        self.record_complete_signal.emit(True)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('try.ui', self)
        self.setWindowTitle("Trail App")
        self.imageLabel = self.findChild(QtWidgets.QLabel, 'feed')
        self.start = self.findChild(QtWidgets.QPushButton, 'start')
        self.stop = self.findChild(QtWidgets.QPushButton, 'stop')


        # self.lv = LiveFeedThread(self)
        # self.lv.image_update_signal.connect(self.ImageUpdate)
        # self.lv.start()

        self.start.clicked.connect(self.startFunc)
        self.stop.clicked.connect(self.stopFunc)

        self.rec = RecordThread(self)
        self.rec.record_complete_signal.connect(self.recordComplete)

        self.start_recording = False

        self.show()

    @pyqtSlot(bool)
    def recordComplete(self, data):
        print("record complete")

    def startFunc(self):
        print("Clicked start")
        self.start_recording = True
        self.rec.start()


    def stopFunc(self):
        print("stop clicked")
        self.start_recording = False

    @pyqtSlot(QImage)
    def ImageUpdate(self, image):
        self.imageLabel.setPixmap(QPixmap.fromImage(image))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()