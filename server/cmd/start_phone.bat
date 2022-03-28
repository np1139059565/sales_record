chcp 65001

set _device=%1
set _server_ip=%3
set _search_button=%4
set _search_str=%5

echo %0 %_device% %_port% %_server_ip% %_search_button%...

title phone %_device%

adb -s %_device% shell mkdir -p /sdcard/lcy/data

adb -s %_device% push server\sh\start_loop.sh /sdcard/lcy/
adb -s %_device% push server\sh\get_ui.sh /sdcard/lcy/
adb -s %_device% push server\sh\simulation_click.sh /sdcard/lcy/
adb -s %_device% push server\sh\loop_read_phone_data.sh /sdcard/lcy/
adb -s %_device% push server\sh\data\search_str.txt /sdcard/lcy/data/

adb -s %_device% shell sh /sdcard/lcy/start_loop.sh %_server_ip% '%_search_button%' '%_search_str%'
