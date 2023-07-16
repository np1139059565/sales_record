import sys
from pathlib import Path
script1_path = str(Path(__file__).resolve().parents[2]  / 'server' / 'common' / 'py')
sys.path.append(script1_path)
import module_logger as logg
logger = logg.Logger()
sys.stdout = logger
sys.excepthook = logger.error_handler

import module_command as cmd




def connect(params, resp, self):
    # 检查参数是否足够
    if not params or not params['wifi_device']:
        print("请提供手机驱动信息!")
    else:
        return cmd.command("adb connect "+params['wifi_device'])

def devices(params, resp, self):
    return cmd.command("adb devices")

def tcpip(params, resp, self):
    # 检查参数是否足够
    if not params or not params['local_device'] or not params['port']:
        print("请提供手机驱动信息!")
    else:
        return cmd.command("adb -s "+params['local_device']+" tcpip "+params['port'])


if __name__ == "__main__":
    v = devices(1, 1, 1)
    print(v)