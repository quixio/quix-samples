#!/bin/sh
echo "${sentiment}" > /usr/share/nginx/html/sentiment_topic
echo "${messages}" > /usr/share/nginx/html/messages_topic
nginx -g "daemon off;"