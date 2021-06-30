from EquirectangularViewer import config
import sys
import os
from PyQt5.QtCore import QProcess, QSettings
import platform

try:
    from pydevd import *
except ImportError:
    None

state = None
pid = None

s = QSettings()
# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")


def serverInFolder(root_folder):
    p = QProcess()
    p.setWorkingDirectory(root_folder)
    args = ('-m', 'http.server', str(config.PORT))
    exec_dir = os.path.dirname(sys.executable)

    if WINDOWS:
        executable = os.path.join(exec_dir, ('python3', 'python-qgis.bat')[True])
    else:
        executable = os.path.join(exec_dir, ('python3', 'python-qgis.sh')[True])
    state, pid = p.startDetached(executable, args, root_folder)
    if state:
        s.setValue("EquirectangularViewer/server_pid", pid)


def serverShutdown():
    server_pid = s.value("EquirectangularViewer/server_pid")
    if server_pid is not None:
        pid = int(server_pid)
        try:
            if WINDOWS:
                QProcess.execute('TASKKILL /PID %s' % pid)
            else:
                os.kill(pid, 11)
        except Exception:
            None
    return
