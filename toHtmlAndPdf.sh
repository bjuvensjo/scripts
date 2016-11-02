#!/bin/bash

rm -rf html
rm -rf pdf

mkdir html
mkdir pdf

mds=$(find . -depth 1 -name "*md")

for md in ${mds}
do
    markdown=${md:2}
    html=${markdown%.md}.html
    pdf=${markdown%.md}.pdf

    echo $pdf

    markdown $markdown > html/$html
    wkhtmltopdf html/$html pdf/$pdf    
done
