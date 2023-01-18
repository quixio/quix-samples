#!/bin/sh
echo "${Quix__Sdk__Token}" > /usr/share/nginx/html/sdk_token
echo "${Quix__Workspace__Id}" > /usr/share/nginx/html/workspace_id
echo "${webcam_output}" > /usr/share/nginx/html/topic_raw
echo "${Quix__Portal__Api}" > /usr/share/nginx/html/portal_api
nginx -g "daemon off;"
