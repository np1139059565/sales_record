import uiautomator2 as u2
import json
import sys
from pathlib import Path
script1_path = str(Path(__file__).resolve().parents[2]  / 'server' / 'common' / 'py')
sys.path.append(script1_path)
import module_logger as logg
logger = logg.Logger()
sys.stdout = logger
sys.excepthook = logger.error_handler

device_pool = {}

def connect(device_serial):
    global device_pool
    if device_serial in device_pool:
        return device_pool[device_serial]
    else:
        device = u2.connect(device_serial)
        device_pool[device_serial] = device
        return device

def dump(params, resp, self):
    # 检查参数是否足够
    if not params or not params['device']:
        print("参数错误!")
        return False
    else:
        device_serial = params['device'][0]
        d = connect(device_serial)
        print('dump..')
        return d.dump_hierarchy()
    
def click(params, resp, self):
    device_serial = params['device'][0]
    # 连接手机设备
    con = connect(device_serial)

    node_info=json.loads(params['node_info'][0])
    # 解析边界值字符串
    bounds = node_info['bounds'].strip("[]").split("][")
    left, top = map(int, bounds[0].split(","))
    right, bottom = map(int, bounds[1].split(","))
        
    # 计算元素的中心点
    x = (left + right) // 2
    y = (top + bottom) // 2

    print('click..'+str(x)+' '+str(y))

    # 点击元素的中心点
    return con.click(x, y)

def slice(params, resp, self):
    device_serial = params['device'][0]
    # 连接手机设备
    con = connect(device_serial)

    node_info=json.loads(params['node_info'][0])
    # 解析边界值字符串
    bounds = node_info['bounds'].strip("[]").split("][")
    left, top = map(int, bounds[0].split(","))
    right, bottom = map(int, bounds[1].split(","))
        
    speed= 0.5 if not node_info['speed'] else node_info['speed']

    print('slice..'+str(left)+' '+str(top)+' '+str(right)+' '+str(bottom)+' '+str(speed))
    # 执行滑动操作
    return con.swipe(left, top, right, bottom,duration=speed)

def input(params, resp, self):
    device_serial = params['device'][0]
    # 连接手机设备
    con = connect(device_serial)

    node_info=json.loads(params['node_info'][0])

    resourceStr=node_info['resource-id']
    # classStr=node_info['class']
    value=node_info['value']

    print('input..'+value+','+resourceStr)
    e=con(
        resourceId=resourceStr
        # ,className=classStr
        )
    return e.set_text(value)

if __name__ == "__main__":
    v = dump({'device': ['78590ad7']}, 1, 1)
    print(v)