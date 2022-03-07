from N2G import yed_diagram

diagram = yed_diagram()
sample_list_graph = [
    {'source': {'id': 'SW1', 'top_label': 'CORE', 'bottom_label': '1,1,1,1'}, 'src_label': 'Gig0/0', 'target': 'R1', 'trgt_label': 'Gig0/1'},
    {'source': {'id': 'R2', 'top_label': 'DC-PE'}, 'src_label': 'Gig0/0', 'target': 'SW1', 'trgt_label': 'Gig0/2'},
    {'source': {'id':'R3', 'bottom_label': '1.1.1.3'}, 'src_label': 'Gig0/0', 'target': 'SW1', 'trgt_label': 'Gig0/3'},
    {'source': 'SW1', 'src_label': 'Gig0/4', 'target': 'R4', 'trgt_label': 'Gig0/1'},
    {'source': 'SW1', 'src_label': 'Gig0/5', 'target': 'R5', 'trgt_label': 'Gig0/7'},
    {'source': 'SW1', 'src_label': 'Gig0/6', 'target': 'R6', 'trgt_label': 'Gig0/11'}
]
diagram.from_list(sample_list_graph)
diagram.dump_file(filename="Sample_graph.graphml", folder="./")
