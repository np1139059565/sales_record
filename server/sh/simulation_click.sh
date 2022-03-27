echo $0 $1 $2 $3 $4..

_search_str=$1
_select_index=$2
_clean_button=$3
_search_button=$4
_ui_sh_file="/sdcard/lcy/get_ui.sh"
_ui_swap_file="/sdcard/lcy/data/ui.swap"


#打开搜索框..
input tap 300 150
sleep 1;


#计算清空按钮的坐标(可能不准确,建议使用传进来的坐标)..
if [ -z "$_clean_button" ];then
  sh $_ui_sh_file "tv_cancel"
  _clean_button=$(head -1 $_ui_swap_file|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
  _x=$(echo $_clean_button|awk -F ' ' '{print $1}')
  let _x-=75
  _y=$(echo $_clean_button|awk -F ' ' '{print $1}')
  let _y+=42
  _clean_button="$_x $_y"
fi
#清空旧搜索内容..
input  tap $_clean_button
input  tap $_clean_button

#输入搜索内容(不能输入中文)..
input text "$_search_str"
sleep 1;

#搜索按钮的坐标(可能不准确,建议使用传进来的坐标)..
if [ -z "$_search_button" ];then
  _search_button="1000 2200"
fi
input tap $_search_button
sleep 1;

#是否打开品类型号选择框..
if [ -n "$_select_index" ];then
  #打开品类型号选择框
  sh $_ui_sh_file "tv_item"
  _pbound=$(head -2 $_ui_swap_file|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
  input tap $_pbound
  sleep 1;
  #过滤品类型号
  sh $_ui_sh_file "tv_name"
  _pbound=$(sed -n $_select_index'p' $_ui_swap_file|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
  input tap $_pbound
  #确认
  sh $_ui_sh_file "tv_confirm"
  _pbound=$(head -1 $_ui_swap_file|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
  input tap $_pbound
fi
