import xml.etree.ElementTree as ET
import requests
import json
import subprocess
import time
import copy
from urllib.parse import quote
import traceback



port=''
ip=''
dump_xml=""
pstr_cache=[]
server_host='127.0.0.1'
atx_host='127.0.0.1'

def http_get_by_curl(url):
    curl_cmd = 'curl -X GET -w "%{http_code}" '+f'"{quote(url, safe=":/?=&")}"'
    result = subprocess.Popen(
        curl_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8'
    )
    output, error = result.communicate()

    status_code=int(output.strip()[-3:])
    text=output.strip()[:-3]
    return {'status_code':status_code,'text':text}

def http_post_by_curl(url,data):
    pass


def run_hand(node_info):
    url=f'http://{atx_host}:7912/jsonrpc/0'
    headers = {'Content-Type': 'application/json'}
    payload_arr=eval(f'get_{node_info["hand_type"]}_payload(node_info)')
    r_arr=[]
    for p in payload_arr:
        response = requests.post(url, data=json.dumps(p), headers=headers)
        print('run hand code:',response.status_code)
        r_arr.append(response)
    return r_arr

def get_click_payload(node_info):
    # 解析边界值字符串
    bounds = node_info['bounds'].strip("[]").split("][")
    left, top = map(int, bounds[0].split(","))
    right, bottom = map(int, bounds[1].split(","))
        
    # 计算元素的中心点
    x = (left + right) // 2
    y = (top + bottom) // 2

    print('click by utx',x,y)
    
    return [{
        "jsonrpc": "2.0",
        "id": "1",
        "method": "click",
        "params": [x, y]
    }]

def get_slice_payload(node_info):
    # 解析边界值字符串
    bounds = node_info['bounds'].strip("[]").split("][")
    left, top = map(int, bounds[0].split(","))
    right, bottom = map(int, bounds[1].split(","))
        
    speed= 0.5 if not node_info['speed'] else node_info['speed']

    print('slice..'+str(left)+' '+str(top)+' '+str(right)+' '+str(bottom)+' speed='+str(speed))

    return [{
        "jsonrpc": "2.0",
        "id": "875f1a68cb92cf4b28b43802504227d9",
        "method": "swipe",
        "params": [500, 2000, 500, 1000, int(200*speed)]
    }]

def get_input_payload(node_info):

    resourceIdStr=node_info['resource-id']
    # classStr=node_info['class']
    value=node_info['value']
    # value_encode=''.join([f'\\u{ord(x):04x}' if ord(x) > 127 else x for x in  value])  # 转换为Unicode代码点表示
    print('input..',resourceIdStr,value)
    return [
        {
            "jsonrpc": "2.0",
            "id": "37deeb48c6e53aa721665821c18886b4",
            "method": "waitForExists",
            "params": [
                {
                    "mask": 2097152,
                    "childOrSibling": [],
                    "childOrSiblingSelector": [],
                    "resourceId": resourceIdStr
                },
                20000
            ]
        },
        {
            "jsonrpc": "2.0",
            "id": "46b822226986402f6aa23f86f6f4e994",
            "method": "setText",
            "params": [
                {
                    "mask": 2097152,
                    "childOrSibling": [],
                    "childOrSiblingSelector": [],
                    "resourceId": "com.aihuishou.opt:id/et_search"
                },
                value
            ]
        }]


def dump_by_atx():
    global dump_xml
    response = requests.get(f'http://{atx_host}:7912/dump/hierarchy')
    if response.status_code == 200:
        dump_xml=json.loads(response.text).get('result')
    return response.status_code == 200

def find_node_by_reg(reg=''):
    global dump_xml
    root_node = ET.fromstring(dump_xml)
    if not reg:
        return root_node
    else:
        # 查找任意深度的子元素'.//node[@id="111"]'
        # print('find node by reg:',reg)
        return root_node.findall(reg)


