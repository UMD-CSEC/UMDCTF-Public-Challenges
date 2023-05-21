#!/bin/bash

for i in {1..200}
do
  filename="file$i.txt"
  echo "$filename" > "./website/public/files/$filename"
done
