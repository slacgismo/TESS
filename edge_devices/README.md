# Instructions for GismoLab - Raspberry Pi PubSub with AWSIoTPyMQTT

## RPi Remote Connection
We are using teamviewer to remote connect and interact with the Raspberry Pi which is running the code tess_pubsub.py to publish the data received.

## MQTT TroubleShooting
1. Use the AWS MQTT test GUI on AWS console to see if a subscribed topic is returning any data. The topic name for TESS is "DeviceEvents" - if you are still experiencing trouble put "#" as the topic name which subscribes to all the topics in the account
2. If data is received on the MQTT Test client RPi is successfully publishing data and there is an issue with the code that subscribes to the topic
3. If there is nothing received - the problem is likely with the publishing script ran on R Pi, so contact a team member for remote connection parameters on teamviewer. Once connected to the R Pi, check for the script running on the terminal window. If it's hung/errored out - restart the the script. (Path: "~/Documents/TESS/AWSpubsub/tess_pubsub.py")
4. If there is empty data received, then the problem is likely with the inverter in which case contact one of the GISMo team members to fix the issue

## AWS Simple Notification Service (SNS)
Sns is used to subscribe to the topic RPi is publishing to. Subscribing to a topic is done using the https protocol and the endpoint is web/api/sns_read.py.
