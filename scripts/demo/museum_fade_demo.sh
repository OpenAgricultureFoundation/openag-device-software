#/bin/bash

# For a long running fade demo, call this script (by full path) from the debian
# users account with: "crontab -e" and add the following lines, 
# just make sure the last line is NOT commented out!

# Restart fade every hour
# m h  dom mon dow   command
# */60 * * * * /home/debian/scripts/demo/museum_fade_demo.sh


# Set this variable depending on which branch of the code you are running:
# pfc3-rack-20-test branch brain is on 80
# master branch brain is on port 8000
#HOST=localhost
HOST=localhost:8000

LOGIN_URL=http://$HOST/accounts/login/?next=/
YOUR_USER='openag'
YOUR_PASS='openag'
COOKIES=cookies.txt
CURL_BIN="curl -s -c $COOKIES -b $COOKIES -e $LOGIN_URL"

# saves the cookies.txt file
echo 'Getting CSRF cookie...'
$CURL_BIN $LOGIN_URL > /dev/null

# get the token from the file:
#   grep the line in the file that has the token,
#   reverse all the chars in the line to put the token as the first word,
#   cut the first field from the tab separated line,
#   un-reverse the chars in the token
CSRF=`grep csrftoken $COOKIES | rev | cut -f 1 | rev`
DJANGO_TOKEN="csrfmiddlewaretoken=$CSRF"

# perform login 
echo 'Logging in...'
$CURL_BIN \
    -d "$DJANGO_TOKEN&username=$YOUR_USER&password=$YOUR_PASS" \
    --cookie "csrftoken=$CSRF" \
    -X POST $LOGIN_URL

# put LED peripheral in manual mode
REST_URL=http://$HOST/api/led/manual/
REST_METHOD=POST
POST_DATA='{}'
echo "CALLING REST API: $REST_URL"
RET=`$CURL_BIN -X $REST_METHOD $REST_URL -H "X-CSRFToken: $CSRF" -H "Content-Type: application/json" -d "$POST_DATA" --cookie "csrftoken=$CSRF"`
echo $RET
sleep 2
echo ''

# turn LED off
REST_URL=http://$HOST/api/led/turn_off/
REST_METHOD=POST
POST_DATA=''
echo "CALLING REST API: $REST_URL"
RET=`$CURL_BIN -X $REST_METHOD $REST_URL -H "X-CSRFToken: $CSRF" -H "Content-Type: application/json" -d "$POST_DATA" --cookie "csrftoken=$CSRF"`
echo $RET
sleep 2
echo ''

# fade LED 
REST_URL=http://$HOST/api/led/fade/
REST_METHOD=POST
POST_DATA=''
echo "CALLING REST API: $REST_URL"
RET=`$CURL_BIN -X $REST_METHOD $REST_URL -H "X-CSRFToken: $CSRF" -H "Content-Type: application/json" -d "$POST_DATA" --cookie "csrftoken=$CSRF"`
echo $RET
echo ''

# logout
rm $COOKIES


