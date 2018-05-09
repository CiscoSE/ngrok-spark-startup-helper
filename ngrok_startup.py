"""

Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

from __future__ import absolute_import, division, print_function

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

import requests
import json
import os
import sys

from requests.adapters import HTTPAdapter

# version
version = "1.0"

# ngrok URL

tunnels_api_uri = "/api/tunnels"

tunnel_delete_uri = "/api/tunnels/"

# spark developer token
dev_token = os.environ.get('SPARK_DEV_TOKEN')
webhook_base_url = "https://api.ciscospark.com/v1/webhooks"

webhook_request_headers = {"Accept" : "application/json","Content-Type":"application/json", "Authorization": "Bearer {}".format(dev_token)}


def get_tunnels_list(ngrok_base_url):
    print("get_tunnels_list start")
    error = ""
    active_tunnels = list()
    print(" Getting the list of tunnels...")
    tunnel_list_url = ngrok_base_url + tunnels_api_uri
    r = requests.get(tunnel_list_url, verify=False)
    print(" ...Received List of Tunnels...")

# get the json object from the response
    json_object = json.loads(r.text)

    tunnels = json_object['tunnels']

    if r.status_code==200:
        for potential_tunnel in tunnels:
#            if potential_tunnel['name'].find('(http)') == -1:
            active_tunnels.append(potential_tunnel)

    else:
        error=" Unable to list of tunnels"
    print("get_tunnels_list end")
    return active_tunnels,error

def delete_active_tunnels(tunnel_list, ngrok_base_url):
    print("delete_active_tunnels start")
    errors=list()
    tunnel_delete_base_url = ngrok_base_url + tunnel_delete_uri

    print(" beginning delete of tunnels...")
    for tunnel_to_delete in my_active_tunnels:
        tunnel_name = tunnel_to_delete['name']
        tunnel_delete_complete_url = tunnel_delete_base_url + tunnel_name

        delete_request = requests.delete(tunnel_delete_complete_url, verify=False)
        if delete_request.status_code != 204:
            errors.append("Error Deleting tunnel:  {}".format(tunnel_name))
    print(" ...ending delete of tunnels...")
    print("delete_active_tunnels end\n")
    return errors

def public_tunnel_for_name(tunnel_name, tunnel_port, ngrok_base_url):
    print("public_tunnel_for_name start")
    errors=list()
    public_tunnel = ()
    create_tunnel_url = ngrok_base_url + tunnels_api_uri
  
  #  make sure you change the port!!"
    print(" creating new tunnel...")
    tunnel_json = { 'addr' : tunnel_port, 'proto' : 'http', 'name' : tunnel_name}
    create_tunnel_response = requests.post(create_tunnel_url,json=tunnel_json,verify=False)
    if create_tunnel_response.status_code != 201:
        errors.append("Error creating tunnel:  {}".format(create_tunnel_response.status_code))
    else:
        jsonObject = json.loads(create_tunnel_response.text)
        public_tunnel = (jsonObject['public_url'],jsonObject['uri'])
    print(" ...done creating new tunnel")
    print("public_tunnel_for_name end\n")
    return public_tunnel,errors

def delete_prexisting_webhooks():
    print("delete_prexisting_webhooks start")
    errors=list()

    print(" deleting existing webhook...")
    webhooks_list_response =requests.get(webhook_base_url,headers=webhook_request_headers, verify=False)

    if webhooks_list_response.status_code != 200:
        errors.append("Error getting list of webhooks:  {}".format(webhooks_list_response.status_code))

    else:
        webhooks = json.loads(webhooks_list_response.text)['items']

        if len(webhooks) > 0:

            for webhook in webhooks:
                delete_webhook_url = webhook_base_url + '/' + webhook['id']
                delete_webhook_response = requests.delete(delete_webhook_url,headers=webhook_request_headers)
                if delete_webhook_response.status_code != 204:
                    errors.append("Delete Webhook Error code:  {}".format(delete_webhook_response.status_code))
    print(" ...Deleted existing webhooks")
    print("delete_prexisting_webhooks end\n")
    return errors

def update_webhook(webhook_request_json):
    print("update_webhook start")

    webhook_creation_response = requests.post(webhook_base_url, json=webhook_request_json,
                                              headers=webhook_request_headers)
    if webhook_creation_response.status_code == 200:
        print(' Webhook creation for new tunnel successful!')
    else:
        print(' Webhook creation for new tunnel was not successful.  Status Code: {}'.format(
            webhook_creation_response.status_code))

    print("update_webhook end\n")


if __name__ == "__main__":

    port = 10040
    requests.packages.urllib3.disable_warnings()
    tunnel_name = "myAppsTunnelName"

    if sys.argv[1] =='version':
        print('\n** ngrok-startup.py version:  {}\n'.format(version))
    else:
        port = sys.argv[1]
        tunnel_name = sys.argv[2]



    ngrok_base_url = "http://127.0.0.1:4040" # **** make sure you have the right port for your integration"
    # Get list of tunnels
    my_active_tunnels,tunnel_list_error = get_tunnels_list(ngrok_base_url)

    if tunnel_list_error:
        print("error getting tunnel list:  {}".format(tunnel_list_error))
        exit()

    #delete all the tunnels so we can start from scratch.
    delete_tunnels_error = delete_active_tunnels(my_active_tunnels, ngrok_base_url)
    if delete_tunnels_error:
        print("...Error Deleting tunnels:  {}".format(delete_tunnels_error))
        exit()

    #  Create a new tunnel
    demo_tunnel,errors = public_tunnel_for_name(tunnel_name, port, ngrok_base_url)
    if demo_tunnel[0] == "":
        print("  error:  {}".format(errors))

    errors = delete_prexisting_webhooks()



    if errors:
        print("Errors webhooks:  {}".format(errors))
        exit()

    #  create the new webhook with the new tunnel details.
    # to update a webhook.  We just need to make sure we keep the same name as a previous one
    webhook_target_url = demo_tunnel[0]
    webhook_request_json = {
        "resource": "messages",
        "event": "created",
        "targetUrl": webhook_target_url,
        "name": tunnel_name
    }
    update_webhook(webhook_request_json)






