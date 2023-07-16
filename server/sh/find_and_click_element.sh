#!/bin/bash

# 函数：查找元素的坐标并执行点击
function find_and_click_element() {
  local resource_id="$1"
  local text="$2"
  local class_name="$3"

  # 下载 XML 文件
  curl -o dump.xml "http://192.168.1.37:8000/get_ui_by_uiautomator2/dump?device=78590ad7"

  # 使用 grep 提取坐标信息
  bounds=$(grep -oE 'bounds="\[(\d+,\d+)\]\[(\d+,\d+)\]"' dump.xml)

  # 读取坐标信息
  if [[ $bounds ]]; then
    # 提取左上角和右下角坐标
    IFS=',' read -ra coords <<< "$(echo $bounds | sed -E 's/bounds="\[|(\]\[)|\]"//g')"
    left_top=${coords[0]}
    right_bottom=${coords[1]}

    # 提取左上角和右下角坐标的具体值
    IFS=' ' read -ra left_top_coords <<< "$left_top"
    IFS=' ' read -ra right_bottom_coords <<< "$right_bottom"

    left=${left_top_coords[0]}
    top=${left_top_coords[1]}
    right=${right_bottom_coords[0]}
    bottom=${right_bottom_coords[1]}

    center_x=$(( ($left + $right) / 2 ))
    center_y=$(( ($top + $bottom) / 2 ))

    # 在坐标位置执行点击操作
    adb shell input tap $center_x $center_y

    echo "点击元素：$resource_id"
    echo "坐标位置：($center_x, $center_y)"
  else
    echo "未找到匹配的元素"
  fi

  # 清理临时文件
  rm -f dump.xml
}


find_and_click_element 'com.aihuishou.opt:id/tv_search' 'oppo find x' 'android.widget.TextView'