# -*- coding: utf-8 -*-
import os
import sys

from PySide import QtCore, QtGui
from PySide.QtUiTools import QUiLoader

from serial import Serial
from serial.tools import list_ports

from datetime import datetime
import binascii
from time import sleep

#----------------------------------------------------------------------------
## GUIを作るクラス
class GUI(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)
        loader = QUiLoader()
        self.UI = loader.load('TPui.ui')
        self.setCentralWidget(self.UI)
        self.resize(736, 460)
        self.setWindowTitle("Throw Parame Update Ver_0.1")
        # コンボボックスに値をセット
        self.ports = list_ports.comports()	# ポートデータを取得しクラス変数に入れる
        self.setComPortName()
        # UI要素にシグナルを追加
        self.setSignals()

        # 結果表示と保存用変数
        self.result_array = []
        self.result_num = 1

        # TZ選択
        self.UI.tz.addItems(['TZ1', 'TZ2', 'TZ3'])
        # シャトルコック選択
        #self.UI.shuttle.addItems([u'マルコック(ストロー', u'中国版マルコック', u'涙滴型'])
        self.UI.shuttle.addItems(['STRAW_MARU', 'CHINA_MARU', 'RUITEKI'])

    ## シグナルの登録
    def setSignals(self):
        self.UI.serial_start.clicked.connect(self.serialStart)
        self.UI.param_update.clicked.connect(self.paramUpdate)

        self.UI.next_status.clicked.connect(self.enterNextStatus)
        self.UI.initialize.clicked.connect(self.initStatus)

        self.UI.result_in.clicked.connect(self.resultOK)
        self.UI.result_hoge.clicked.connect(self.resultHoge)
        self.UI.result_dame.clicked.connect(self.resultDame)
        self.UI.result_back.clicked.connect(self.resultBack)
        self.UI.result_el.clicked.connect(self.resultClear)
        self.UI.result_save.clicked.connect(self.resultSave)

        self.UI.param_update.setEnabled(False)
        self.UI.param_get.setEnabled(False)
        self.UI.next_status.setEnabled(False)
        self.UI.initialize.setEnabled(False)

    def setComPortName(self):
        #COMポート
        ports_list = []
        #デバイス名に日本語があるとユニコードエラーが起こる。暇なとき解決しよう
        for port in self.ports:
            ports_list.append(str(port.device))

        self.UI.com_port.addItems(ports_list)
        #ボーレート
        self.UI.baud_rate.addItems(['9600', '115200'])

    def serialStart(self):
        port = self.ports[self.UI.com_port.currentIndex()].device
        baudrate = self.UI.baud_rate.currentText()

        try:
            self.com = Serial(
                port=port,
                baudrate=baudrate,
            )
            print ("Succeed open COM port!")
            self.UartTx = uartTx(self.com)

            self.UI.param_update.setEnabled(True)
            self.UI.next_status.setEnabled(True)
            self.UI.initialize.setEnabled(True)

        except:
            print ("Failed to open COM port!")

    # PARAMETER用メソッド
    def paramUpdate(self):
        self.UartTx.ServoStart(self.UI.box_servo_start.value())
        self.UartTx.MotorSlow(self.UI.box_motor_slow.value())
        self.UartTx.MotorThrow(self.UI.box_motor_throw.value())
        self.UartTx.EncSlow(self.UI.box_enc_slow.value())
        self.UartTx.EncAccel(self.UI.box_enc_accel.value())
        self.UartTx.EncRelease(self.UI.box_enc_release.value())

    def enterNextStatus(self):
        self.UartTx.nextStatus()

    def initStatus(self):
        self.UartTx.initializeStatus()

    # result用メソッド
    def resultOK(self):
        self.UI.result_list.addItem(str(self.result_num) + u"回目  〇")
        self.result_num += 1
        self.result_array.append(0)
    def resultHoge(self):
        self.UI.result_list.addItem(str(self.result_num) + u"回目  △")
        self.result_num += 1
        self.result_array.append(1)
    def resultDame(self):
        self.UI.result_list.addItem(str(self.result_num) + u"回目  ✖")
        self.result_num += 1
        self.result_array.append(2)
    def resultClear(self):
        self.UI.result_list.clear()
        self.result_num = 1
        self.result_array = []
    def resultBack(self):
        if self.result_num > 1:
            self.result_num -= 1
            self.result_array.pop()
            self.UI.result_list.clear()
            tmp = 0
            for i in self.result_array:
                tmp += 1
                if i == 0:
                    self.UI.result_list.addItem(str(tmp) + u"回目  〇")
                if i == 1:
                    self.UI.result_list.addItem(str(tmp) + u"回目  △")
                if i == 2:
                    self.UI.result_list.addItem(str(tmp) + u"回目  ✖")
    def resultSave(self): #パラメータと投擲結果を保存するメソッド
        str0 = self.UI.tz.currentText() + ',' + self.UI.shuttle.currentText()
        """
        str1 = "\nPV.byte.servo_wait_pos = 6650"
        str2 = "\nPV.byte.servo_start_pos = " + str(self.UI.box_servo_start.value() )
        str3 = "\nPV.byte.slow_throw_motor_output = " + str(self.UI.box_motor_slow.value())
        str4 = "\nPV.byte.throw_motor_output = " + str(self.UI.box_motor_throw.value())
        str5 = "\nTV.byte.slow_throw_enc_pos = " + str(self.UI.box_enc_slow.value())
        str6 = "\nTV.byte.release_enc_pos = " + str(self.UI.box_enc_accel.value())
        str7 = "\nTV.byte.throw_enc_pos = " + str(self.UI.box_enc_release.value())
        str8 = "\n"
        """
        str1 = "\nswp,6650"
        str2 = "\nssp," + str(self.UI.box_servo_start.value() )
        str3 = "\nsto," + str(self.UI.box_motor_slow.value())
        str4 = "\ntmo," + str(self.UI.box_motor_throw.value())
        str5 = "\nste," + str(self.UI.box_enc_slow.value())
        str6 = "\nrep," + str(self.UI.box_enc_accel.value())
        str7 = "\ntep," + str(self.UI.box_enc_release.value())
        str8 = "\n"
        save_strs = [str0, str1, str2, str3, str4, str5, str6, str7]

        tmp_ok = 0
        tmp_hoge = 0
        tmp_dame = 0
        tmp_num = 0
        for i in self.result_array:
            tmp_num += 1
            if i == 0:
                tmp_ok += 1
                #save_strs.append("\n" + str(tmp_num) + "回目  o")
                save_strs.append("\n" + str(tmp_num) + ",o")
            if i == 1:
                tmp_hoge += 1
                #save_strs.append("\n" + str(tmp_num) + "回目  △")
                save_strs.append("\n" + str(tmp_num) + ",△")
            if i == 2:
                tmp_dame += 1
                #save_strs.append("\n" + str(tmp_num) + "回目  x")
                save_strs.append("\n" + str(tmp_num) + ",x")

        #save_strs.append("\n\n" + "o -> " + str(tmp_ok) + "  △ -> " + str(tmp_hoge) + "  x -> " + str(tmp_dame))
        save_strs.append("\n" + str(tmp_ok) + "," + str(tmp_hoge) + "," + str(tmp_dame))
        file_name = datetime.now().strftime("%Y%m%d_%H_%M") + "_" +self.UI.tz.currentText() + ".txt"
        f = open("C:\\Users\\greee\\Desktop\\ThrowParam\\" + file_name, 'w')
        f.writelines(save_strs) # シーケンスが引数。
        f.close()
        self.resultClear()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.enterNextStatus()
        if event.key() == QtCore.Qt.Key_Escape:
            self.initStatus()
        if event.key() == QtCore.Qt.Key_R:
            self.UI.box_servo_start.setValue(self.UI.box_servo_start.value() + 20)
        if event.key() == QtCore.Qt.Key_F:
            self.UI.box_servo_start.setValue(self.UI.box_servo_start.value() - 20)
        if event.key() == QtCore.Qt.Key_T:
            self.UI.box_motor_slow.setValue(self.UI.box_motor_slow.value() + 1)
        if event.key() == QtCore.Qt.Key_G:
            self.UI.box_motor_slow.setValue(self.UI.box_motor_slow.value() - 1)
        if event.key() == QtCore.Qt.Key_Y:
            self.UI.box_motor_throw.setValue(self.UI.box_motor_throw.value() + 1)
        if event.key() == QtCore.Qt.Key_H:
            self.UI.box_motor_throw.setValue(self.UI.box_motor_throw.value() - 1)
        if event.key() == QtCore.Qt.Key_U:
            self.UI.box_enc_slow.setValue(self.UI.box_enc_slow.value() + 10)
        if event.key() == QtCore.Qt.Key_J:
            self.UI.box_enc_slow.setValue(self.UI.box_enc_slow.value() - 10)
        if event.key() == QtCore.Qt.Key_I:
            self.UI.box_enc_accel.setValue(self.UI.box_enc_accel.value() + 10)
        if event.key() == QtCore.Qt.Key_K:
            self.UI.box_enc_accel.setValue(self.UI.box_enc_accel.value() - 10)
        if event.key() == QtCore.Qt.Key_O:
            self.UI.box_enc_release.setValue(self.UI.box_enc_release.value() + 10)
        if event.key() == QtCore.Qt.Key_L:
            self.UI.box_enc_release.setValue(self.UI.box_enc_release.value() - 10)
        if event.key() == QtCore.Qt.Key_Q:
            self.resultOK()
        if event.key() == QtCore.Qt.Key_W:
            self.resultHoge()
        if event.key() == QtCore.Qt.Key_E:
            self.resultDame()
        if event.key() == QtCore.Qt.Key_D:
            self.resultClear()
        if event.key() == QtCore.Qt.Key_A:
            self.resultBack()
        if event.key() == QtCore.Qt.Key_S:
            self.resultSave()

