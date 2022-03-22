#打开搜索框..
_search_str=$1
input tap 300 150
sleep 1;

#删除旧搜索内容..
input  tap 800 150
input  tap 800 150

#输入搜索内容(不能输入中文)..
input text "$_search_str"
sleep 1;

#点击搜索..
input tap 1000 2200
sleep 1;

#是否打开品类型号选择框..
_filter_str=$2
_select_index=$3
if [ -n "$_filter_str" or "$_select_index" ]
then
  #打开品类型号选择框
  input tap 318 250
  sleep 1;
  #是否需要过滤品类型号
  if [ -n "$_filter_str" ]
  then
    sh /sdcard/lcy/get_ui.sh "tv_name"
    cat /sdcard/lcy/data/ui.swap2|grep "$_filter_str">/sdcard/lcy/data/simulation_click.swap
  fi
  #根据index选择对应的品类型号
  if [ -n "$_select_index" ]
  then
   _pbound=$(sed -n $_select_index'p' /sdcard/lcy/data/simulation_click.swap|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
   input tap $_pbound
  #确认
  sh /sdcard/lcy/get_ui.sh "tv_confirm"
  _pbound=$(sed -n 1'p' /sdcard/lcy/data/ui.swap2|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
  input tap $_pbound
fi