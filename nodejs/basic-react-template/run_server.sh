#!/bin/sh
echo "${bearer_token}" > /usr/share/nginx/html/bearer_token
echo "${input}" > /usr/share/nginx/html/input_topic
echo "${Quix__Workspace__Id}" > /usr/share/nginx/html/workspace_id
echo "${Quix__Portal__Api}" > /usr/share/nginx/html/portal_api
echo "${processed}" > /usr/share/nginx/html/processed_topic
nginx -g "daemon off;"