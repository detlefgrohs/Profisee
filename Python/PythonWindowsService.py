import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import logging
import os

logging.basicConfig(filename = fr"{os.path.splitext(os.path.basename(__file__))[0]}.log", format="%(asctime)s %(levelname)s : %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class PythonWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonWindowsService"
    _svc_display_name_ = "Python Windows Service"
    _svc_description_ = "A Python service."

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        logging.getLogger().info(f"PythonWindowsService __init__()")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)
        logging.getLogger().info(f"PythonWindowsService SvcStop()")

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                servicemanager.PYS_SERVICE_STARTED,
                                (self._svc_name_, ""))
        self.main()
        logging.getLogger().info(f"PythonWindowsService SvcDoRun()")

    def main(self):
        while self.is_running:
            try:
                logging.getLogger().info(f"PythonWindowsService main()")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(10) # Run every 10 seconds

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PythonWindowsService)