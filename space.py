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


class MultilayerNetworkSpace(object):
    '''
    Base class for multilayer network space. Currently based on networkx... 
    No links between layers, same set of node in every layer.

    Methods:
        get_nodes:      Returns list of all nodes.
        get_neighbors:  Returns neighbors of given node in given layer.
    '''

    def __init__( self, nodes, edges, weight='distance'):
        self.n_layers = len(edges)
        self.graphs = []
        self.routes = []
        for n in range(self.n_layers):
            g = nx.Graph()
            g.add_nodes_from(nodes)
            g.add_edges_from(edges[n])
            self.graphs.append(g)
            #import pdb; pdb.set_trace()
            self.routes.append(nx.all_pairs_dijkstra_path_length(g, weight=weight))

    def get_nodes(self):
        return self.graph.nodes()

    def get_neighbors(self, node, layer):
        return self.graphs[layer][node]

    def shortest_path_to(self, src_node, dest_node, layer):
        return self.routes[layer][src_node][dest_node]

    def path_exists(self, src_node, dest_node, layer):
        return dest_node in self.routes[layer][src_node]

    def get_flattened_network(self):
        pass

