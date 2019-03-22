#/bin/bash

# curl -X POST -H "Authorization: JWT YourToken" -d "field=value&field=value" 'http://127.0.0.1:80/dashboard/' 

LOGIN_URL=http://localhost/accounts/login/?next=/
YOUR_USER='openag'
YOUR_PASS='openag'
COOKIES=cookies.txt
CURL_BIN="curl -s -c $COOKIES -b $COOKIES -e $LOGIN_URL"

# saves the cookies.txt file
$CURL_BIN $LOGIN_URL > /dev/null

# get the token from the file:
#   grep the line in the file that has the token,
#   reverse all the chars in the line to put the token as the first word,
#   cut the first field from the tab separated line,
#   un-reverse the chars in the token
CSRF=`grep csrftoken $COOKIES | rev | cut -f 1 | rev`
DJANGO_TOKEN="csrfmiddlewaretoken=$CSRF"

# perform login 
$CURL_BIN \
    -d "$DJANGO_TOKEN&username=$YOUR_USER&password=$YOUR_PASS" \
    -X POST $LOGIN_URL

# put LED peripheral in manual mode
REST_URL=http://localhost/api/led/manual/
REST_METHOD=POST
POST_DATA=''
echo "CALLING REST API: $REST_URL"
$CURL_BIN -X $REST_METHOD $REST_URL -H "X-CSRFToken: $CSRF" -H "Content-Type: application/json" -d "$POST_DATA"
echo ''
echo 'sleeping 1 sec'
sleep 1

# set LED peripheral channel to blue
REST_URL=http://localhost/api/led/set_channel/
REST_METHOD=POST
POST_DATA='{"channel":"B","percent":"50"}'
echo "CALLING REST API: $REST_URL"
$CURL_BIN -X $REST_METHOD $REST_URL -H "X-CSRFToken: $CSRF" -H "Content-Type: application/json" -d "$POST_DATA"
echo ''
echo 'sleeping 1 sec'
sleep 1

# turn LED off
REST_URL=http://localhost/api/led/turn_off/
REST_METHOD=POST
POST_DATA=''
echo "CALLING REST API: $REST_URL"
$CURL_BIN -X $REST_METHOD $REST_URL -H "X-CSRFToken: $CSRF" -H "Content-Type: application/json" -d "$POST_DATA"
echo ''
echo 'sleeping 1 sec'
sleep 1

# fade LED 
REST_URL=http://localhost/api/led/fade/
REST_METHOD=POST
POST_DATA=''
echo "CALLING REST API: $REST_URL"
$CURL_BIN -X $REST_METHOD $REST_URL -H "X-CSRFToken: $CSRF" -H "Content-Type: application/json" -d "$POST_DATA"
echo ''
echo 'sleeping 5 secs'
sleep 5

# reset LED peripheral 
REST_URL=http://localhost/api/led/reset/
REST_METHOD=POST
POST_DATA=''
echo "CALLING REST API: $REST_URL"
$CURL_BIN -X $REST_METHOD $REST_URL -H "X-CSRFToken: $CSRF" -H "Content-Type: application/json" -d "$POST_DATA"

# logout
#rm $COOKIES


# use with GET
#REST_METHOD=GET
#REST_URL=http://localhost/api/iot/info/
#REST_URL=http://localhost/api/state/
#REST_URL=http://localhost/api/

