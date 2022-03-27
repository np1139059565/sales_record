#!/bin/bash
echo $0 "$1" "$2" "$3"..

_server_ip=$1
_search_button="$2"
_search_str="$3"
_search_str_file="/sdcard/lcy/data/search_str.txt"
_swap_file="/sdcard/lcy/data/start_loop.swap"


#是否覆盖默认搜索字符串..
if [ -n "$_search_str" ];then
  echo cover search str $_search_str
  echo "$_search_str">$_search_str_file
fi

#初始化一次(不能删除,否则在对比数据时grep找不到数据)
echo ""> $_swap_file
_is_init_only=true


#进入循环..
while true;
do
  #遍历每个手机..
  while read -r _line
  do
    _search_str=$(echo $_line|awk -F ',' '{print $1}')
    _select_index=$(echo $_line|awk -F ',' '{print $2}')
    #搜索..
    sh /sdcard/lcy/simulation_click.sh "$_search_button" "$_search_str" $_select_index
    #读取长表格数据..
    sh /sdcard/lcy/loop_read_phone_data.sh $_is_init_only $_swap_file $_server_ip
  done < $_search_str_file
  if [ $_is_init_only ];then
    echo .................init is end.....................
    _is_init_only=false
  fi
  sleep 1;
done