def run_hand_by_nodes(node_arr,func_new_pstr_callback=None,si=0):
    global pstr_cache
    pstr_new_cache=[]
    for i in range(len(node_arr)):
        # loop by check..
        if node_arr[i]['type']=='check':
            comp_node=node_arr[i]
            count=0
            while True:
                # refush dump,save cache
                dump_by_atx()
                phone_infos=find_node_by_reg('.//node[@resource-id="com.aihuishou.opt:id/ll_info"]')
                for p in phone_infos:
                    ptext_arr=[]
                    for child in p.iter():
                        ptext_arr.append(child.get('text'))
                    pstr=''.join(ptext_arr)

                    # 严格规则 必须是4个数组 以大写字母开头 包含库存 以数字结尾
                    if pstr not in pstr_cache and len(ptext_arr)>=4 and pstr[0].isupper() and '库存' in pstr and pstr[-1].isdigit():
                        pstr_cache.append(pstr)
                        pstr_new_cache.append(pstr)
                        if callable(func_new_pstr_callback):
                            func_new_pstr_callback(pstr)
                        # 某些中文字符明文打印会导致莫名其妙退出!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # check slice is end
                r=find_node_by_reg(f'.//node[@text="{comp_node["text"]}"]')
                count+=1
                if len(r)>0:
                    si+=1
                    break
                run_hand(node_arr[i+1])
        # search input splice..
        elif node_arr[i]['type']=='search_input':
            input_str_arr=node_arr[i].get('value').split('@')
            new_node_info=copy.deepcopy(node_arr[i])
            new_val=input_str_arr[si%len(input_str_arr)]
            new_node_info['value']=new_val
            print('search val',f'"{new_val}"',si)
            run_hand(new_node_info)
            time.sleep(1)
        else:
            run_hand(node_arr[i])
    return si

def up_new_pstr(pstr):
    global server_host
    pobj={'pstrhex':pstr.encode('utf-8').hex(),'device':'device1','time':time.time()}
    url=f'http://{server_host}/py/flask_server/up_new_pstr?pobj={json.dumps(pobj)}'
    # r=requests.get(url)
    r=http_get_by_curl(url)
    print('up new pstr',pstr.encode('utf-8'),r.get('status_code'))

def main(server_ip,input_value_length,encode_str,atx_ip=''):
    global server_host,atx_host
    try:
        server_host=server_ip
        if not(not atx_host):
            atx_host=atx_ip
        # 将十六进制字符串转换回原始字符串
        decoded_str = bytes.fromhex(encode_str.replace('-', '')).decode('utf-8')
        nodes=json.loads(decoded_str)
        # check dump is ok
        if dump_by_atx():
            # 为了能刷新多部手机，需要input_value_length跟si结合使用
            si=0
            for i in range(input_value_length):
                si=run_hand_by_nodes(nodes,si=si)
            while True:
                si=run_hand_by_nodes(nodes,up_new_pstr,si)
        else:
            print('test dump is fail!')
    except Exception as e:
        traceback.print_exc()

waitcount=15
print(f'{waitcount}s后启动。。')
for t in range(waitcount):
    time.sleep(1)
    print(t)

