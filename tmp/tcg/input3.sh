input3=`pm path com.sigma_rt.tcg`
export CLASSPATH=${input3#*:}
exec app_process /system/bin com.ma2phone.inputeventsinjector.Main '-p 12019' &
