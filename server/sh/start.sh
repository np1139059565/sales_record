_ip=$1
_port=$2
_server_ip=$3
#curl "$_server_ip/py/phone_heart?ip=$_ip&port=$_port"

while true;
do
  #清空缓存
  #echo "">/sdcard/lcy/data/start.swap
  #遍历每个手机..
  while read -r _phone_info
  do
    _search_str=$(echo $_phone_info|awk -F ',' '{print $1}')
    _filter_str=$(echo $_phone_info|awk -F ',' '{print $2}')
    _select_index=$(echo $_phone_info|awk -F ',' '{print $3}')
    #模拟点击搜索..
    sh /sdcard/lcy/simulation_click.sh "$_search_str" "$_filter_str" "$_select_index"
    #循环读取长表格..
    sh /sdcard/lcy/loop_read_phone_data.sh
    cat /sdcard/lcy/data/phone_data.swap>>/sdcard/lcy/data/start.swap
  done < /sdcard/lcy/data/phone_arr.txt
  #all phone data
  cat /sdcard/lcy/data/phone_data.swap>/sdcard/lcy/data/start.swap2
  sleep 1;
done