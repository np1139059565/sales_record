echo $0 "$1"...

_wres=0
_werr=0
_ui_file="/sdcard/lcy/data/ui.xml"
_swap_file="/sdcard/lcy/data/ui.swap"

_start_time=$(date '+%s')
#读取页面内容..
while [ $_wres -eq $_werr ]
do
  sleep 1
  echo "">$_ui_file
  _msg=$(uiautomator dump $_ui_file)
  _wres=$(echo $_msg|grep "UI hierchary dumped to:"|wc -l)
done

#过滤页面内容(_grep_str:tv_product_type_name|tv_name|tv_product_level|tv_sku_name|tv_price|tv_product_number)
_grep_str=$1
rm -rf $_swap_file

sed 's/<node/\n/g' $_ui_file |
grep -v 'text=""'|
awk -F 'text="' '{print $2}'|
awk -F 'resource-id="' '{print $1$2}'|
awk -F 'bounds="' '{print $2$1}'|
awk -F '"' '{print $1$3$2}'|
sed 's/,/ /g'|
sed 's/<\/node>//g'|
grep -E "$_grep_str">$_swap_file

_end_time=$(date '+%s')
echo read phone ui used time $((_end_time-_start_time)) s, line $(cat $_swap_file|wc -l)
