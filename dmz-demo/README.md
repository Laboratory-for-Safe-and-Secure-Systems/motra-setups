Scripts and basic configuration to forward data from the OT side to the IT side. 
The base forwarders are designed to be included in the default water-treatement process as additional clients. 
The forwarder sends data from a local server over to a DMZ service (REDIS in our case). The IT side hosts an additional OPC server and an additional dashboard based on fuxa for configuration and visualization.

The bridge components are used to restart the default connections between all the setups, in case something breaks.