import xml.etree.ElementTree as ET
import sys
import json
import subprocess
import time
import copy
from urllib.parse import quote
import sys


port=''
ip=''
dump_xml=""
pstr_cache=[]

def http_get_by_curl(url):
    curl_cmd = 'curl -X GET -w "%{http_code}" '+f'"{quote(url, safe=":/?=&")}"'
    result = subprocess.Popen(
        curl_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8'
    )
    output, error = result.communicate()

    status_code=int(output.strip()[-3:])
    text=output.strip()[:-3]
    return {'status_code':status_code,'text':text}


def run_hand(device,node_info):
    url=f'http://localhost/py/get_ui_by_uiautomator2/{node_info["hand_type"]}?device={device}&node_info={json.dumps(node_info)}'
    # print('run hand',node_info['hand_type'],node_info)
    r=http_get_by_curl(url)
    return r

def dump(device):
    global dump_xml
    response = run_hand(device,{'hand_type':'dump'})
    if response.get('status_code') == 200:
        dump_xml=response.get('text')
    return response.get('status_code') == 200

def find_node_by_reg(reg=''):
    global dump_xml
    root_node = ET.fromstring(dump_xml)
    if not reg:
        return root_node
    else:
        # 查找任意深度的子元素'.//node[@id="111"]'
        # print('find node by reg:',reg)
        return root_node.findall(reg)




def run_hand_by_nodes(device,node_arr,func_new_pstr_callback=None,si=0):
    global pstr_cache
    pstr_new_cache=[]
    for i in range(len(node_arr)):
        # loop by check..
        if node_arr[i]['type']=='check':
            comp_node=node_arr[i]
            count=0
            while True:
                # refush dump,save cache
                dump(device)
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
                            del ptext_arr[2]
                            func_new_pstr_callback(''.join(ptext_arr),device)
                        # 某些中文字符明文打印会导致莫名其妙退出!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # check slice is end
                r=find_node_by_reg(f'.//node[@text="{comp_node["text"]}"]')
                count+=1
                if len(r)>0:
                    si+=1
                    break
                run_hand(device,node_arr[i+1])
        # search input splice..
        elif node_arr[i]['type']=='search_input':
            input_str_arr=node_arr[i].get('value').split('@')
            new_hand=copy.deepcopy(node_arr[i])
            new_val=input_str_arr[si%len(input_str_arr)]
            new_hand['value']=new_val
            print('search val',f'"{new_val}"',si)
            run_hand(device,new_hand)
            time.sleep(1)
        else:
            run_hand(device,node_arr[i])
    return si

def up_new_pstr(pstr,device):
    pobj={'pstrhex':pstr.encode('utf-8').hex(),'device':device,'time':time.time()}
    url=f'http://localhost/py/flask_server/up_new_pstr?pobj={json.dumps(pobj)}'
    # r=requests.get(url)
    r=http_get_by_curl(url)
    print('up new pstr',pstr.encode('utf-8'),r.get('status_code'))

def main():
    try:
        device=sys.argv[1]
        encode_str=sys.argv[2]
        input_value_length=int(sys.argv[3])
        # 将十六进制字符串转换回原始字符串
        decoded_str = bytes.fromhex(encode_str.replace('-', '')).decode('utf-8')
        nodes=json.loads(decoded_str)
        # check dump is ok
        if dump(device):
            # 为了能刷新多部手机，需要input_value_length跟si结合使用
            si=0
            for i in range(input_value_length):
                si=run_hand_by_nodes(device,nodes,si=si)
            while True:
                si=run_hand_by_nodes(device,nodes,up_new_pstr,si)
        else:
            print('test dump is fail!')
    except Exception as e:
        print(e)

main()

