import os, sys
import argparse
from src.extractor import main
from rosdiscover_wrapper import *
import pandas as pd
from graph_merger import *
from graphviz import Source

def check_files_extension(folder_path, extension):
    for filename in os.listdir(folder_path):
        if filename.endswith(extension):
            return True
    return False


def run_extractor(ros_version, start_time, end_time, file_path, filetype, input, time_space, rosdiscover):
    print(">>>> Bag File Extractor <<<<")

    if start_time is None:
        start_time = 'start'
    if end_time is None:
        end_time = 'end'

    if ros_version == 'ros1':
        if filetype == 'bag':
            graph_path = main.extractor(start_time, end_time, file_path, filetype, input, time_space, rosdiscover = rosdiscover)
        else:
            print("ROS1 only has filetype `bag`")
            sys.exit()
    elif ros_version == 'ros2':
        if filetype == 'db3':
            if check_files_extension(file_path, '.db3'):
                graph_path = main.extractor(start_time, end_time, file_path, filetype, input, time_space, rosdiscover = rosdiscover)
            else:
                print("Cannot find the correct file with the input filetype: " + filetype)
        elif filetype == 'mcap':
            if check_files_extension(file_path, '.mcap'):
                graph_path = main.extractor(start_time, end_time, file_path, filetype, input, time_space, rosdiscover = rosdiscover)
            else:
                print("Cannot find the correct file with the input filetype: " + filetype)
        else:
            print("Input the correct filetype. Valid filetypes in ROS2 are 'db3' and 'mcap'.")
    else:
        print("ROS version is unknown")

    print(">>>>>>>>>>>>>><<<<<<<<<<<<<<<")
    return graph_path


def convert_dot_to_pdf(dot_file_path, pdf_output_path):
    """
    Reads a DOT file, displays the graph, and saves it as a PDF.
    
    Parameters:
    - dot_file_path: str, the path to the DOT file.
    - pdf_output_path: str, the path where the PDF file will be saved.
    """
    print(pdf_output_path)
    # Read the DOT file
    with open(dot_file_path, 'r') as file:
        dot_content = file.read()

    # Create a Source object from the DOT content
    dot_graph = Source(dot_content)

    # Optionally, view the graph (this will open a viewer window if supported)
    dot_graph.view()

    # Save the graph to a PDF file (cleanup=True removes intermediate files)
    dot_graph.render(pdf_output_path, format='pdf', cleanup=True)

def run():
    # Arguments definition and management
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--ros_version', help='ROS Version: ros1 or ros2', required=True, type=str)
    parser.add_argument('-s', '--start_time', help='User-defined start time (in seconds)', required=False, type=str)
    parser.add_argument('-e', '--end_time', help='User-defined end time (in seconds)', required=False, type=str)
    parser.add_argument('-f', '--file_path', help='Path to FOLDER containing the ros bagfile.', required=True, type=str)
    parser.add_argument('-ft', '--file_type', help='Bag file type: bag, db3 or mcap', required=True, type=str)
    parser.add_argument('-i', '--input', help='Path to file containing nodes information', required=False, type=str)
    parser.add_argument('-ts', '--time_space', help='Time in second to generate a series of interconnected graphs', required=False, type=str)
    parser.add_argument('-rd', '--use-ros-discover', help='Option to run rosdiscover', required=False, type=bool)
    parser.add_argument('-rdc', '--ros-discover-config', help='Path to the rosdiscover config', required=False, type=str)
    parser.add_argument('-rds', '--node-input-strategy', help='either node-provider or graph-merge', required=False, type=str)
    options = parser.parse_args()

    if options.use_ros_discover is not None:
        if options.ros_discover_config is not None:
            if options.node_input_strategy is not None:
                csv_output_file = f"{options.file_path}/rosdiscover_output.csv"
                print("Running ROS Discover",options.ros_discover_config, "with the", options.node_input_strategy, "strategy")
                run_rosdiscover(options.ros_discover_config, csv_output_file)
             

                if str(options.node_input_strategy) == "graph-merge":
                    base_graph_path = run_extractor(options.ros_version,
                        options.start_time,
                        options.end_time,
                        options.file_path,
                        options.file_type,
                        options.input,
                        options.time_space, 
                        rosdiscover = True)

                    rosdiscover_graph_path = create_graph(path=csv_output_file, format= "dot")
                    convert_dot_to_pdf(rosdiscover_graph_path, f"{rosdiscover_graph_path}.pdf")
                    rosdiscover_graph_path = rosdiscover_graph_path + ".dot"

                    print("Base graph path: ", base_graph_path)
                    graph_folder_path = os.path.dirname(os.path.realpath(base_graph_path))
                    print("Rosdiscover graph path: ", rosdiscover_graph_path)

                    base_graph = parse_dotfile(base_graph_path)
                    rosdiscover_graph = parse_dotfile(rosdiscover_graph_path)
                    merged_graph = merge_and_highlight(base_graph, rosdiscover_graph)
                    export_to_dot(merged_graph, graph_folder_path + "/merged_graph.dot")
                    convert_dot_to_pdf(graph_folder_path + "/merged_graph.dot", graph_folder_path + "/merged_graph.pdf")

                    
                elif str(options.node_input_strategy) == "node-provider":
                    graph_path = run_extractor(options.ros_version,
                        options.start_time,
                        options.end_time,
                        options.file_path,
                        options.file_type,
                        csv_output_file,
                        options.time_space, 
                        rosdiscover = True)
                    print(graph_path)
                    
                else:
                    print("Node strategy is not node-provider or graph-merge")
            else:
                print("Please provide a strategy for the node input, can be either node-provider or graph-merge")
    else:
        run_extractor(options.ros_version,
                        options.start_time,
                        options.end_time,
                        options.file_path,
                        options.file_type,
                        options.input,
                        options.time_space, 
                        rosdiscover = False)
    



if __name__ == "__main__":
    run()