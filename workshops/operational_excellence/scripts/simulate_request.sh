#!/bin/bash

while :
do
    ab -p encrypt_data.json -n 60000 -c 3000 $ALBEndpoint/encrypt
done