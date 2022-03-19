::"d:\scrcpy gui\nircmd\nircmd.exe" sendmouse move -9999 9999
::"d:\scrcpy gui\nircmd\nircmd.exe" sendmouse move 60 50
::"d:\scrcpy gui\nircmd\nircmd.exe" sendmouse left click

"d:\scrcpy gui\nircmd\nircmd.exe" clipboard readfile "%1"
"d:\scrcpy gui\nircmd\nircmd.exe" sendkey ctrl down
"d:\scrcpy gui\nircmd\nircmd.exe" sendkey v down
"d:\scrcpy gui\nircmd\nircmd.exe" sendkey ctrl up
"d:\scrcpy gui\nircmd\nircmd.exe" sendkey v up
"d:\scrcpy gui\nircmd\nircmd.exe" sendkey enter down
"d:\scrcpy gui\nircmd\nircmd.exe" sendkey enter up
