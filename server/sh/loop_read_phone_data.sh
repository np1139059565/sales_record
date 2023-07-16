echo $0 "$1" "$2" "$3"..

_is_init=$1
_long_swap_file=$2
_server_ip=$3
_ui_swap_file="/sdcard/lcy/data/ui.swap"
_ui_sh_file="/sdcard/lcy/get_ui.sh"
_phone_data_file="/sdcard/lcy/data/phone_data.swap"
_phone_new_line_file="/sdcard/lcy/data/phone_data.swap2"
_phone_sort_file="/sdcard/lcy/data/phone_data.swap3"

_start_time=$(date '+%s')
_heart_last_time=$(date '+%s')
#读取全屏数据
f_read_phone_data(){
  rm -rf $_phone_new_line_file
  #将多行数据合并整理
  curl -o dump.xml "http://192.168.1.37:8000/get_ui_by_uiautomator2/dump?device=78590ad7"
  cat $_ui_swap_file|tr "\n[" "/>"|
  sed 's/tv_product_level/\ntv_product_level/g'|
  grep -E 'tv_product_level.*tv_sku_name.*tv_price.*tv_product_number'|
  awk -F '/>' '{print $2$4$6$8}'|f_filter_new_line>>$_phone_data_file
  #心跳
  _heart_time=$(($(date '+%s')-_heart_last_time))
  if [ $_heart_time -gt 6 ];then
    _heart_last_time=$(date '+%s')
    curl -X GET "$_server_ip:5000/phone_heart"
  fi
  #判断是否存在新数据
  if [ $_is_init == false -a  -f $_phone_new_line_file ];then
    #发送到服务端
    _all_line_b64=$(echo $(cat $_phone_new_line_file|tr "\n" "$")|f_myb64)
    curl -X POST -d "$_all_line_b64" "$_server_ip/py/add_monitor_child"
  fi
}

#将数据转成base64并禁止换行
f_myb64(){
  while read _line
  do
    echo $(echo $_line|base64 -w 0)
  done
}

#过滤新数据
f_filter_new_line(){
  while read _line
  do
    _spline=$(echo $_line|sed 's/\/$//g'|awk -F '¥' '{print $1}')
    #缓存是否存在此条数据
    _comp_count=$(grep -c "^$_spline" $_long_swap_file)
    if [ $_comp_count == 0 ];then
      #收集新数据
      echo $_line>>$_phone_new_line_file
      #追加到缓存中
      echo $_line>>$_long_swap_file
    else
      #对比库存数据
      _new_kc=$(echo $_line|awk -F ' ' '{print $NF}')
      _max_kc=$(grep "^$_spline" $_long_swap_file|awk -F ' ' '{print $NF}'|sort -nr|head -1)
      if [ $_new_kc -ne $_max_kc ];then
        echo update kc $_new_kc $_max_kc..
        #更新缓存中的库存
        sed -i "/^$_spline/c\\$_line" $_long_swap_file
        #库存增加时属于新数据
        if [ $_new_kc -gt $_max_kc ];then
          #收集新数据
          echo $_line>>$_phone_new_line_file
        fi
      fi
    fi
      
    #返回数据到管道
    echo $_line
  done
}

#把滑动的数据拼接成表格
rm -rf $_phone_data_file
while [[ $_isbootom != 1 ]]
do
  f_read_phone_data
  input swipe 400 2000 400 1200
  _isbootom=$(cat $_ui_swap_file|grep "/tv_footer_tips"|wc -l)
done

#去重..
sort -n $_phone_data_file|uniq>$_phone_sort_file
cat $_phone_sort_file>$_phone_data_file
#将所有数据追加到总缓存
if [ $_is_init ];then
  echo copy data to long swap..
  cat $_phone_data_file>>$_long_swap_file
fi

#time
_end_time=$(date '+%s')
echo read phone data used time $((_end_time-_start_time)) s, line $(cat $_phone_data_file|wc -l)