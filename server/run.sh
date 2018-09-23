#!/bin/bash 
COUNTER=1
while [  $COUNTER -gt 0 ]; do
	echo [RUNNING] The counter is $COUNTER 
	python teplo500.py --mode real --debug
 	let COUNTER=COUNTER+1 
done
