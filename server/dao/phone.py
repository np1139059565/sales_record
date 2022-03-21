import common.py.module_command as _command

def phone_heart(ip,port):
    return _command.command("adb connect "+ip+":"+port)
