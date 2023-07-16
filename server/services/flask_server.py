import logging
import json
import os
import time

import sys
from pathlib import Path
script1_path = str(Path(__file__).resolve().parents[2]  / 'server' / 'common' / 'py')
sys.path.append(script1_path)
import module_logger as logg
logger = logg.Logger()
sys.stdout = logger
sys.excepthook = logger.error_handler

import module_ip as _mip
import module_file as _file

script2_path = str(Path(__file__).resolve().parents[2]  / 'server' / 'services')
sys.path.append(script2_path)
import adb as _adb


if __name__ == "__main__":
    print(_adb.devices(1,1,1))


_NULL = "_NULL"
_PSTR_PATH="server/db/pstr/"
_MONTH_PATH="server/db/months/"
_PHONES_PATH="server/db/phones.json"
wifi_loop_script='server/py/loop_by_qpython.py'

def make_response(resp,msg,code):
    resp['code']=code
    resp['message']=msg
    return ''


def f_get_month_data(params, resp, self):
    try:
        _month = params.get("month", _NULL)
        _data_path = _MONTH_PATH+_month+".csv"
        print("get_month_data "+_data_path)
        if _month != _NULL:
            return make_response(resp,_file.f_read(_data_path), 200)
        else:
            return make_response(resp,"not find", 404)
    except Exception as e:
        print("server is err!", e)
        return make_response(resp,"server is err", 500)


def f_get_month_arr(params, resp, self):
    try:
        _dirs = os.listdir(_MONTH_PATH)
        print("get_month_arr "+_MONTH_PATH)
        for i in range(len(_dirs)):
            _dirs[i] = _dirs[i].replace(".csv", "")
        return make_response(resp,json.dumps(_dirs), 200)
    except Exception as e:
        print("server is err!", e)
        return make_response(resp,"server is err", 500)

def f_add_table_data(params, resp, self):
    try:
        _month = params.get("month", _NULL)
        _data_path = _MONTH_PATH+_month+".csv"
        print("add_table_data "+_data_path)
        _data = _NULL
        for v in request.form.items(params, resp, self):
            #_data=json.loads(v[0])
            _data = v[0]
        print(_data)
        _file.f_write(_data_path, _data.replace("\\n", "\n"))
        return make_response(resp,"", 200)
    except Exception as e:
        print("server is err!", e)
        return make_response(resp,"server is err", 500)

def up_new_pstr(params, resp, self):
    pobj=json.loads(params['pobj'][0])

    _ok=True
    _rstr='success'
  
    parr=[]
    # split file by 60s
    pstr_path=f'{_PSTR_PATH}{str(int(pobj["time"]/60/30))}min30.json'
    isexist=_file.f_exist(pstr_path)
    print("up new pstr:",pobj,isexist)
    if isexist:
        parr=json.loads(_file.f_read(pstr_path))

    parr.append(pobj)
    _file.f_write(pstr_path,json.dumps(parr))

    return make_response(resp,_rstr,200 if _ok else 500)

def get_pstr(params, resp, self):
        file_arr=os.listdir(_PSTR_PATH)
        file_arr.sort()
        index= -1 if params["page"][0] == 'last' else int(params["page"][0])
        return make_response(resp,json.dumps({
            'index':index if index>=0 else len(file_arr)-1,
            'count':len(file_arr),
            'conter':_file.f_read(f'{_PSTR_PATH}{file_arr[index]}')
        }),200)

def f_get_monitor(params, resp, self):
    try:
        print("get_monitor_info...")
        return make_response(resp,_file.f_read(_PSTR_PATH+params.get("time")),200)
    except Exception as e:
        print("server is err!",e)
        return make_response(resp,"server is err",500)

def f_save_phone(params, resp, self):
    print("save phone...")
    phone_info=json.loads(params['phone_info'][0])
    _ok=True
    _rstr='success'
  
    phone_arr=json.loads(_file.f_read(_PHONES_PATH))
    #check is cove
    iscover=False
    for i in range(len(phone_arr)):
        p=phone_arr[i]
        if p['device']==phone_info['device']:
            iscover=True
            phone_arr[i]=phone_info
    if iscover !=True:
        phone_arr.append(phone_info)
    _file.f_write(_PHONES_PATH,json.dumps(phone_arr))

    return make_response(resp,_rstr,200 if _ok else 500)

def f_get_phones(params, resp, self):
    try:
        return make_response(resp,_file.f_read(_PHONES_PATH),200)
    except Exception as e:
        print("server is err!",e)
        return make_response(resp,"server is err!",500)

def f_phone_delete(params, resp, self):
        print("delete phone...")
        device=params['device'][0]
        phone_arr=json.loads(_file.f_read(_PHONES_PATH))
        for i in range(len(phone_arr)):
            if device==phone_arr[i].get("device"):
                phone_arr.pop(i)
                _file.f_write(_PHONES_PATH,json.dumps(phone_arr))
                return make_response(resp,"ok",200)
        return make_response(resp,"not find device",500)

def f_phone_start(params, resp, self):
    print("phone start...")
    device=params['device'][0]
    hand_nodes_str=params['hand_nodes'][0]
    ivlen=params['ivlen'][0]
    # return os.system("python server\py\loop_by_xml.py "+device +" \""+hand_nodes_str+"\" "+_mip.f_get_local_ip())
    # 将字符串转换为十六进制字符串
    hex_str = hand_nodes_str.encode('utf-8').hex()

    # 在每两个字符之间插入 "-"
    hex_str_with_dashes = '-'.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))

    os.system("start server\cmd\\run_python.bat server\py\loop_by_xml.py "+device+" "+hex_str_with_dashes+" "+ivlen)

def f_start_by_wifi(params, resp, self):

    return make_response(resp,_file.f_read(wifi_loop_script),200)

