#!/bin/bash
echo $0 "$1"..

_server_ip=$1

_all_swap_file="/sdcard/lcy/data/start_loop.swap"
_phone_arr_file="/sdcard/lcy/data/phone_arr.txt"
#清空缓存
_is_init_only=true
rm -rf $_all_swap_file

while true;
do
  #遍历每个手机..
  while read -r _phone_info
  do
    _search_str=$(echo $_phone_info|awk -F ',' '{print $1}')
    _filter_str=$(echo $_phone_info|awk -F ',' '{print $2}')
    _select_index=$(echo $_phone_info|awk -F ',' '{print $3}')
    #搜索..
    sh /sdcard/lcy/simulation_click.sh "$_search_str" "$_filter_str" "$_select_index"
    #读取长表格数据..
    sh /sdcard/lcy/loop_read_phone_data.sh $_is_init_only $_all_swap_file $_server_ip
  done < $_phone_arr_file
  _is_init_only=false
  sleep 1;
done