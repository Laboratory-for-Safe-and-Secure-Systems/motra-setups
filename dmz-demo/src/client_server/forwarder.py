import asyncio
import typer

from client_server.opcua_client import OPCUAConnectionManager
from client_server.redis_bridge import RedisBridge
from core.config import settings


# the forwarder is located in OT and forwarding to DMZ!
ot2dmz_ReadNodes = {
    "hist:tanklevel": "{ns0}:Devices/{ns0}:Sensors/{ns0}:S001/{ns0}:Measurement/{ns0}:FillLevel/{ns0}:Percent",
    "hist:valvestate": "{ns0}:Devices/{ns0}:Valves/{ns0}:V001/{ns0}:Output/{ns0}:D1/{ns0}:Active",
}

dmz2ot_WriteNodes = {
    "config:upperLimit": "{ns0}:Devices/{ns0}:Tanks/{ns0}:T001/{ns0}:Configuration/{ns0}:MaxLevelPercent",
    "config:lowerLimit": "{ns0}:Devices/{ns0}:Tanks/{ns0}:T001/{ns0}:Configuration/{ns0}:MinLevelPercent",
}


async def readOpcUaNodesTask(redis: RedisBridge, opcUa: OPCUAConnectionManager):

    while True:

        # a set of KV-parameters to forward from OPC to REDIS
        forward_data: dict = {key: 0 for key, _ in ot2dmz_ReadNodes.items()}

        if not opcUa.is_connected:
            typer.echo("Connection to OPC UA server is currently down ...")
            await asyncio.sleep(3)
            continue

        typer.echo("Forwarding measurement data: OPC >> DMZ")

        for node_key, path_template in ot2dmz_ReadNodes.items():
            node_path = path_template.format(ns0=opcUa.idx)

            # resolve the node reference on the remote server
            try:
                node_ref = await opcUa.client.nodes.objects.get_child(node_path)
            except Exception as err:
                typer.echo(err)
                typer.echo(f"Cannot resolve node path: {node_key}")
                await asyncio.sleep(1)
                break
            try:
                data = await node_ref.read_value()
            except Exception as err:
                typer.echo(err)
                typer.echo(f"Failed to read {node_key} from OPC server")
                await asyncio.sleep(1)
                break

            forward_data[node_key] = int(data)

        tasks = []
        for key, val in forward_data.items():
            # typer.echo(f"{key} {val}")
            if val is not None:
                tasks.append(redis.write(key, val))

        # perform all write operations using async (this should kick off the timeout handler)
        asyncio.gather(*tasks)

        # we forward historical data every 1s to the DMZ server
        await asyncio.sleep(1)


async def writeOpcUaNodesTask(redis: RedisBridge, opcUa: OPCUAConnectionManager):

    while True:

        tasks = []
        for key, _ in dmz2ot_WriteNodes.items():
            # pack the result into a dict to keep the keys and
            tasks.append(redis.read(key))

        # perform all read operations using async (this should kick off the timeout handler)
        result = await asyncio.gather(*tasks)
        updated_config_data = dict(zip([*dmz2ot_WriteNodes], result))

        if not opcUa.is_connected:
            typer.echo("Connection to OPC UA server is currently down ...")
            await asyncio.sleep(3)
            continue

        typer.echo("Forwarding configuration data: OPC << DMZ ")

        for node_key, value in updated_config_data.items():
            node_path = dmz2ot_WriteNodes[node_key].format(ns0=opcUa.idx)
            try:
                node_ref = await opcUa.client.nodes.objects.get_child(node_path)
            except Exception as err:
                typer.echo(err)
                typer.echo(f"Cannot resolve node path: {node_key}")

            try:
                # cast the remainder in case some float gets pushed
                await node_ref.write_value(float(value))
            except Exception as err:
                typer.echo(err)
                typer.echo(f"Failed to write {node_key} to local OPC server")

        # write configuration is only pushed every 3s
        await asyncio.sleep(3)


async def async_run_forwarder():

    # Connect to DMZ Redis
    bridge = RedisBridge(
        settings.ot_forwarder_redis_host,
        settings.ot_forwarder_redis_port,
    )

    opc_client = OPCUAConnectionManager(settings.ot_server_opcua_url)

    # Connect both with built-in retries
    await asyncio.gather(
        opc_client.connect(),
        bridge.connect(),
    )

    typer.echo("OT Bridge connected to OT Server and DMZ Redis")
    tasks = [
        asyncio.create_task(opc_client.keep_alive_monitor()),
        asyncio.create_task(readOpcUaNodesTask(bridge, opc_client)),
        asyncio.create_task(writeOpcUaNodesTask(bridge, opc_client)),
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(async_run_forwarder())
