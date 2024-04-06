import argparse
import sys
import pathlib
import importlib
import os


def get_plugins():
    if getattr(sys, "frozen", False):
        app_path = pathlib.Path(sys.executable).parent / "plugins"
    elif __file__:
        app_path = pathlib.Path(__file__).parent / "plugins"
    sys.path.append(str(app_path))
    plugins = {}
    for i in os.listdir(app_path):
        datatype_path = app_path / i
        datatype_name = datatype_path.stem
        if datatype_name.startswith("__"):
            continue
        plugins[datatype_name] = {}
        for j in os.listdir(datatype_path):
            plugin_file = datatype_path / j
            plugin_name = plugin_file.stem
            if plugin_name.startswith("__"):
                continue
            plugins[datatype_name][plugin_name] = importlib.import_module(
                f"{datatype_name}.{plugin_name}")
    plugins_input = {}
    plugins_output = {}
    for i in plugins:
        datatype = plugins[i]
        plugins_input[i] = {}
        plugins_output[i] = {}
        for j in datatype:
            plugin = datatype[j]
            if plugin.input is not None:
                plugins_input[i][j] = plugin
            if plugin.output is not None:
                plugins_output[i][j] = plugin
    return plugins_input, plugins_output


def get_args(plugins_input, plugins_output):
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--input", type=str, help="input file")
    args.add_argument("-dt", "--datatype", type=str,
                      help="datatype", choices=plugins_input.keys())
    args.add_argument("-if", "--input-format", type=str,
                      help="input format")
    args.add_argument("-of", "--output-format", type=str,
                      help="output format")
    args.add_argument("-o", "--output", type=str, help="output file")
    args.add_argument("-l", "--list", action="store_true", help="list plugins")
    args = args.parse_args()

    if args.list:
        print("┌───────────────┬───────────────┐")
        print("│Input formats: │Output formats:│")
        for i in plugins_input:
            print("├───────────────┴───────────────┤")
            print(f"│{i:^31}│")
            print("├───────────────┬───────────────┤")
            input_elements = list(plugins_input[i].keys())
            output_elements = list(plugins_output[i].keys())
            for j in range(min(len(input_elements), len(output_elements))):
                print(f"│{input_elements[j]:^15}│{output_elements[j]:^15}│")
            if len(input_elements) > len(output_elements):
                for j in range(len(output_elements), len(input_elements)):
                    print(f"│{input_elements[j]:^15}│               │")
            elif len(output_elements) > len(input_elements):
                for j in range(len(input_elements), len(output_elements)):
                    print(f"│               │{output_elements[j]:^15}│")
        print("└───────────────┴───────────────┘")
        sys.exit(0)

    datatype = args.datatype

    if args.input is None:
        print("Input file not found")
        sys.exit(1)
    input_path = pathlib.Path(args.input).absolute()
    if not input_path.exists():
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    if args.input_format is None and input_path.suffix[1:] in plugins_input[datatype]:
        input_format = input_path.suffix[1:]
    elif args.input_format is None:
        print(f"Input format not found: {args.input_format}")
        sys.exit(1)
    elif args.input_format in plugins_input[datatype]:
        input_format = args.input_format
    else:
        print(f"Input format not found: {args.input_format}")
        sys.exit(1)

    if args.output is None and args.output_format is not None:
        output_path = input_path.with_suffix(
            f".{args.output_format}").absolute()
    elif args.output is None:
        sys.exit(1)
    else:
        output_path = pathlib.Path(args.output).absolute()

    if args.output_format is None and output_path.suffix[1:] in plugins_output[datatype]:
        output_format = output_path.suffix[1:]
    elif args.output_format is None:
        print(f"Output format not found: {args.output_format}")
        sys.exit(1)
    elif args.output_format in plugins_output[datatype]:
        output_format = args.output_format
    else:
        print(f"Output format not found: {args.output_format}")
        sys.exit(1)
    return datatype, input_path, input_format, output_path, output_format


def read(plugins_input, input_path, datatype, input_format):
    plugin = plugins_input[datatype][input_format]
    try:
        data = plugin.input(input_path)
    except ValueError as e:
        print(e)
        sys.exit(2)

    return data


def write(plugins_output, output_path, datatype, output_format, data):
    plugin = plugins_output[datatype][output_format]
    plugin.output(output_path, data)


def main():
    plugins_input, plugins_output = get_plugins()
    datatype, input_path, input_format, output_path, output_format = get_args(
        plugins_input, plugins_output)
    data = read(plugins_input, input_path, datatype, input_format)
    write(plugins_output, output_path, datatype, output_format, data)


if __name__ == "__main__":
    main()
    sys.exit(0)
