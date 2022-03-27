echo $0 $1 $2 $3 $4..

_search_button=$1
_search_str=$2
_select_index=$3
_clean_button=$4
_ui_sh_file="/sdcard/lcy/get_ui.sh"
_ui_swap_file="/sdcard/lcy/data/ui.swap"


#打开搜索框..
input tap 300 150
sleep 1;
input tap 300 150


#是否需要修改搜索内容..
if [ -n "$_search_str" ];then
  #计算清空按钮的坐标(可能不准确,建议使用传进来的坐标)..
  if [ -z "$_clean_button" ];then
    sh $_ui_sh_file "tv_cancel"
    _clean_button=$(sed -n 1'p' $_ui_swap_file|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
    _x=$(echo $_clean_button|awk -F ' ' '{print $1}')
    let _x-=75
    _y=$(echo $_clean_button|awk -F ' ' '{print $2}')
    let _y+=42
    _clean_button="$_x $_y"
  fi
  #清空旧搜索内容..
  input  tap $_clean_button
  input  tap $_clean_button
  #输入搜索内容(不能输入中文)..
  input text "$_search_str"
  sleep 1;
fi


#搜索按钮的坐标(可能不准确,建议使用传进来的坐标)..
if [ -z "$_search_button" ];then
  _search_button="1000 2200"
fi
echo search button pbound $_search_button
input tap $_search_button
sleep 1;

f_select_index(){
  while read _line
  do
    _pbound=$(sed -n $_line'p' $_ui_swap_file|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
    input tap $_pbound
  done
}

#是否打开品类型号选择框..
if [ -n "$_select_index" ];then
  #打开品类型号选择框
  sh $_ui_sh_file "tv_item"
  _pbound=$(sed -n 2'p' $_ui_swap_file|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
  input tap $_pbound
  sleep 1;
  #过滤品类型号
  sh $_ui_sh_file "tv_name"
  echo $_select_index|sed 's/~/\n/g'|f_select_index
  #确认
  sh $_ui_sh_file "tv_confirm"
  _pbound=$(sed -n 1'p' $_ui_swap_file|awk -F ']' '{print $1}'|awk -F '[' '{print $2}')
  input tap $_pbound
fi
