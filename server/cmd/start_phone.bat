chcp 65001

set _phone_ip=%1
set _port=%2
set _server_ip=%3

title phone %_phone_ip%:%_port%

echo %0 %_phone_ip% %_port% %_server_ip%...

adb -s %_phone_ip%:%_port% shell mkdir -p /sdcard/lcy/data

adb -s %_phone_ip%:%_port% push server\sh\start_loop.sh /sdcard/lcy/
adb -s %_phone_ip%:%_port% push server\sh\get_ui.sh /sdcard/lcy/
adb -s %_phone_ip%:%_port% push server\sh\simulation_click.sh /sdcard/lcy/
adb -s %_phone_ip%:%_port% push server\sh\loop_read_phone_data.sh /sdcard/lcy/
adb -s %_phone_ip%:%_port% push server\sh\data\phone_arr.txt /sdcard/lcy/data/

adb -s %_phone_ip%:%_port% shell sh /sdcard/lcy/start_loop.sh %_server_ip%
