echo $0 "$1"...

_wres=0
_werr=0

#读取页面内容..
while [ $_wres -eq $_werr ]
do
  sleep 1
  echo "">/sdcard/lcy/data/ui.xml
  _msg=$(uiautomator dump /sdcard/lcy/data/ui.xml)
  _wres=$(echo $_msg|grep "UI hierchary dumped to:"|wc -l)
done

#过滤页面内容到缓存..
echo "">/sdcard/lcy/data/ui.swap
sed 's/<node/\n/g' /sdcard/lcy/data/ui.xml |
grep -v 'text=""'|
awk -F 'text="' '{print $2}'|
awk -F 'resource-id="' '{print $1$2}'|
awk -F 'bounds="' '{print $2$1}'|
awk -F '"' '{print $1$3$2}'|
sed 's/,/ /g'|
sed 's/<\/node>//g'>/sdcard/lcy/data/ui.swap

#过滤内容..tv_product_type_name|tv_name|tv_product_level|tv_sku_name|tv_price|tv_product_number
echo "">/sdcard/lcy/data/ui.swap2
if [ -n "$1" ]
then
  _grep_str=$1
  cat /sdcard/lcy/data/ui.swap|grep -E "$_grep_str">/sdcard/lcy/data/ui.swap2
else
  cat /sdcard/lcy/data/ui.swap>/sdcard/lcy/data/ui.swap2
fi