class uartTx():
    def __init__(self, _com):
        self.com = _com

    def ServoStart(self, value):
        tmp = (int)(value / 20)
        self.com.write(binascii.a2b_hex('50'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('51'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('%x' % tmp))
        sleep(0.001)

    def MotorSlow(self, value):
        self.com.write(binascii.a2b_hex('50'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('52'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('%x' % value))
        sleep(0.001)

    def MotorThrow(self, value):
        self.com.write(binascii.a2b_hex('50'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('53'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('%x' % value))
        sleep(0.001)

    def EncSlow(self, value):
        tmp = (int)(value / 10)
        self.com.write(binascii.a2b_hex('50'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('54'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('%x' % tmp))
        sleep(0.001)

    def EncAccel(self, value):
        tmp = (int)(value / 10)
        self.com.write(binascii.a2b_hex('50'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('55'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('%x' % tmp))
        sleep(0.001)

    def EncRelease(self, value):
        tmp = (int)(value / 10)
        self.com.write(binascii.a2b_hex('50'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('56'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('%x' % tmp))
        sleep(0.001)

    def nextStatus(self):
        self.com.write(binascii.a2b_hex('50'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('57'))

    def initializeStatus(self):
        self.com.write(binascii.a2b_hex('50'))
        sleep(0.001)
        self.com.write(binascii.a2b_hex('58'))

## GUIの起動
def main():
    app = QtGui.QApplication(sys.argv)
    app.setStyle('plastique')    # ← ここでスタイルを指定
    ui = GUI()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
