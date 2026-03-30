import typer  # for logging

import asyncio
from asyncua import Server, ua, uamethod
from client_server.redis_bridge import RedisBridge

from core.config import settings


async def read_historical_data(
    opc_server,  # OPC UA server reference
    redis: RedisBridge,
):
    """
    Reads a list of historical nodes and forwards data to REDIS
    """

    active_namespace = await opc_server.register_namespace(
        "urn:open62541.server.application"
    )
    objects = opc_server.nodes.objects

    # Historical Nodes (Readable)
    hist_folder = await objects.add_folder(active_namespace, "History")
    hist1 = await hist_folder.add_variable(active_namespace, "History_FillLevel", 0)
    hist2 = await hist_folder.add_variable(active_namespace, "History_ValveState", 0)

    await opc_server.historize_node_data_change(hist1, period=None, count=100)
    await opc_server.historize_node_data_change(hist2, period=None, count=100)

    # forward any value from redis to the local server namespace
    while True:
        typer.echo("Query data from REDIS...")

        val1 = None
        val2 = None

        try:
            val1 = await redis.read("hist:tanklevel")
            val2 = await redis.read("hist:valvestate")
        except:
            # redis has built in backoff and connection retry
            # just ignore value updates, if connection is down and retry later
            typer.echo("Failed to get data from REDIS")

        if val1 is not None:
            typer.echo(f"Updating tanklevel: {val1}")
            await hist1.write_value(int(float(val1)))

        if val2 is not None:
            typer.echo(f"Updating valvestate: {val2}")
            await hist2.write_value(int(float(val2)))

        await asyncio.sleep(3)


async def forward_configuration_data(
    opc_server: Server,  # OPC UA server reference
    redis: RedisBridge,
):
    """
    Forwards records from Fuxa and writes new config to REDIS.
    Does currently ignore settings from inside the OT side!
    """

    active_namespace = await opc_server.register_namespace(
        "urn:open62541.server.application"
    )
    objects = opc_server.nodes.objects

    # Create Nodes
    # 1. Config Nodes (Writable)
    typer.echo("creating server address space")
    config_folder = await objects.add_folder(active_namespace, "Configuration")
    config1 = await config_folder.add_variable(
        active_namespace, "Config_UpperLimitTank", 0
    )
    config2 = await config_folder.add_variable(
        active_namespace, "Config_LowerLimitTank", 0
    )
    await config1.set_writable()
    await config2.set_writable()

    while True:
        typer.echo("pushing values to the DMZ")
        val1 = await config1.read_value()
        val2 = await config2.read_value()

        try:
            await redis.write("config:upperLimit", val1)
            await redis.write("config:lowerLimit", val2)
        except Exception as err:
            # redis has built in backoff and connection retry
            # just ignore value updates, if connection is down and retry later
            typer.echo("Failed to write data to REDIS")
            typer.echo(err)

        await asyncio.sleep(3)


async def it_server():
    bridge = RedisBridge(settings.it_server_redis_host, settings.it_server_redis_port)
    # await bridge.r.ping()

    server = Server()
    await server.init()
    server.socket_address = ("0.0.0.0", 4840)
    server.set_endpoint(settings.it_server_opcua_url)
    server.set_server_name("KRITIS3M IT Server")
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
        ]
    )

    async with server:
        typer.echo(f"OPC UA Server started at {settings.it_server_opcua_url}")
        typer.echo(f"Starting history and config tasks")
        tasks = [
            asyncio.create_task(forward_configuration_data(server, bridge)),
            asyncio.create_task(read_historical_data(server, bridge)),
        ]

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(it_server())
    except KeyboardInterrupt:
        typer.echo("Server stopped.")
