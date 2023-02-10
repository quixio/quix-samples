#!/bin/sh
echo "${BearerToken}" > /my-app/api/bearer_token
echo "${Quix__Workspace__Id}" > /my-app/api/workspace_id
echo "${Quix__Portal__Api}" > /my-app/api/portal_api

node main.js
