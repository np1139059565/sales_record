import common.py.module_command as _command

def connect(ip,port):
    return _command.command("adb connect "+ip+":"+port)
