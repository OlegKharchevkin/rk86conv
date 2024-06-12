import argparse
import sys
import pathlib
import importlib
from types import ModuleType
from typing import Optional
import os


def get_plugins() -> tuple[dict[str, dict[str, ModuleType]], dict[str, dict[str, ModuleType]]]:
    """
    Get plugins from the 'plugins' directory in the current directory.

    Returns:
        Tuple of two dictionaries: plugins_input and plugins_output.
        Each dictionary has the following structure:
        {
            datatype_name: {
                plugin_name: plugin_module
            }
        }
    """
    # Get the path to the 'plugins' directory
    if getattr(sys, "frozen", False):
        app_path = pathlib.Path(sys.executable).parent / "plugins"
    elif __file__:
        app_path = pathlib.Path(__file__).parent / "plugins"

    # Add the 'plugins' directory to the system path
    sys.path.append(str(app_path))

    # Create dictionaries to store plugins
    plugins = {}
    plugins_input = {}
    plugins_output = {}

    # Loop through all files and directories in the 'plugins' directory
    for i in os.listdir(app_path):
        datatype_path = app_path / i
        datatype_name = datatype_path.stem

        # Skip directories starting with '__'
        if datatype_name.startswith("__"):
            continue

        # Create a dictionary for the current datatype
        plugins[datatype_name] = {}
        plugins_input[datatype_name] = {}
        plugins_output[datatype_name] = {}

        # Loop through all files and directories in the current datatype directory
        for j in os.listdir(datatype_path):
            plugin_file = datatype_path / j
            plugin_name = plugin_file.stem

            # Skip files starting with '__'
            if plugin_name.startswith("__"):
                continue

            # Import the module and add it to the plugins dictionary
            plugins[datatype_name][plugin_name] = importlib.import_module(
                f"{datatype_name}.{plugin_name}")
            # Check if the plugin has an input and output function
            plugin = plugins[datatype_name][plugin_name]
            if plugin.input is not None:
                plugins_input[datatype_name][plugin_name] = plugin
            if plugin.output is not None:
                plugins_output[datatype_name][plugin_name] = plugin

    # Return the dictionaries with plugins
    return plugins_input, plugins_output


def get_args(plugins_input: dict[str, dict[str, ModuleType]], plugins_output: dict[str, dict[str, ModuleType]]) -> tuple[str, str, str, str, str]:
    """
    This function parses command line arguments and returns the datatype, input path, input format, output path, and output format.

    Args:
        plugins_input (dict): A dictionary containing information about the input plugins.
        plugins_output (dict): A dictionary containing information about the output plugins.

    Returns:
        tuple: A tuple containing the datatype, input path, input format, output path, and output format.
    """
    # Create the argument parser
    args = argparse.ArgumentParser()

    # Add arguments to the parser
    args.add_argument("-i", "--input", type=str, help="input file")
    args.add_argument("-dt", "--datatype", type=str,
                      help="datatype", choices=plugins_input.keys())
    args.add_argument("-if", "--input-format", type=str,
                      help="input format")
    args.add_argument("-of", "--output-format", type=str,
                      help="output format")
    args.add_argument("-o", "--output", type=str, help="output file")
    args.add_argument("-l", "--list", action="store_true", help="list plugins")

    # Parse the arguments
    args = args.parse_args()

    # If the --list flag is set, print the list of plugins and exit
    if args.list:
        print_plugins(plugins_input, plugins_output)
        sys.exit(0)

    # Get the datatype from the command line arguments
    datatype = args.datatype

    # If the input file is not specified, print an error message and exit
    if args.input is None:
        print("Input file not found")
        sys.exit(1)

    # Get the absolute path of the input file
    input_path = pathlib.Path(args.input).absolute()

    # If the input file does not exist, print an error message and exit
    if not input_path.exists():
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    # Get the input format from the command line arguments or the file extension
    input_format = get_format(
        args.input_format, input_path, plugins_input[datatype])

    # Get the output path and format from the command line arguments or the input path and format
    output_path, output_format = get_output_info(
        args.output, args.output_format, input_path, plugins_output[datatype])

    # Return the datatype, input path, input format, output path, and output format
    return datatype, input_path, input_format, output_path, output_format


