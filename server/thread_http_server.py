import sys
import time
from pathlib import Path
script1_path = str(Path(__file__).resolve().parents[2] / 'sales_record' / 'server' / 'common' / 'py')
sys.path.append(script1_path)
import module_logger as logg
logger=logg.Logger()
sys.stdout = logger
sys.excepthook = logger.error_handler

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading





# 创建一个多线程HTTP请求处理类
class MultiThreadedHTTPRequestHandler(BaseHTTPRequestHandler):
    # 处理GET请求
    def do_GET(self):
        # 解析URL中的参数
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # 获取当前线程
        thread_name = threading.currentThread().getName()
        
        # 打印参数
        print(f"Received parameters in thread {thread_name}:--{self.path} {query_params}")

        #默认响应
        res={
            'code':200,
            'headers':{
                'Content-type': 'text/plain; charset=utf-8'
            },
            'message':'def res'
        }

        # 调用自定义service处理结果
        url=self.path.split('?')[0]
        try:
            murl=f'services.{".".join(url.split("/")[1:][:-1])}'
            print(f'murl is :{murl}')
            starttime=time.time()*1000
            module=__import__(murl,fromlist=[''])
            method = getattr(module, url.split('/')[-1])
            msg=str(method(query_params,res,self))
            endtime=time.time()*1000
            print('hand time:',endtime-starttime)
            if not msg:
                print(f'services return is null:{msg}')
            else:
                res['message']=msg
        except Exception as e:
            res['code']=404 if 'No module named \'services.' in str(e) else 500
            res['message']='Not find' if 'No module named \'services.' in str(e) else str(e)
            print(e)

        # 设置响应状态码
        self.send_response(res['code'])
        # 设置响应头部
        for k in res['headers']:
            self.send_header(k,res['headers'][k])
        self.end_headers()
        
        # 发送响应内容
        self.wfile.write(res['message'].encode('utf-8'))

# 创建多线程HTTP服务并指定请求处理类和端口
def run(server_class=ThreadingHTTPServer, handler_class=MultiThreadedHTTPRequestHandler, port=8000):
    # 启动多线程HTTP服务
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting server on port', port)
    httpd.serve_forever()

# 运行多线程HTTP服务
run()