import os
from typing import Optional, List, Dict

import rich_click as click

from ._api import PredictaSearch
from ._lib import console, parse_network_filters, print_tree

client = PredictaSearch(api_key=os.environ["PREDICTA_API_KEY"])


@click.group()
@click.option(
    "--filter",
    type=str,
    help="A comma-separated "
         "list of networks to filter the (email|phone) search (e.g., facebook,linkedin)."
)
@click.option(
    "--pretty",
    type=bool,
    help="Return results in raw JSON format."
)
@click.pass_context
def cli(ctx: click.Context, filter: Optional[str], pretty: Optional[bool]):
    """
    PredictaSearch

    Get the digital footprint from an email or phone number.
    """

    console.set_window_title("Predicta Search - Get the digital footprint from an email or phone number.")
    ctx.ensure_object(dict)
    ctx.obj["filter"] = filter
    ctx.obj["pretty"] = pretty


@cli.command()
@click.argument("email", type=str)
@click.pass_context
def email(ctx: click.Context, email: str):
    """
    Search for a digital footprint using an EMAIL address.

    e.g., predictasearch email johndoe@gmail.com --filter facebook,linkedin
    """
    parsed_networks: Optional[List[str]] = parse_network_filters(value=ctx.obj.get("filter"))
    results: List = client.search_by_email(email=email, networks=parsed_networks)
    if ctx.obj.get("pretty"):
        console.print(results)
    else:
        print_tree(root_label=email, data=results)


@cli.command()
@click.argument("phone", type=str)
@click.pass_context
def phone(ctx: click.Context, phone: str):
    """
    Search for a digital footprint using a PHONE number.

    e.g., predictasearch phone +1234567890 --filter facebook,tiktok
    """
    parsed_networks: Optional[List[str]] = parse_network_filters(value=ctx.obj.get("filter"))
    results: List = client.search_by_phone(phone=phone, networks=parsed_networks)
    if ctx.obj.get("pretty"):
        console.print(results)
    else:
        print_tree(root_label=phone, data=results)


@cli.command()
@click.pass_context
def networks(ctx: click.Context):
    """
    Retrieve a list of supported networks.

    e.g., predictasearch networks
    """
    results: Dict = client.get_supported_networks()
    if ctx.obj.get("pretty"):
        console.print(results)
    else:
        print_tree(root_label="Networks", data=results)

