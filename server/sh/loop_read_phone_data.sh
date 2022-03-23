_is_init=$1
_all_swap_file=$2
_server_ip=$3

echo $0 $_is_init $_all_swap_file $_server_ip...

_new_line_file="/sdcard/lcy/data/phone_data.swap"
_long_length_file="/sdcard/lcy/data/phone_data.swap2"
_ui_swap_file2="/sdcard/lcy/data/ui.swap2"

_start_time=$(date '+%s')
#读取全屏数据
f_read_phone_data(){
  #将多行数据合并整理
  rm -rf $_new_line_file
  sh /sdcard/lcy/get_ui.sh
  cat $_ui_swap_file2|tr "\n[" "/>"|
  sed 's/tv_product_level/\ntv_product_level/g'|
  grep -E 'tv_product_level.*tv_sku_name.*tv_price.*tv_product_number'|
  awk -F '/>' '{print $2$4$6$8}'|f_check_line_data
  #判断是否存在新数据
  if [ -f $_new_line_file ];then
    #去重
    sort -n $_new_line_file|uniq>$_new_line_file
    #追加到总缓存中
    cat $_new_line_file>>$_all_swap_file
    #发送到服务端
    _all_line_b64=$(echo $(cat $_new_line_file|tr "\n" "$")|f_myb64)
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
#检查每行数据
f_check_line_data(){
  while read _line
  do
    #收集数据
    echo $_line>>$_long_length_file
    #非初始化时
    if [ $_is_init == false ];then
      #查找总缓存表的数据
      _comp_count=$(grep -c "^$_line$" $_all_swap_file)
      #收集新数据
      if [ $_comp_count == 0 ];then
        echo $_line>>$_new_line_file
      fi
    fi
  done
}

#把很长的表格数据拼接成一个文件
rm -rf $_long_length_file
while [[ $_isbootom != 1 ]]
do
  f_read_phone_data
  echo swipe..
  input swipe 400 2000 400 1200
  _isbootom=$(cat $_ui_swap_file2|grep "/tv_footer_tips"|wc -l)
done

#去重..
sort -n $_long_length_file|uniq>$_long_length_file
#初始化时将所有数据追加到总缓存
if [ $_is_init ];then
  echo init..................... $_is_init
  cat $_long_length_file>>$_all_swap_file
fi

#time
_end_time=$(date '+%s')
echo read phone data used time $((_end_time-_start_time)) s, line $(cat $_long_length_file|wc -l)