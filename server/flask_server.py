import logging
import json
import os
import time

import common.py.module_ip as _mip
import common.py.module_file as _file

import dao.phone as _phone


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
            _tmonitor=v[0]
        _file.f_write(_tmonitor_file,_tmonitor)
        
        #to wx
        _is_open_wx=request.args.get("isopenwx",_NULL)
        if _is_open_wx!=_NULL:
            os.system("server\cmd\wx.bat "+_tmonitor_file.replace("/","\\"))
        return make_response("",200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)


@_flask_app.route('/get_last_monitor',methods=["GET"])
def f_get_last_monitor():
    try:
        _flask_app.logger.info("get_last_monitor...")
        #get all monitor name...
        _monitor_arr=os.listdir(_MONITOR_PATH)
        _monitor_arr.sort()
        try:
            #get last monitor name arr...
            _last_heart_time=request.args.get("last_heart_time",_NULL)
            _monitor_arr=_monitor_arr[_monitor_arr.find(_last_heart_time)+1:len(_monitor_arr)]
        except:
            _monitor_arr=[_monitor_arr.pop()]
        
        #get monitor content by name...
        for i in range(len(_monitor_arr)):
            _mname=_monitor_arr[i]
            _monitor_arr[i]={
                "name":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(_mname))) ,
                "content":_file.f_read(_MONITOR_PATH+_mname)
            }
        return make_response(json.dumps(_monitor_arr),200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)


@_flask_app.route("/get_phones",methods=["GET"])
def f_phone_heart():
    try:
        return make_response(_file.f_read(_PHONES_PATH),200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/add_phone",methods=["GET"])
def f_add_phone():
    try:
        _flask_app.logger.info("add_phone...")
        _ip=request.args.get("ip",_NULL)
        _port=request.args.get("port",_NULL)
        #check phone
        _rstr=_phone.phone_heart(_ip,_port)
        if _rstr.find("connected to")==0:
            #add phone
            phone_arr=json.loads(_file.f_read(_PHONES_PATH))
            phone_arr.append({"ip":_ip,"port":_port,"heart_time":time.time()})
            _file.f_write(_PHONES_PATH,json.dumps(phone_arr))

        return make_response(_rstr,201 if _rstr.find("connected to")!=0 else 200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/phone_heart",methods=["GET"])
def f_connect_phone():
    try:
        _ip=request.args.get("ip",_NULL)
        _port=request.args.get("port",_NULL)

        _isfind_phone=False
        phone_arr=json.loads(_file.f_read(_PHONES_PATH))
        for i in range(len(phone_arr)):
            _p=phone_arr[i]
            #find phone
            if _p.get("ip")==_ip and _p.get("port")==_port:
                _isfind_phone=True
                _rstr=_phone.phone_heart(_ip,_port)
                if _rstr.find("already connected to")!=0 or _rstr.find("connected to")!=0:
                    #update heart time
                    phone_arr[i]["heart_time"]=time.time()
                    _file.f_write(_PHONES_PATH,json.dumps(phone_arr))
                    return make_response(_rstr,200)
                else:
                    return make_response(_rstr,500)
        if _isfind_phone==False:
            return make_response("not find phone",500)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err!",500)


@_flask_app.route("/start_phone_command",methods=["GET"])
def f_start_phone_command():
    try:
        _flask_app.logger.info("phone_show_command...")
        _ip=request.args.get("ip",_NULL)
        _port=request.args.get("port",_NULL)
        os.system("start server\cmd\push.bat "+_ip+" "+_port+" "+_mip.f_get_local_ip())
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
        host="localhost",
        port=5000
    )
