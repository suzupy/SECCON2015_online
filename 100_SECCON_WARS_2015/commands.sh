ffmpeg -i SECCON\ WARS\ 2015.mp4 -r 1 images-%04d.jpeg
for i in $(seq -f %04g 27); do ls ./ | grep $i | xargs rm; done
for i in $(seq -f %04g 82 85); do ls ./ | grep $i | xargs rm; done
for file in $(ls ./*.jpeg); do convert $file images-0028.jpeg -compose lighten -composite images-0028.jpeg; done
open images-0028.jpeg
