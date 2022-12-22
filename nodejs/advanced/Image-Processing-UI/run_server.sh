#!/bin/sh
echo "${Quix__Sdk__Token}" > /usr/share/nginx/html/sdk_token
echo "${Quix__Workspace__Id}" > /usr/share/nginx/html/workspace_id
echo "${Quix__Portal__Api}" > /usr/share/nginx/html/portal_api
echo "${processed}" > /usr/share/nginx/html/processed_topic
nginx -g "daemon off;"