# main(server_ip="192.168.1.37",input_value_length=2,atx_ip="192.168.1.28",encode_str="5b-7b-22-6c-61-62-65-6c-22-3a-22-e6-90-9c-e7-b4-a2-e6-8c-89-e9-92-ae-22-2c-22-74-79-70-65-22-3a-22-73-65-61-72-63-68-5f-6f-70-65-6e-22-2c-22-68-61-6e-64-5f-74-79-70-65-22-3a-22-63-6c-69-63-6b-22-2c-22-63-6c-61-73-73-22-3a-22-61-6e-64-72-6f-69-64-2e-77-69-64-67-65-74-2e-54-65-78-74-56-69-65-77-22-2c-22-62-6f-75-6e-64-73-22-3a-22-5b-31-37-34-2c-31-31-33-5d-5b-31-30-34-31-2c-32-31-32-5d-22-2c-22-72-65-73-6f-75-72-63-65-2d-69-64-22-3a-22-63-6f-6d-2e-61-69-68-75-69-73-68-6f-75-2e-6f-70-74-3a-69-64-2f-74-76-5f-73-65-61-72-63-68-22-7d-2c-7b-22-6c-61-62-65-6c-22-3a-22-e6-90-9c-e7-b4-a2-e8-be-93-e5-85-a5-22-2c-22-74-79-70-65-22-3a-22-73-65-61-72-63-68-5f-69-6e-70-75-74-22-2c-22-68-61-6e-64-5f-74-79-70-65-22-3a-22-69-6e-70-75-74-22-2c-22-63-6c-61-73-73-22-3a-22-61-6e-64-72-6f-69-64-2e-77-69-64-67-65-74-2e-45-64-69-74-54-65-78-74-22-2c-22-76-61-6c-75-65-22-3a-22-6f-70-70-6f-20-66-69-6e-64-20-78-40-e5-b0-8f-e7-b1-b3-31-31-22-2c-22-72-65-73-6f-75-72-63-65-2d-69-64-22-3a-22-63-6f-6d-2e-61-69-68-75-69-73-68-6f-75-2e-6f-70-74-3a-69-64-2f-65-74-5f-73-65-61-72-63-68-22-7d-2c-7b-22-6c-61-62-65-6c-22-3a-22-e6-90-9c-e7-b4-a2-e7-a1-ae-e8-ae-a4-22-2c-22-74-79-70-65-22-3a-22-73-65-61-72-63-68-5f-6f-6b-22-2c-22-68-61-6e-64-5f-74-79-70-65-22-3a-22-63-6c-69-63-6b-22-2c-22-63-6c-61-73-73-22-3a-22-61-6e-64-72-6f-69-64-2e-77-69-64-67-65-74-2e-54-65-78-74-56-69-65-77-22-2c-22-62-6f-75-6e-64-73-22-3a-22-5b-31-30-30-30-2c-32-32-30-30-5d-5b-31-30-30-30-2c-32-32-30-30-5d-22-2c-22-72-65-73-6f-75-72-63-65-2d-69-64-22-3a-22-22-7d-2c-7b-22-6c-61-62-65-6c-22-3a-22-e6-9f-a5-e6-89-be-22-2c-22-74-79-70-65-22-3a-22-63-68-65-63-6b-22-2c-22-68-61-6e-64-5f-74-79-70-65-22-3a-22-63-68-65-63-6b-22-2c-22-63-6c-61-73-73-22-3a-22-61-6e-64-72-6f-69-64-2e-77-69-64-67-65-74-2e-54-65-78-74-56-69-65-77-22-2c-22-72-65-73-6f-75-72-63-65-2d-69-64-22-3a-22-63-6f-6d-2e-61-69-68-75-69-73-68-6f-75-2e-6f-70-74-3a-69-64-2f-74-76-5f-66-6f-6f-74-65-72-5f-74-69-70-73-22-2c-22-74-65-78-74-22-3a-22-7e-e5-b7-b2-e7-bb-8f-e5-88-b0-e5-ba-95-e4-ba-86-7e-22-7d-2c-7b-22-6c-61-62-65-6c-22-3a-22-e6-bb-91-e5-8a-a8-22-2c-22-74-79-70-65-22-3a-22-73-6c-69-63-65-22-2c-22-68-61-6e-64-5f-74-79-70-65-22-3a-22-73-6c-69-63-65-22-2c-22-62-6f-75-6e-64-73-22-3a-22-5b-35-30-30-2c-32-30-30-30-5d-5b-35-30-30-2c-31-30-30-30-5d-22-2c-22-73-70-65-65-64-22-3a-30-2e-32-7d-5d")


