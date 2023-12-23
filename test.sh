clear
rm -f test-out/*.png

python3 retrographics.py test-in/doom.png test-out/doom-8,2.png
python3 retrographics.py test-in/doom.png test-out/doom-8,3.png   --cellcolors 3
python3 retrographics.py test-in/doom.png test-out/doom-8,8.png   --cellcolors 0
python3 retrographics.py test-in/doom.png test-out/doom-16,2.png  --masterpal cga
python3 retrographics.py test-in/doom.png test-out/doom-16,16.png --masterpal cga --cellcolors 0

python3 retrographics.py test-in/grad-hl.png test-out/grad-hl-16,2.png --masterpal cga
python3 retrographics.py test-in/grad-hs.png test-out/grad-hs-16,2.png --masterpal cga

python3 retrographics.py test-in/keen.png test-out/keen-8,2.png
python3 retrographics.py test-in/keen.png test-out/keen-8,3.png   --cellcolors 3
python3 retrographics.py test-in/keen.png test-out/keen-8,8.png   --cellcolors 0
python3 retrographics.py test-in/keen.png test-out/keen-16,2.png  --masterpal cga
python3 retrographics.py test-in/keen.png test-out/keen-16,16.png --masterpal cga --cellcolors 0
