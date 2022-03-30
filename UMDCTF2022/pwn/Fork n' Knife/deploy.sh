./build.sh
sudo docker build -t fnk .

sudo docker tag fnk registry.ctfd.io/umdctf/fnk
sudo docker push registry.ctfd.io/umdctf/fnk

rm -f fnk.zip
zip -r fnk.zip chall
