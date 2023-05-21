#!/usr/bin/env zsh

for i in {1..15}; do
  echo "Processing: top_secret_document-part-$i.pdf" 
  line=$(sed -n "${i}p" < encoded_flag.txt)
  deda_create_dots top_secret_document-part-$i.pdf --serial $line 
  mv new_dots.pdf encoded_ts_doc-part-$i.pdf
done
