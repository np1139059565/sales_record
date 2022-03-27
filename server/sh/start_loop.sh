#!/bin/bash
echo $0 $1..

_server_ip=$1
_swap_file="/sdcard/lcy/data/start_loop.swap"
_phone_arr_file="/sdcard/lcy/data/phone_arr.txt"

#初始化一次
rm -rf $_swap_file
_is_init_only=true

while true;
do
  #遍历每个手机..
  while read -r _line
  do
    _search_str=$(echo $_line|awk -F ',' '{print $1}')
    _select_index=$(echo $_line|awk -F ',' '{print $2}')
    #搜索..
    sh /sdcard/lcy/simulation_click.sh "$_search_str" $_select_index
    #读取长表格数据..
    sh /sdcard/lcy/loop_read_phone_data.sh $_is_init_only $_swap_file $_server_ip
  done < $_phone_arr_file
  _is_init_only=false
  #heart..
  curl -X GET -d "$_server_ip:5000/phone_heart"
  sleep 1;
done