import asyncio
import typer
from asyncua import Server

import logging

server_logger = logging.getLogger("asyncua")
server_logger.setLevel(logging.WARNING)

ot2dmz_ReadNodes = {
    "hist:tanklevel": "{ns0}:Devices/{ns0}:Sensors/{ns0}:S001/{ns0}:Measurement/{ns0}:FillLevel/{ns0}:Percent",
    "hist:valvestate": "{ns0}:Devices/{ns0}:Valves/{ns0}:V001/{ns0}:Output/{ns0}:D1/{ns0}:Active",
}

dmz2ot_WriteNodes = {
    "config:upperLimit": "{ns0}:Devices/{ns0}:Tanks/{ns0}:T001/{ns0}:Configuration/{ns0}:MaxLevelPercent",
    "config:lowerLimit": "{ns0}:Devices/{ns0}:Tanks/{ns0}:T001/{ns0}:Configuration/{ns0}:MinLevelPercent",
}


async def run_mock_server(endpoint: str = "opc.tcp://0.0.0.0:4840/"):
    server = Server()
    await server.init()
    server.set_endpoint(endpoint)

    # Set up a dummy namespace and variable
    idx = await server.register_namespace("urn:open62541.server.application")

    myobj = await server.nodes.objects.add_object(idx, "TestData")
    myvar = await myobj.add_variable(idx, "TestSensor", 0.0)
    await myvar.set_writable()  # Allow your forwarder to write to it if needed

    server_logger.setLevel(logging.INFO)

    async with server:
        typer.echo(f"Mock OPC UA Server started at {endpoint}")
        count = 0
        while True:
            await asyncio.sleep(1)
            count += 1
            # Simulate changing data that your forwarder can read
            await myvar.write_value(float(count))
