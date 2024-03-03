import pydot

def parse_dotfile(file_path):
    graphs = pydot.graph_from_dot_file(file_path)
    if graphs:
        return graphs[0]
    else:
        return None

def merge_and_highlight(graph1, graph2):
    # Initialize the merged graph
    merged_graph = pydot.Dot(graph_type='digraph')
    
    # Add all nodes and edges from the first graph
    for node in graph1.get_nodes():
        merged_graph.add_node(node)
    for edge in graph1.get_edges():
        merged_graph.add_edge(edge)
    
    # Keep track of existing nodes and edges for comparison
    existing_nodes = set(node.get_name() for node in merged_graph.get_nodes())
    existing_edges = set((edge.get_source(), edge.get_destination()) for edge in merged_graph.get_edges())
    
    # Add nodes from the second graph
    for node in graph2.get_nodes():
        if node.get_name() not in existing_nodes:
            node.set_color('red')  # Highlight new nodes in red
        merged_graph.add_node(node)
    
    # Add edges from the second graph, highlight new edges or edges between existing nodes
    for edge in graph2.get_edges():
        edge_tuple = (edge.get_source(), edge.get_destination())
        if edge_tuple not in existing_edges:
            edge.set_color('red')  # Highlight new edges in red
            merged_graph.add_edge(edge)
        elif edge.get_color() != 'red':  # For existing edges not highlighted, ensure they're not colored red
            edge.set_color('')  # Reset color to default if re-adding an existing edge that's not new

    return merged_graph

def export_to_dot(merged_graph, output_file):
    merged_graph.write_dot(output_file)
    print(f"Exported merged graph to {output_file}")