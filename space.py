import networkx as nx

class NetworkSpace(object):
    '''
    Base class for network space. Currently based on networkx...

    Methods:
        get_nodes:      Returns list of all nodes.
        get_neighbors:  Returns neighbors of given node.
    '''
    def __init__( self, nodes, edges):
        self.graph = nx.Graph()
        self.graph.add_nodes_from(nodes)
        self.graph.add_edges_from(edges)

    def get_nodes(self):
        return self.graph.nodes()

    def get_neighbors(self, node):
        return self.graph[node]

