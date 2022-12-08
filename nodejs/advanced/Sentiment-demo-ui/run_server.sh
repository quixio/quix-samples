#!/bin/sh
echo "${Quix__Workspace__Id}" > /usr/share/nginx/html/workspace_id
echo "${Quix__Sdk__Token}" > /usr/share/nginx/html/sdk_token
echo "${sentiment}" > /usr/share/nginx/html/sentiment_topic
echo "${messages}" > /usr/share/nginx/html/messages_topic
nginx -g "daemon off;"