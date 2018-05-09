# ngrok-startup

One of the nuisances of developing integrations or bots with ngrok is that the tunnel url changes everytime you fire up ngrok.  Then you have to manually update your spark webhook.
This script tears down all of your existing ngrok tunnels, creates new ones, then updates your Spark Bot webhook urls.

To use it simply type
```
python3 ngrok_startup.py <port> "tunnel_name"
```

Where *port* is the port ngrok is listening to and *tunnel_name* is the name of the tunnel you may have given it previously. Note that *tunnel_name* is also the name given to the Cisco Spark webhook.  So for example if the port was 10040 and the tunnel name was "my_tunnel_name", the command line argument would be:
```
python3 ngrok_startup.py 10040 "my_tunnel_name"
```