import logging
import json
import os
import time

import common.py.module_ip as _mip
import common.py.module_file as _file

import dao.adb as _adb


from flask import Flask, request, make_response


_NULL = "_NULL"
_MONITOR_PATH="server/db/monitors/"
_MONTH_PATH="server/db/months/"
_PHONES_PATH="server/db/phones.json"

_flask_app = Flask(__name__)


@_flask_app.route('/get_month_data', methods=["GET"])
def f_get_month_data():
    try:
        _month = request.args.get("month", _NULL)
        _data_path = _MONTH_PATH+_month+".csv"
        _flask_app.logger.info("get_month_data "+_data_path)
        if _month != _NULL:
            return make_response(_file.f_read(_data_path), 200)
        else:
            return make_response("not find", 404)
    except Exception as e:
        logging.exception("server is err!", e)
        return make_response("server is err", 500)


@_flask_app.route('/get_month_arr', methods=["GET"])
def f_get_month_arr():
    try:
        _dirs = os.listdir(_MONTH_PATH)
        _flask_app.logger.info("get_month_arr "+_MONTH_PATH)
        for i in range(len(_dirs)):
            _dirs[i] = _dirs[i].replace(".csv", "")
        return make_response(json.dumps(_dirs), 200)
    except Exception as e:
        logging.exception("server is err!", e)
        return make_response("server is err", 500)


@_flask_app.route('/add_table_data', methods=["POST"])
def f_add_table_data():
    try:
        _month = request.args.get("month", _NULL)
        _data_path = _MONTH_PATH+_month+".csv"
        _flask_app.logger.info("add_table_data "+_data_path)
        _data = _NULL
        for v in request.form.items():
            #_data=json.loads(v[0])
            _data = v[0]
        _flask_app.logger.info(_data)
        _file.f_write(_data_path, _data.replace("\\n", "\n"))
        return make_response("", 200)
    except Exception as e:
        logging.exception("server is err!", e)
        return make_response("server is err", 500)


@_flask_app.route('/add_monitor_child', methods=["POST"])
def f_add_monitor_child():
    try:
        _tmonitor_file = _MONITOR_PATH+str(time.time())
        _flask_app.logger.info("add_monitor_child "+_tmonitor_file)
        _tmonitor=_NULL
        for v in request.form.items():
            #_data=json.loads(v[0])
            _tmonitor=v[0].replace(" ","+")
        _flask_app.logger.info(_tmonitor)
        _file.f_write(_tmonitor_file,_tmonitor)
        
        #to wx
        _is_open_wx=request.args.get("isopenwx",_NULL)
        if _is_open_wx!=_NULL:
            os.system("server\cmd\wx.bat "+_tmonitor_file.replace("/","\\"))
        return make_response("",200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)


@_flask_app.route('/get_monitor_last_times',methods=["GET"])
def f_get_monitor_last_times():
    try:
        _flask_app.logger.info("get_monitor_last_times...")
        #get all monitor name...
        _monitor_arr=os.listdir(_MONITOR_PATH)
        _monitor_arr.sort()
        try:
            #get last index by name...
            _last_heart_time=request.args.get("last_heart_time",_NULL)
            _last_index=_monitor_arr.index(_last_heart_time)
            #remove cache
            if _last_index>100:
                for i in reversed(range(_last_index)):
                    if i>30:
                        _flask_app.logger.info("remove monitor cache "+_MONITOR_PATH+_monitor_arr[i])
                        os.remove(_MONITOR_PATH+_monitor_arr[i])
            
            _monitor_arr=_monitor_arr[_last_index+1:len(_monitor_arr)]
        except Exception as e1:
            logging.exception("server is err!",e1)
            _monitor_arr=[_monitor_arr.pop()]
        return make_response(json.dumps(_monitor_arr),200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)


@_flask_app.route('/get_monitor_info',methods=["GET"])
def f_get_monitor():
    try:
        _flask_app.logger.info("get_monitor_info...")
        return make_response(_file.f_read(_MONITOR_PATH+request.args.get("time")),200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)


