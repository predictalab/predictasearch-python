from rich import print as rprint
from typing import Union, List
from typing import Dict, Any, Optional, Set
from rich.tree import Tree



def parse_network_filters(value: Optional[str]) -> Optional[List[str]]:
    """
    Parse a comma-separated string into a list of network names.

    :param value: A string of comma-separated network names (e.g., "facebook,linkedin")
    :type value: Optional[str
    :return: A list of cleaned network names or None if no input provided
    :rtype: Optional[List[str]]
    """
    if value is None:
        return None
    return [network.strip() for network in value.split(",") if network.strip()]



def print_tree(
    root_label: str,
    data: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]
):
    """
    Print a grouped tree of records under a root label using Rich.

    This function prints all records under a single root node, such as an email
    address or phone number. Each subnode is labeled by its platform or key name.

    :param root_label: The label for the root of the tree (e.g., email or phone number).
    :type root_label: str

    :param data: The data to display. Can be a list of records (list of dicts) or
                 a mapping of keys to records (dict of dicts).
    :type data: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]
    """
    if not data:
        print("No results found.")

    # Create the root of the tree
    root = Tree(label=root_label, guide_style="bright_blue", highlight=True)

    # Handle dictionary-style data (e.g., networks)
    if isinstance(data, dict):
        for name, record in data.items():
            # Use the key as the subtree label
            node = root.add(name)
            _build_tree(record=record, parent=node, exclude_keys={"platform"})

    # Handle list-style data (e.g., search results)
    elif isinstance(data, list):
        for record in data:
            # Use 'platform' or 'source' as the subtree label
            platform = record.get("platform") or record.get("source") or "NaN"
            node = root.add(platform.capitalize())
            _build_tree(record=record, parent=node, exclude_keys={"platform"})

    rprint(root)



def _build_tree(
    record: Dict[str, Any],
    parent: Tree,
    exclude_keys: Optional[Set[str]] = None
):
    """
    Recursively adds a dictionary's contents to a Rich Tree node, expanding all dicts/lists properly.

    :param record: Dictionary representing a data record.
    :param parent: Tree node to attach children to.
    :param exclude_keys: Keys to exclude from rendering (e.g., 'platform').
    """
    exclude_keys = exclude_keys or set()
    description = record.get("description") # Will render this at the end

    # Iterate over all key-value pairs in the record
    for key, value in record.items():
        # Skip keys explicitly excluded and defer 'description'
        if key in exclude_keys or key == "description":
            continue

        # If the value is a nested dictionary, create a branch and recurse
        if isinstance(value, dict):
            branch = parent.add(key)
            _build_tree(value, branch)

        # If the value is a list, create a branch and add each item
        elif isinstance(value, list):
            branch = parent.add(key)
            # Recurse into dict items
            for item in value:
                if isinstance(item, dict):
                    _build_tree(item, branch)
                else:
                    # Add simple items directly
                    branch.add(str(item))

        # For all other value types, just print the key-value pair
        else:
            parent.add(f"{key}: {value}")

    if description:
        parent.add(description) # Finally render the description
