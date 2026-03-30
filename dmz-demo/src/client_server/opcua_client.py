import asyncio
import typer
from asyncua import Client
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)


class OPCUAConnectionManager:
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self.client = Client(url=self.endpoint_url)
        self.uri: str = "urn:open62541.server.application"
        self.defaultns: int = 0
        self.is_connected = False
        self._subscriptions = []  # Keep track of subs to recreate them

    # Retry: Wait 2s, then 4s, 8s... up to 60s between attempts. Never stop trying.
    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=16),
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(10),
        before_sleep=lambda retry_state: typer.echo(
            f"Connection failed. Retrying in {retry_state.next_action.sleep}s..."
        ),
    )
    async def connect(self):
        typer.echo(f"Attempting connection to {self.endpoint_url}")

        try:
            await self.client.connect()
        except Exception as err:
            typer.echo(err)
            raise

        self.is_connected = True
        typer.echo("Successfully connected to OPC UA Server.")

        try:
            self.idx = await self.client.get_namespace_index(self.uri)
        except ValueError:
            typer.echo(
                f"Provided uri no present in server: {self.uri} \n Defaulting to ns0."
            )
            self.idx = 0

    async def write(self, data, node: tuple[str, str]):

        node_key, path_template = node
        node_path = path_template.format(ns0=self.idx)

        # resolve the node reference on the connected server
        try:
            node_ref = await self.client.nodes.objects.get_child(node_path)
        except:
            typer.echo(f"Cannot resolve node path: {node_key}")

        # try to update the provided value
        try:
            await node_ref.write_value(int(float(data)))
        except:
            typer.echo(f"Failed to send {node_key}!")

    async def read(self, node: tuple[str, str]) -> str | int | float | None:
        node_key, path_template = node
        node_path = path_template.format(ns0=self.idx)

        # resolve the node reference on the connected server
        try:
            node_ref = await self.client.nodes.objects.get_child(node_path)
        except:
            typer.echo(f"Cannot resolve node path: {node_key}")

        data = None

        # actually perform a read operation
        try:
            data = node_ref.read_value()
        except:
            typer.echo(f"Failed to read {node_key} from OPC server")

        return data

    async def keep_alive_monitor(self):
        """Runs in the background to detect silent drops."""
        while True:
            try:
                if self.is_connected:
                    # Read server time as a heartbeat
                    node_path = "{0}:Server/{0}:ServerStatus/{0}:CurrentTime".format(0)
                    sTime = await self.client.nodes.objects.get_child(node_path)
                    cTime = await sTime.read_value()
                    typer.echo(f"keep alive ping... @ {cTime}")
            except Exception as e:
                typer.echo(f"Connection lost: {e}")
                self.is_connected = False
                # Disconnect cleanly if possible, then trigger reconnect
                try:
                    await self.client.disconnect()
                except:
                    pass
                await self.connect()

            await asyncio.sleep(10)  # Check every 5 seconds