def print_plugins(plugins_input: dict[str, dict[str, ModuleType]], plugins_output: dict[str, dict[str, ModuleType]]) -> None:
    """
    This function prints a table of input and output plugins for each datatype.

    Args:
        plugins_input (dict): A dictionary containing information about the input plugins.
        plugins_output (dict): A dictionary containing information about the output plugins.
    """
    # Print the table headers
    print("┌───────────────┬───────────────┐")
    print("│Input formats: │Output formats:│")

    # Loop through each datatype
    for datatype in plugins_input:
        # Print the datatype name
        print(f"├───────────────┴───────────────┤")
        print(f"│{datatype:^31}│")
        print("├───────────────┬───────────────┤")

        # Get the input and output plugins for the current datatype
        input_plugins = list(plugins_input[datatype].keys())
        output_plugins = list(plugins_output[datatype].keys())

        # Loop through the minimum number of input and output plugins
        for i in range(min(len(input_plugins), len(output_plugins))):
            # Print the input and output plugin names
            print(f"│{input_plugins[i]:^15}│{output_plugins[i]:^15}│")

        # If there are more input plugins than output plugins, print the remaining input plugins
        if len(input_plugins) > len(output_plugins):
            for i in range(len(output_plugins), len(input_plugins)):
                print(f"│{input_plugins[i]:^15}│               │")

        # If there are more output plugins than input plugins, print the remaining output plugins
        elif len(output_plugins) > len(input_plugins):
            for i in range(len(input_plugins), len(output_plugins)):
                print(f"│               │{output_plugins[i]:^15}│")

    # Print the table footer
    print("└───────────────┴───────────────┘")


def get_format(input_format: Optional[str], input_path: pathlib.Path, input_plugins: dict[str, ModuleType]) -> str:
    """
    This function returns the input format from the command line arguments or the file extension.

    Args:
        input_format (str): The input format from the command line arguments.
        input_path (pathlib.Path): The path to the input file.
        input_plugins (dict): A dictionary containing information about the input plugins.

    Returns:
        str: The input format.
    """
    # If the input format is specified, return it
    if input_format is not None:
        return input_format

    # If the input format is not specified, get the file extension
    suffix = input_path.suffix[1:]

    # If the file extension is in the input plugins, return it
    if suffix in input_plugins:
        return suffix

    # If the file extension is not in the input plugins, print an error message and exit
    print(f"Input format not found: {suffix}")
    sys.exit(1)


def get_output_info(output: Optional[str], output_format: Optional[str], input_path: pathlib.Path, output_plugins: dict[str, ModuleType]) -> tuple[pathlib.Path, str]:
    """
    This function returns the output path and format from the command line arguments or the input path and format.

    Args:
        output (str): The output path from the command line arguments.
        output_format (str): The output format from the command line arguments.
        input_path (pathlib.Path): The path to the input file.
        datatype (str): The datatype.
        output_plugins (dict): A dictionary containing information about the output plugins.

    Returns:
        tuple: A tuple containing the output path and format.
    """
    # If the output path is specified, return it
    if output is not None:
        output_path = pathlib.Path(output).absolute()
        return output_path, output_format

    # If the output path is not specified, use the input path to get the output path and format
    output_path = input_path.with_suffix(f".{output_format}")
    output_format = get_format(output_format, output_path, output_plugins)
    return output_path, output_format


def read(plugins_input: dict[str, dict[str, ModuleType]], input_path: pathlib.Path, datatype: str, input_format: str):
    """
    Reads data from the input file using the specified plugin and format.

    Args:
        plugins_input (dict): A dictionary containing information about the input plugins.
        input_path (pathlib.Path): The path to the input file.
        datatype (str): The datatype.
        input_format (str): The input format.

    Returns:
        Data: The data read from the input file.

    Raises:
        ValueError: If there is an error reading the input file.
    """
    # Get the plugin for the specified datatype and input format
    plugin = plugins_input[datatype][input_format]

    try:
        # Read the data from the input file using the plugin
        data = plugin.input(input_path)
    except ValueError as e:
        # If there is an error reading the input file, print the error message and exit
        print(e)
        sys.exit(2)

    return data


def write(plugins_output: dict[str, dict[str, ModuleType]], output_path: pathlib.Path, datatype: str, output_format: str, data) -> None:
    """
    Writes data to the output file using the specified plugin and format.

    Args:
        plugins_output (dict): A dictionary containing information about the output plugins.
        output_path (pathlib.Path): The path to the output file.
        datatype (str): The datatype.
        output_format (str): The output format.
        data (Data): The data to write to the output file.
    """
    # Get the plugin for the specified datatype and output format
    plugin = plugins_output[datatype][output_format]

    # Write the data to the output file using the plugin
    plugin.output(output_path, data)


def main() -> None:
    """
    Main function that reads data from an input file, converts it to a different format, and writes it to an output file.
    """
    # Get the input and output plugins
    plugins_input, plugins_output = get_plugins()

    # Get the datatype, input path, input format, output path, and output format from the command line arguments
    datatype, input_path, input_format, output_path, output_format = get_args(
        plugins_input, plugins_output)

    # Read data from the input file using the specified plugin and format
    data = read(plugins_input, input_path, datatype, input_format)

    # Write the data to the output file using the specified plugin and format
    write(plugins_output, output_path, datatype, output_format, data)


if __name__ == "__main__":
    main()
    sys.exit(0)
