from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from time import sleep
import resources

import sys
from qt_material import apply_stylesheet
import traceback, sys
import serial
import serial.tools.list_ports
import os


if sys.platform == "linux" or sys.platform == "linux2":
    pass

elif sys.platform == "win32":
    import ctypes
    myappid = u'prl.paras2'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

elif sys.platform == "darwin":
    pass

class WorkerSignals(QObject):
    error = pyqtSignal(tuple)
    progress = pyqtSignal(int)
    result = pyqtSignal(object)
    finished = pyqtSignal()
    
class Worker(QRunnable):

    def __init__(self, fn, signals_flag, *args, **kwargs):
        # signals_flag = [progress, result, finished]

        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs    
        self.signals = WorkerSignals()
        self.signals_flag = signals_flag

        if self.signals_flag[0]:
            kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            if self.signals_flag[1]:
                self.signals.result.emit(result) # Return the result of the processing
        finally:
            if self.signals_flag[2]:
                self.signals.finished.emit() # Done

class Ui(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(Ui, self).__init__(*args, **kwargs)

        uic.loadUi('gui.ui', self)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.led_on  = QPixmap(":/leds/images/leds/green.png")
        self.led_off = QPixmap(":/leds/images/leds/off.png")

        self.relays = { 1 : self.lbl_uar_lamp,
                        2 : self.lbl_tung_lamp,
                        3 : self.lbl_star_cvr,
                        4 : self.lbl_cal_cvr,
                        5 : self.lbl_star2_cvr}

        self.ser = None
        self.connect_ser()
        self.ui_settings()
        self.show()

        self.load_settings()

    def closeEvent(self, event):
        # msg_box = QMessageBox.information(self, 'Message', 'Saving Settings!', QMessageBox.Ok)
        
        msg_box = QMessageBox(QMessageBox.Information, "PARAS-2", "Saving Settings!")
        msg_box.show()
        QCoreApplication.processEvents()
        
        self.send_cmd("save_relays")
        self.read_output()
        msg_box.close()
        print("closing")

    def ui_settings(self):

        self.grbbox_ser.setVisible(False)

        # =========================================================================
        #                       Relays
        # =========================================================================
        self.btngrp_relays = QButtonGroup()
        self.btngrp_relays.addButton(self.btn_uar_lamp ,  1)
        self.btngrp_relays.addButton(self.btn_tung_lamp , 2)
        self.btngrp_relays.addButton(self.btn_star_cvr ,  3)
        self.btngrp_relays.addButton(self.btn_cal_cvr ,   4)
        self.btngrp_relays.addButton(self.btn_star2_cvr ,  5)
        self.btngrp_relays.buttonClicked.connect(self.toggle_relay)
        # =========================================================================


        # =========================================================================
        # Select Lamp for Calibration Fiber
        # =========================================================================
        self.btngrp_lamp = QButtonGroup()
        self.btngrp_lamp.addButton(self.btn_uar ,   1)
        self.btngrp_lamp.addButton(self.btn_tung ,  2)
        self.btngrp_lamp.addButton(self.btn_fabry , 3)
        self.btngrp_lamp.buttonClicked.connect(self.select_lamp)
        # =========================================================================


        # =========================================================================
        # Select Speckle Imaging Unit
        # =========================================================================
        self.btngrp_lamp = QButtonGroup()
        self.btngrp_lamp.addButton(self.btn_nonspec ,   1)
        self.btngrp_lamp.addButton(self.btn_spec , 2)
        self.btngrp_lamp.buttonClicked.connect(self.select_speckle)
        # =========================================================================

        # =========================================================================
        #                               ND Filter
        # =========================================================================
        self.spnbx_nd_angle.setValue(46)
        self.spnbx_nd_angle.setHidden(True)

        self.btngrp_nd = QButtonGroup()
        self.btngrp_nd.addButton(self.btn_nd_set ,   1)
        self.btngrp_nd.addButton(self.btn_nd_unset , 2)
        self.btngrp_nd.buttonClicked.connect(self.select_nd_filter)
        # =========================================================================
        
    def toggle_led(self, led, target):
        if led == "resources/icons/off.png":
            target.setPixmap(QPixmap("resources/icons/on.png").scaled(32,32))
            return "resources/icons/on.png"
        else:
            target.setPixmap(QPixmap("resources/icons/off.png").scaled(32,32))
            return "resources/icons/off.png"

            
    
    # +================================================================+
    # |                     Thread  Functions                           |
    # +================================================================+
    def move_servo_thread(self, str_cmd):
        self.send_cmd(str_cmd)
        output = self.read_output()

        print("output: ", output)

        if output == "uar":
            self.lbl_uar.setPixmap(self.led_on)
        if output == "tung":
            self.lbl_tung.setPixmap(self.led_on)
        if output == "fabry":
            self.lbl_fabry.setPixmap(self.led_on)
        
        self.enable_buttons()


    def move_speckle_servo_thread(self, str_cmd):
        self.send_cmd(str_cmd)
        output = self.read_output()

        print("output: ", output)

        if output == "nonspec":
            self.lbl_nonspec.setPixmap(self.led_on)
        if output == "spec":
            self.lbl_spec.setPixmap(self.led_on)
        
        self.enable_buttons()


    def select_nd_filter_thread(self, str_cmd, btn_id):
        self.send_cmd(str_cmd)
        output = self.read_output()

        if btn_id == 1:
            self.lbl_nd_set.setPixmap(self.led_on)
        else:
            self.lbl_nd_unset.setPixmap(self.led_on)

        self.enable_buttons()


    def toggle_relay_thread(self, str_cmd, btn_id):
        self.send_cmd(str_cmd)
        output = int(self.read_output())

        if output == 0:
            self.relays[btn_id].setPixmap(self.led_on)
        else:
            self.relays[btn_id].setPixmap(self.led_off)
        
        self.enable_buttons()

    def load_settings_thread(self):
        self.disable_buttons()
        sleep(2)
        self.send_cmd("status")
        output = self.read_output()
        print("output: ", output)

        self.lbl_uar_lamp.setPixmap(self.led_on)  if output[0] == "0" else None
        self.lbl_tung_lamp.setPixmap(self.led_on) if output[1] == "0" else None
        self.lbl_star_cvr.setPixmap(self.led_on)  if output[2] == "0" else None
        self.lbl_cal_cvr.setPixmap(self.led_on)   if output[3] == "0" else None
        self.lbl_star2_cvr.setPixmap(self.led_on)  if output[4] == "0" else None

        if output[5] == "1":
            self.lbl_nd_set.setPixmap(self.led_on)    
        else:
             self.lbl_nd_unset.setPixmap(self.led_on)

        if output[6] == "1":
            self.lbl_uar.setPixmap(self.led_on)    
        elif output[6] == "2":
             self.lbl_tung.setPixmap(self.led_on)
        else:
             self.lbl_fabry.setPixmap(self.led_on)

        if output[7] == "1":
            self.lbl_nonspec.setPixmap(self.led_on)    
        else:
             self.lbl_spec.setPixmap(self.led_on)

        self.enable_buttons()
    # +================================================================+



    # +================================================================+
    # |                     Serial Functions                           |
    # +================================================================+
    def connect_ser(self):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            print("{}: {} [{}]".format(port, desc, hwid))
            if os.environ["CASSEGRAIN_PORT"] in hwid:
                self.ser = serial.Serial(port, 115200)
                print("Serial connected on: {}".format(port))
    
    def check_serial(self):
        if not self.ser:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("Controller Not Connected!")
            msg_box.setWindowTitle("About")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            return False
        return True

    def send_cmd(self, str_cmd):
        try:
            self.ser.write(str_cmd.encode())
        except:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("Serial Error: Restart Software!")
            msg_box.setWindowTitle("Error!")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            
            self.closeEvent()
    
    def read_output(self):
        # return "done"
        output = self.ser.readline().strip().decode()
        output = output.replace(" ","")
        return output
    # +================================================================+
    

    # +================================================================+
    # |                     Button Functions                           |
    # +================================================================+
    def select_lamp(self, lamp):
        self.disable_buttons()
        self.lbl_uar.setPixmap(self.led_off)
        self.lbl_tung.setPixmap(self.led_off)
        self.lbl_fabry.setPixmap(self.led_off)

        btn_id = self.btngrp_lamp.checkedId()

        if btn_id == 1:
            str_cmd = "uar"
        elif btn_id == 2:
            str_cmd = "tung"
        elif btn_id == 3:
            str_cmd = "fabry"

        worker = Worker(self.move_servo_thread, [False, False, False], str_cmd)
        self.threadpool.start(worker)

    def select_speckle(self, speckle):
        self.disable_buttons()
        self.lbl_nonspec.setPixmap(self.led_off)
        self.lbl_spec.setPixmap(self.led_off)

        btn_id = self.btngrp_speckle.checkedId()

        if btn_id == 1:
            str_cmd = "nonspec"
        elif btn_id == 2:
            str_cmd = "spec"

        worker = Worker(self.move_servo_thread, [False, False, False], str_cmd)
        self.threadpool.start(worker)

    def select_nd_filter(self):
        self.disable_buttons()
        self.lbl_nd_set.setPixmap(self.led_off)
        self.lbl_nd_unset.setPixmap(self.led_off)

        btn_id = self.btngrp_nd.checkedId()

        if btn_id == 1:
            str_cmd = "nd"+str(self.spnbx_nd_angle.value())
        elif btn_id == 2:
            str_cmd = "nd0"

        worker = Worker(self.select_nd_filter_thread, [False, False, False], str_cmd, btn_id)
        self.threadpool.start(worker)

    def toggle_relay(self):
        self.disable_buttons()
        btn_id = self.btngrp_relays.checkedId()

        if btn_id == 1:
            str_cmd = "uar_relay"
        elif btn_id == 2:
            str_cmd = "tung_relay"
        elif btn_id == 3:
            str_cmd = "sol1"
        elif btn_id == 4:
            str_cmd = "sol2"
        elif btn_id == 5:
            str_cmd = "sol3"

        worker = Worker(self.toggle_relay_thread, [False, False, False], str_cmd, btn_id)
        self.threadpool.start(worker)
    # +================================================================+

    def load_settings(self):
        worker = Worker(self.load_settings_thread, [False, False, False])
        self.threadpool.start(worker)
    
    def enable_buttons(self):
        self.btn_connect.setDisabled(False)
        self.btn_disconnect.setDisabled(False)

        self.btn_tung_lamp.setDisabled(False)
        self.btn_uar_lamp.setDisabled(False)
        self.btn_cal_cvr.setDisabled(False)
        self.btn_star_cvr.setDisabled(False)
        self.btn_star2_cvr.setDisabled(False)

        self.btn_tung.setDisabled(False)
        self.btn_fabry.setDisabled(False)
        self.btn_uar.setDisabled(False)

        self.btn_nonspec.setDisabled(False)
        self.btn_spec.setDisabled(False)
        
        self.btn_nd_set.setDisabled(False)
        self.btn_nd_unset.setDisabled(False)

    def disable_buttons(self):
        self.btn_connect.setDisabled(True)
        self.btn_disconnect.setDisabled(True)
        
        self.btn_tung_lamp.setDisabled(True)
        self.btn_uar_lamp.setDisabled(True)
        self.btn_cal_cvr.setDisabled(True)
        self.btn_star_cvr.setDisabled(True)
        
        self.btn_tung.setDisabled(True)
        self.btn_fabry.setDisabled(True)
        self.btn_uar.setDisabled(True)

        self.btn_nonspec.setDisabled(True)
        self.btn_spec.setDisabled(True)
        
        self.btn_nd_set.setDisabled(True)
        self.btn_nd_unset.setDisabled(True)

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("resources/icons/prl2.png"))
apply_stylesheet(app, theme='dark_blue.xml')
window = Ui()
app.exec_()