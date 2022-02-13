#!/bin/bash
if [ -s Desktop/Retina/testlog.log ];
then
	echo "Log file is not empty"
else
	python3 ~/Desktop/Retina/blink_detection.py
fi
str=$( tail -n 1 Desktop/Retina/testlog.log )
        last=${str: -2}
        echo $last
        >Desktop/Retina/testlog.log
        echo $str>Desktop/Retina/testlog.log
        crontab -r
        (crontab -l; echo "*/$last * * * * python3 ~/Desktop/Retina/blink_detection.py && ./blink.sh")|awk '!x[$0]++'|crontab -

