import subprocess, re, os, csv, yaml, sys
import pandas as pd
from graphviz import Digraph
from ruamel.yaml import YAML
import re

def run_script_and_capture_output(script_path, * args):
    timestamp_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    warning_pattern = r"^Warning: "

    # List to hold the output lines
    output_lines = ""

    # Construct the command with the script path and its arguments
    command = [script_path] + list(args)

    # Run the script and capture the output
    with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as proc:
        for line in proc.stdout:
            # Check if the line starts with a timestamp
            if not re.match(timestamp_pattern, line):
                if not re.match(warning_pattern, line):
                    output_lines += line
                    print(line, end='')
    # Join the lines back into a single string


    # Use ruamel.yaml to load the YAML preserving the formatting
    yaml = YAML()
    yaml.preserve_quotes = True
    data = yaml.load(output_lines)

    return data

def format_topics_as_array(topics):
    """Formats the list of topics as a string array, with each topic in single quotes."""
    quoted_topics = [f"'{topic}'" for topic in topics]  # Surround each topic with single quotes
    return f"\"[{','.join(quoted_topics)}]\"" if topics else "[]"

def create_graph(path, format="dot"):
    print(path)
    df = pd.read_csv(path)
    out_file = os.path.dirname(path) + "/rosdiscover_graph"
    print(path, out_file)
    # Initialize a Digraph object
    dot = Digraph(comment='ROS Nodes and Topics')

    # Add nodes and edges
    for index, row in df.iterrows():
        node_name = row['Name']
        publishes = eval(row['Publish']) if row['Publish'] not in [None, '[]', ''] else []
        subscribes = eval(row['Subscribe']) if row['Subscribe'] not in [None, '[]', ''] else []

        # Add the node for the ROS node
        dot.node(node_name, node_name, shape='ellipse')

        # Add nodes and edges for publish topics
        for topic in publishes:
            dot.node(topic, topic, shape='box')
            dot.edge(node_name, topic, label='')

        # Add nodes and edges for subscribe topics
        for topic in subscribes:
            dot.node(topic, topic, shape='box')
            dot.edge(topic, node_name, label='')

    # Render the graph to a file (e.g., output.pdf)
    dot.render(out_file, view=False, format=format)
    return out_file

def remove_whitespace_from_csv(file_path):
    # Open the file, read its contents as a string
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Remove all spaces from the content
    modified_content = content.replace(" ", "")
    
    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(modified_content)

def run_rosdiscover(config_path, out_file):
    nodes = run_script_and_capture_output("rosdiscover", 'launch', config_path)

    # Prepare data for CSV
    csv_data = []


    for node in nodes:
        name = "/" + node.get('name', '')
        publishes = format_topics_as_array([pub['name'] for pub in node.get('pubs', [])])
        subscribes = format_topics_as_array([sub['name'] for sub in node.get('subs', [])])
        node_start = '' 
        node_end = '' 
        print(name, publishes, subscribes, node_start, node_end)
        csv_data.append([name, publishes, subscribes, node_start, node_end])


    with open(out_file, 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar=' ')
        writer.writerow(['Name', 'Publish', 'Subscribe', 'Node-start', 'Node-end'])
        writer.writerows(csv_data)

    remove_whitespace_from_csv(out_file)
    return out_file

