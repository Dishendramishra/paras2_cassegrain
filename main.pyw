from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys
from qt_material import apply_stylesheet
import traceback, sys
import serial
import serial.tools.list_ports

if sys.platform == "linux" or sys.platform == "linux2":
    pass

elif sys.platform == "win32":
    import ctypes
    myappid = u'prl.microk'  # arbitrary string
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

        # self.threadpool = QThreadPool()
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.ser = None

        self.img_tung_lamp = "resources/icons/off.png"
        self.img_uar_lamp  = "resources/icons/off.png"
        
        self.img_uar      = "resources/icons/off.png"
        self.img_tung     = "resources/icons/off.png"
        self.img_fabry    = "resources/icons/off.png"
        
        self.img_star_cvr = "resources/icons/off.png"
        self.img_cal_cvr  = "resources/icons/off.png"

        self.img_nd_off   = "resources/icons/on.png"
        self.img_nd_on    = "resources/icons/off.png"
        
        self.connect_ser()
        self.ui_settings()
        self.show()

    def ui_settings(self):

        # =========================================================================
        #  Lamp On/Off
        # =========================================================================
        self.btn_tung_lamp.clicked.connect(self.lamp_tung)
        self.btn_uar_lamp.clicked.connect(self.lamp_uar)
        self.lbl_tung_lamp.setPixmap(QPixmap(self.img_tung_lamp).scaled(32,32))
        self.lbl_uar_lamp.setPixmap(QPixmap(self.img_uar_lamp).scaled(32,32))
        # =========================================================================


        # =========================================================================
        # Select Lamp for Calibration Fiber
        # =========================================================================
        self.btn_uar.clicked.connect(lambda: self.select_lamp("uar"))
        self.btn_tung.clicked.connect(lambda: self.select_lamp("tung"))
        self.btn_fabry.clicked.connect(lambda: self.select_lamp("fabry"))
        self.lbl_uar.setPixmap(QPixmap(self.img_uar).scaled(32,32))
        self.lbl_tung.setPixmap(QPixmap(self.img_tung).scaled(32,32))
        self.lbl_fabry.setPixmap(QPixmap(self.img_fabry).scaled(32,32))
        # =========================================================================


        # =========================================================================
        #                                Fiber Covers
        # =========================================================================
        self.btn_star_cvr.clicked.connect(self.solenoid_1)
        self.btn_cal_cvr.clicked.connect(self.solenoid_2)

        self.lbl_star_cvr.setPixmap(QPixmap(self.img_star_cvr).scaled(32,32))
        self.lbl_cal_cvr.setPixmap(QPixmap(self.img_cal_cvr).scaled(32,32))
        # =========================================================================


        # =========================================================================
        #                               ND Filter
        # =========================================================================
        self.spnbx_nd_angle.setValue(46)
        self.spnbx_nd_angle.setHidden(True)

        self.btn_nd_on.clicked.connect(self.nd_on)
        self.btn_nd_off.clicked.connect(self.nd_off)
        
        self.lbl_nd_on.setPixmap(QPixmap(self.img_nd_on).scaled(32,32))
        self.lbl_nd_off.setPixmap(QPixmap(self.img_nd_off).scaled(32,32))
        # =========================================================================
        
    def toggle_led(self, led, target):
        if led == "resources/icons/off.png":
            target.setPixmap(QPixmap("resources/icons/on.png").scaled(32,32))
            return "resources/icons/on.png"
        else:
            target.setPixmap(QPixmap("resources/icons/off.png").scaled(32,32))
            return "resources/icons/off.png"
        

    def connect_ser(self):
        ports = serial.tools.list_ports.comports()
        target_port = None
        for port, desc, hwid in sorted(ports):
            print("{}: {} [{}]".format(port, desc, hwid))
            if "PID=2341:0043" in hwid:
                # print(port)
                target_port = port

        self.ser = serial.Serial(target_port, 115200)

    
    def send_cmd(self, str_cmd):
        # print("cmd: ", str_cmd)
        self.ser.write(str_cmd.encode())
    
    def read_output(self):
        # return "done"
        return self.ser.readline().strip().decode()

    def all_led_off(self):
        self.lbl_uar.setPixmap(QPixmap("resources/icons/off.png").scaled(32,32))
        self.lbl_tung.setPixmap(QPixmap("resources/icons/off.png").scaled(32,32))
        self.lbl_fabry.setPixmap(QPixmap("resources/icons/off.png").scaled(32,32))

    def select_lamp(self, lamp):
        self.all_led_off()

        if lamp == "uar":
            self.send_cmd("home")
        elif lamp == "tung":
            self.send_cmd("ma19000")
        elif lamp == "fabry":
            self.send_cmd("ma38000")
        else:
            print("error")
            return
        
        output = self.read_output()

        self.lbl_uar.setPixmap(QPixmap("resources/icons/on.png").scaled(32,32)) if lamp == "uar"  else None
        self.lbl_tung.setPixmap(QPixmap("resources/icons/on.png").scaled(32,32)) if lamp == "tung"  else None
        self.lbl_fabry.setPixmap(QPixmap("resources/icons/on.png").scaled(32,32)) if lamp == "fabry"  else None
        
    def nd_on(self):
        self.send_cmd(str(self.spnbx_nd_angle.value()))
        output = self.read_output()

        if output == "done":
            self.lbl_nd_on.setPixmap(QPixmap("resources/icons/on.png").scaled(32,32))
            self.lbl_nd_off.setPixmap(QPixmap("resources/icons/off.png").scaled(32,32))
        else:
            print("error")

    def nd_off(self):
        self.send_cmd("0")
        output = self.read_output()

        if output == "done":
            self.lbl_nd_on.setPixmap(QPixmap("resources/icons/off.png").scaled(32,32))
            self.lbl_nd_off.setPixmap(QPixmap("resources/icons/on.png").scaled(32,32))
        else:
            print("error")

    def solenoid_1(self):
        self.send_cmd("sol1")
        output = self.read_output()

        if output == "done":
            self.img_star_cvr = self.toggle_led(self.img_star_cvr, self.lbl_star_cvr)
        else:
            print("error")

    def solenoid_2(self):
        self.send_cmd("sol2")
        output = self.read_output()

        if output == "done":
            self.img_cal_cvr = self.toggle_led(self.img_cal_cvr, self.lbl_cal_cvr)
        else:
            print("error")

    def lamp_tung(self):
        self.send_cmd("tung")
        output = self.read_output()

        if output == "done":
            self.img_tung_lamp = self.toggle_led(self.img_tung_lamp, self.lbl_tung_lamp)
        else:
            print("error")

    def lamp_uar(self):
        self.send_cmd("uar")
        output = self.read_output()

        if output == "done":
            self.img_uar_lamp = self.toggle_led(self.img_uar_lamp, self.lbl_uar_lamp)
        else:
            print("error")

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("resources/icons/prl2.png"))
apply_stylesheet(app, theme='dark_blue.xml')
window = Ui()
app.exec_()