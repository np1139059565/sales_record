set _phone_ip=%1
set _port=%2
set _server_ip=%3

adb -s %_phone_ip%:%_port% shell mkdir -p /sdcard/lcy/data

adb -s %_phone_ip%:%_port% push server\sh\getui.sh /sdcard/lcy/
adb -s %_phone_ip%:%_port% push server\sh\heart.sh /sdcard/lcy/

adb -s %_phone_ip%:%_port% shell sh /sdcard/lcy/heart.sh %_phone_ip% %_port% %_server_ip%
