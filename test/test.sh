export TEST_SERVER=http://localhost:8099
curl -X PUT -d x=3 -d y=5 -d value=on $TEST_SERVER/api/pixel
curl $TEST_SERVER/pixel-image.png -o pixel-image.png
if [ "$DISPLAY"	!= "" ]; then 
  xdg-open pixel-image.png
fi
