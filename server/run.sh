#!/bin/bash 
COUNTER=1
while [  $COUNTER -gt 0 ]; do
	echo [RUNNING] The counter is $COUNTER 
	php teplo500.php --mode real --debug
 	let COUNTER=COUNTER+1 
done
