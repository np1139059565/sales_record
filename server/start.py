import logging
import json
import os

import common.py.module_ip as _ip
import common.py.module_file as _file

from flask import Flask,request,make_response

_NULL="_NULL"
app=Flask(__name__)
@app.route('/get_data',methods=["GET"])
def f_get_data():
    try:
        _month=request.args.get("month",_NULL)
        _data_path="server/db/"+_month+".csv"
        app.logger.info("read data path "+_data_path)
        if _month!=_NULL:
            return make_response(_file.f_read(_data_path),200)
        else:
            return  make_response("not find",404)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)

@app.route('/get_months',methods=["GET"])
def f_get_months():
    try:
        _dirs=os.listdir("server/db/")
        for i in range(len(_dirs)):
            _dirs[i]=_dirs[i].replace(".csv","")
        return make_response(json.dumps(_dirs),200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)

@app.route('/add_data',methods=["POST"])
def add_data():
    try:
        _month=request.args.get("month",_NULL)
        _data_path="server/db/"+_month+".csv"
        app.logger.info("write data path "+_data_path)
        _data=_NULL
        for v in request.form.items():
            #_data=json.loads(v[0])
            _data=v[0]
        app.logger.info(_data)
        _file.f_write(_data_path,_data.replace("\\n","\n"))
        return make_response("",200)
    except Exception as e:
        logging.exception("server is err!",e)
        return make_response("server is err",500)


if __name__=="__main__":
    app.debug=True
    #ip.f_get_local_ip()
    app.run(
        host="localhost",
        port=5000
    )
