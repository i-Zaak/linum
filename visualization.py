import numpy as np
import networkx as nx
import matplotlib.pylab as plt

def plot_spreading(model, state, pos, cmap, colors):

    fig=plt.figure()
    ax=plt.axes()
    nodes = nx.draw_networkx_nodes(model.network.graph,pos=pos,ax=ax,node_color=colors,cmap=plt.cm.get_cmap("Dark2"))
    nx.draw_networkx_edges(model.network.graph,pos=pos,ax=ax,node_color=colors,cmap=plt.cm.get_cmap("Dark2"))

    n_steps = model.dc.get_agent_vars_dataframe().index.levels[0].shape[0]
    def init():
        states = model.dc.get_agent_vars_dataframe()['state'][0]
        colors = list(map(lambda x: cmap[state(states[x.unique_id])], model.network.graph.nodes()))  
        nodes.set_facecolor(colors)
        return nodes,

    def animate(i):    
        states = model.dc.get_agent_vars_dataframe()['state'][i]
        colors = list(map(lambda x: cmap[state(states[x.unique_id])], model.network.graph.nodes()))  
        nodes.set_facecolor(colors)
        return nodes,

    return fig, animate, init, n_steps

def node_colors(cmap, model):
    colors = list(map(lambda x: cmap[x.state], model.network.graph.nodes()))
    return colors


def plot_path(model,agent_id):
    df = model.dc.get_agent_vars_dataframe()
    dest = model.schedule.agents[agent_id].dest
    path = df.query('AgentID == %d'%(agent_id), engine='python')
    path = path['position'].as_matrix()
    path = path[0:np.argmax(path == dest)+1]
    path_edges = [(path[n], path[n+1]) for n in range(len(path)-1)]
    g = compose_graphs(model.network.graphs)
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g,pos=pos, node_color='k', node_size=30)
    nx.draw_networkx_nodes(g,pos=pos, nodelist=path.tolist(), color='r', node_size=30)
    nx.draw_networkx_nodes(g,pos=pos, nodelist=[path[0],path[-1]], color='r', node_size=100)
    nx.draw_networkx_edges(g,pos=pos)
    nx.draw_networkx_edges(g,pos=pos, edgelist=path_edges, edge_color='r')

    
def compose_graphs(graphs):
    g = graphs[0]
    for h in graphs[1:]:
        g = nx.compose(g,h)

    return g
