for i in {1..15}; do
  sips -s format png --resampleWidth 2550 "encoded_ts_doc-part-$i.pdf" --out "image$i.png"
done

for i in {1..15}; do
  deda_parse_print image$i.png  
done
