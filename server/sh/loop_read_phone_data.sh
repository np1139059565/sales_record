p=p

f_read_phone_data(){
  cat /sdcard/lcy/data/ui.swap2|tr "\n[" "/>"|
  sed 's/tv_product_level/\ntv_product_level/g'|
  grep -E 'tv_product_level.*tv_sku_name.*tv_price.*tv_product_number'|
  awk -F '/>' '{print $2$4$6$8}'>>/sdcard/lcy/data/phone_data.swap
}

echo "">/sdcard/lcy/data/phone_data.swap
while [[ $_bootom != 1 ]]
do
  f_read_phone_data
  echo swipe..
  input swipe 400 2000 400 1200
  _bootom=$(cat /sdcard/lcy/data/ui.swap2|grep "/tv_footer_tips"|wc -l)
done

f_read_phone_data

echo all conter1 to phone_data.swap
cat /sdcard/lcy/data/bak4.text>/sdcard/lcy/data/phone_data.swap