import logging
import json
import os
import time

import common.py.module_ip as _ip
import common.py.module_file as _file

from flask import Flask, request, make_response

_NULL = "_NULL"
_HEART_PATH="server/db/hearts/"
_MONTH_PATH="server/db/months/"

_flask_app = Flask(__name__)


@_flask_app.route('/get_data', methods=["GET"])
def f_get_data():
    try:
        _month = request.args.get("month", _NULL)
        _data_path = _MONTH_PATH+_month+".csv"
        _flask_app.logger.info("read data path "+_data_path)
        if _month != _NULL:
            return make_response(_file.f_read(_data_path), 200)
        else:
            return make_response("not find", 404)
    except Exception as e:
        logging.exception("server is err!", e)
        return make_response("server is err", 500)


@_flask_app.route('/get_months', methods=["GET"])
def f_get_months():
    try:
        _dirs = os.listdir(_MONTH_PATH)
        for i in range(len(_dirs)):
            _dirs[i] = _dirs[i].replace(".csv", "")
        return make_response(json.dumps(_dirs), 200)
    except Exception as e:
        logging.exception("server is err!", e)
        return make_response("server is err", 500)


@_flask_app.route('/add_data', methods=["POST"])
def add_data():
    try:
        _month = request.args.get("month", _NULL)
        _data_path = _MONTH_PATH+_month+".csv"
        _flask_app.logger.info("write data path "+_data_path)
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


@_flask_app.route('/set_heart', methods=["POST"])
def f_set_heart_data():
    try:
        _heart_path = _HEART_PATH+str(time.time())
        _flask_app.logger.info("write heart... "+_heart_path)
        _heart=_NULL
        for v in request.form.items():
            #_data=json.loads(v[0])
            _heart=v[0]
        _flask_app.logger.info(_heart)
        _file.f_write(_heart_path,_heart)
        return make_response("",200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)

@_flask_app.route('/get_heart',methods=["GET"])
def f_get_heart_data():
    try:
        #get all heart...
        _heart_list=os.listdir(_HEART_PATH)
        _heart_list.sort()
        #get last heart list...
        _last_heart_name=request.args.get("last_heart_name",_NULL)
        try:
            _heart_list=_heart_list[_heart_list.index(_last_heart_name)+1:99]
        except:
            _heart_list=[_heart_list.pop()]
        
        #get heart content...
        for i in range(len(_heart_list)):
            _heart_name=_heart_list[i]
            _heart_list[i]={"name":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(_heart_name))) ,"content":_file.f_read(_HEART_PATH+_heart_name)}
        return make_response(json.dumps(_heart_list),200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)


if __name__=="__main__":
    _flask_app.debug=True
    #ip.f_get_local_ip()
    _flask_app.run(
        host="localhost",
        port=5000
    )
