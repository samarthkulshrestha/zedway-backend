#!/bin/bash

FINDJPG=`find . -type f -iname *.jpg`
FINDJPEG=`find . -type f -iname *.jpeg`
FILES="$FINDJPG $FINDJPEG"
for f in $FILES
do
  echo "Optimizing" $f
  jpegoptim $f  >> jpegoptimLog
done

FINDPNG=`find . -type f -iname *.png`
FILES=$FINDPNG
for f in $FILES
do
  echo "Optimizing" $f
  optipng $f # >> optipngLog
done
