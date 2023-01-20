#!/bin/sh
echo "${Quix__Sdk__Token}" > /usr/share/nginx/html/sdk_token
echo "${Quix__Workspace__Id}" > /usr/share/nginx/html/workspace_id
echo "${Quix__Portal__Api}" > /usr/share/nginx/html/portal_api
echo "${topic}" > /usr/share/nginx/html/topic
echo "${eventTopic}" > /usr/share/nginx/html/eventTopic
nginx -g "daemon off;"