@_flask_app.route("/get_adb_devices",methods=["GET"])
def f_get_adb_devices():
    try:
        _flask_app.logger.info("get adb devices...")
        return make_response(_adb.get_devices(),200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/add_phone",methods=["GET"])
def f_add_phone():
    try:
        _flask_app.logger.info("phone_add...")
        _wifi_device=request.args.get("wifi_device",_NULL)
        _port=_wifi_device.split(":")[1]
        _local_device=request.args.get("local_device",_NULL)
        _search_button=request.args.get("search_button",_NULL)
        _search_str=request.args.get("search_str",",1")
        _ok=True
        #tcpip..
        if _local_device!=_NULL and _adb.tcpip(_local_device,_port).find("restarting in TCP mode port:")!=0:
            _ok=False
        _flask_app.logger.info("tcpip to "+_local_device+" "+_port+" is "+str(_ok))
        #connect..
        _rstr="tcpip local device is fail"
        if _ok:
            _rstr=_adb.connect(_wifi_device)
            _ok=(_rstr.find("connected to")==0 or _rstr.find("already connected to")==0)
        _flask_app.logger.info("connect to "+_wifi_device+" is "+str(_ok))
        if _ok:
            #add phone
            phone_arr=json.loads(_file.f_read(_PHONES_PATH))
            phone_arr.append({"wifi_device":_wifi_device,"heart_time":time.time(),
            "search_button":_search_button,"search_str":_search_str})
            _file.f_write(_PHONES_PATH,json.dumps(phone_arr))

        return make_response(_rstr,200 if _ok else 500)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/get_phones",methods=["GET"])
def f_get_phones():
    try:
        return make_response(_file.f_read(_PHONES_PATH),200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/phone_delete",methods=["GET"])
def f_phone_delete():
    try:
        _flask_app.logger.info("phone_delete...")
        _wifi_device=request.args.get("wifi_device",_NULL)
        phone_arr=json.loads(_file.f_read(_PHONES_PATH))
        for i in range(len(phone_arr)):
            if _wifi_device==phone_arr[i].get("wifi_device"):
                phone_arr.pop(i)
                _file.f_write(_PHONES_PATH,json.dumps(phone_arr))
                return make_response("ok",200)
        return make_response("not find device",500)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/phone_start",methods=["GET"])
def f_phone_start():
    try:
        _flask_app.logger.info("phone start...")
        _wifi_device=request.args.get("wifi_device",_NULL)
        _local_device=request.args.get("local_device",_NULL)
        _search_button=request.args.get("search_button","")
        _search_str=request.args.get("search_str",",1")
        _ok=True
        #re open tcpip
        if _local_device!=_NULL:
            _port=_wifi_device.split(":")[1]
            _ok=(_adb.tcpip(_local_device,_port).find("restarting in TCP mode port:")!=0)
            _flask_app.logger.info("tcpip to "+_local_device+" "+_port+" is "+str(_ok))
        #connect..
        _rstr="tcpip local device is fail"
        if _ok:
            _rstr=_adb.connect(_wifi_device)
            _ok=(_rstr.find("connected to")==0 or _rstr.find("already connected to")==0)
        _flask_app.logger.info("connect to "+_wifi_device+" is "+str(_ok))
        #start..
        if _ok:
            os.system("start server\cmd\start_phone.bat "+_wifi_device+" "+_mip.f_get_local_ip()
            +" \""+_search_button+"\""+" \""+_search_str+"\"")
        return make_response(_rstr,200 if _ok else 500)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/phone_heart",methods=["GET"])
def f_phone_heart():
    try:
        _phone_ip=request.remote_addr
        _flask_app.logger.info("phone_heart..."+_phone_ip)
        phone_arr=json.loads(_file.f_read(_PHONES_PATH))
        for i in range(len(phone_arr)):
            if _phone_ip==phone_arr[i].get("ip"):
                phone_arr[i]["heart_time"]=time.time()
                _file.f_write(_PHONES_PATH,json.dumps(phone_arr))
        return make_response("ok",200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/get_time",methods=["GET"])
def f_get_time():
    try:
        _flask_app.logger.info("get_time...")
        return make_response(str(time.time()), 200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


if __name__=="__main__":
    _flask_app.debug=True
    #_mip.f_get_local_ip()
    _flask_app.run(
        host="0.0.0.0",
        port=5000
    )
