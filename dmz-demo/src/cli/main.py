import asyncio
from client_server.forwarder import async_run_forwarder
from client_server.it_opcua_server import it_server
import typer
from core.config import settings
from client_server.opcua_client import OPCUAConnectionManager
from client_server.mock_server import run_mock_server

app = typer.Typer(help="Data Forwarding Node CLI")


@app.command()
def start_forwarder():
    """Starts the data forwarding node."""
    # setup_logging()
    typer.echo(f"Starting forwarder. Source: {settings.ot_server_opcua_url}")

    try:
        # Bridge Typer (sync) to OPC UA (async)
        asyncio.run(async_run_forwarder())
    except KeyboardInterrupt:
        typer.echo("\nShutting down gracefully...")


@app.command()
def start_it_server():
    """Starts the data forwarding node."""
    # setup_logging()
    typer.echo(f"Starting IT OPC UA server.")

    try:
        # Bridge Typer (sync) to OPC UA (async)
        asyncio.run(it_server())
    except KeyboardInterrupt:
        typer.echo("\nShutting down gracefully...")


@app.command()
def mock_server(port: int = 4840):
    """Starts a dummy OPC UA server for local testing."""
    endpoint = f"opc.tcp://0.0.0.0:{port}/freeopcua/server/"
    try:
        asyncio.run(run_mock_server(endpoint))
    except KeyboardInterrupt:
        typer.echo("\nMock server stopped.")


if __name__ == "__main__":
    app()
