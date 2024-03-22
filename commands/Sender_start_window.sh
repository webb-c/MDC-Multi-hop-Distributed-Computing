#!/bin/bash

sleep_gaps="
1000
500
1000
"

sizes="

500
"

for size in $sizes; do

  for sleep_gap in $sleep_gaps; do
    python program/Sender.py --peer 192.168.1.6 --destination 192.168.1.6 --sleep_gap $sleep_gap --size $size --iterate 100 --mode upper --topic job/dnn_output
    sleep 1200
  done

done

for size in $sizes; do

  for sleep_gap in $sleep_gaps; do
    python program/Sender.py --peer 192.168.1.6 --destination 192.168.1.5 --sleep_gap $sleep_gap --size $size --iterate 100 --mode lower --topic job/dnn_output
    sleep 5
  done

done

for size in $sizes; do

  for sleep_gap in $sleep_gaps; do
    python program/Sender.py --peer 192.168.1.6 --destination 192.168.1.5 --sleep_gap $sleep_gap --size $size --iterate 100 --mode lower --topic job/dnn_output
    sleep 60
  done

done

for size in $sizes; do

  for sleep_gap in $sleep_gaps; do
    python program/Sender.py --peer 192.168.1.6 --destination 192.168.1.6 --sleep_gap $sleep_gap --size $size --iterate 100 --mode upper --topic job/dnn_output
    sleep 60
  done

done

for size in $sizes; do

  for sleep_gap in $sleep_gaps; do
    python program/Sender.py --peer 192.168.1.6 --destination 192.168.1.6 --sleep_gap $sleep_gap --size $size --iterate 100 --mode upper --topic job/dnn_output
    sleep 60
  done

done

for size in $sizes; do

  for sleep_gap in $sleep_gaps; do
    python program/Sender.py --peer 192.168.1.6 --destination 192.168.1.5 --sleep_gap $sleep_gap --size $size --iterate 100 --mode lower --topic job/dnn_output
    sleep 60
  done

done

for size in $sizes; do

  for sleep_gap in $sleep_gaps; do
    python program/Sender.py --peer 192.168.1.6 --destination 192.168.1.5 --sleep_gap $sleep_gap --size $size --iterate 100 --mode lower --topic job/dnn_output
    sleep 60
  done

done

for size in $sizes; do

  for sleep_gap in $sleep_gaps; do
    python program/Sender.py --peer 192.168.1.6 --destination 192.168.1.6 --sleep_gap $sleep_gap --size $size --iterate 100 --mode upper --topic job/dnn_output
    sleep 60
  done

done