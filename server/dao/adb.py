import common.py.module_command as _command

def connect(wifi_device):
    return _command.command("adb connect "+wifi_device)

def get_devices():
    return _command.command("adb devices")

def tcpip(local_device,port):
    return _command.command("adb -s "+local_device+" tcpip "+port)
