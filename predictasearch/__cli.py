import json
import os
from typing import Optional, List, Dict

import rich_click as click

from .__api import PredictaSearch


client = PredictaSearch(api_key=os.environ.get("PREDICTA_API_KEY"))

def parse_network_filters(value: Optional[str]) -> Optional[List[str]]:
    """
    Parse a comma-separated string into a list of network names.

    :param value: A string of comma-separated network names (e.g., "facebook,linkedin")
    :return: A list of cleaned network names or None if no input provided
    :rtype: Optional[List[str]]
    """
    if value is None:
        return None
    return [network.strip() for network in value.split(",") if network.strip()]


@click.group()
@click.option(
    "--filter",
    type=str,
    help="A comma-separated "
         "list of networks to filter the (email|phone) search (e.g., facebook,linkedin)."
)
@click.pass_context
def cli(ctx: click.Context, filter: Optional[str]):
    """
    PredictaSearch CLI

    Get the digital footprint from an email or phone number.
    """
    ctx.ensure_object(dict)
    ctx.obj["filter"] = filter


@cli.command()
@click.argument("email", type=str)
@click.pass_context
def email(ctx: click.Context, email: str):
    """
    Search for a digital footprint using an EMAIL address.

    e.g., predictasearch email johndoe@gmail.com --filter facebook,linkedin
    """
    parsed_networks: Optional[List[str]] = parse_network_filters(value=ctx.obj["filter"])
    results: List = client.search_by_email(email=email, networks=parsed_networks)
    click.echo(json.dumps(obj=results, indent=4))


@cli.command()
@click.argument("phone", type=str)
@click.pass_context
def phone(ctx: click.Context, phone: str):
    """
    Search for a digital footprint using a PHONE number.

    e.g., predictasearch phone +1234567890 --filter facebook,tiktok
    """
    parsed_networks: Optional[List[str]] = parse_network_filters(value=ctx.obj["filter"])
    results: List = client.search_by_phone(phone=phone, networks=parsed_networks)
    click.echo(json.dumps(obj=results, indent=4))


@cli.command()
@click.pass_context
def networks():
    """
    Retrieve a list of supported networks.

    e.g., predictasearch networks
    """
    results: Dict = client.get_supported_networks()
    click.echo(json.dumps(obj=results, indent=4))
