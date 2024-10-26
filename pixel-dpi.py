import os
import subprocess
import ctypes
import sys
import time
import psutil
from win32com.client import Dispatch

script_dir = os.path.dirname(os.path.abspath(__file__))
goodbye_dpi_process = None

def set_dns(interface_name):
    try:
        subprocess.run(f'netsh interface ip set dns name="{interface_name}" source=static addr=1.1.1.1', shell=True, check=True)
        subprocess.run(f'netsh interface ip add dns name="{interface_name}" addr=1.0.0.1 index=2', shell=True, check=True)
    except subprocess.CalledProcessError:
        pass

def check_dns(interface_name):
    try:
        result = subprocess.run(f'netsh interface ip show dns name="{interface_name}"', shell=True, capture_output=True, text=True)
        return "1.1.1.1" in result.stdout and "1.0.0.1" in result.stdout
    except Exception:
        return False

def check_process_running(process_name):
    while True:
        time.sleep(30)
        if not any(process_name in p for p in (p.name() for p in psutil.process_iter())):
            os._exit(0)

def run_goodbyedpi():
    global goodbye_dpi_process
    arch = "x86_64" if os.environ["PROCESSOR_ARCHITECTURE"] == "AMD64" else "x86"
    exe_path = os.path.join(script_dir, arch, "goodbyedpi.exe")

    if ctypes.windll.shell32.IsUserAnAdmin():
        try:
            if not check_dns("Ethernet"):
                set_dns("Ethernet")
            if not check_dns("Wi-Fi"):
                set_dns("Wi-Fi")
            goodbye_dpi_process = subprocess.Popen([exe_path, "-5"], creationflags=subprocess.CREATE_NO_WINDOW)
            check_process_running("goodbyedpi.exe")
        except Exception:
            pass
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

def add_to_task_scheduler():
    try:
        task_name = "PixelDPIStart"
        startup_script_path = os.path.abspath(__file__)
        
        command = f'''schtasks /create /f /tn "{task_name}" /tr '"{sys.executable}"' /sc onlogon /rl highest'''
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        pass

def main():
    add_to_task_scheduler()
    run_goodbyedpi()

if __name__ == "__main__":
    main()
