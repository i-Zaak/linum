from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

from space import NetworkSpace

from enum import Enum
from random import random, sample
import networkx as nx

class State(Enum):
    susceptible = 1
    infected = 2
    resistant = 3

class SIR_Agent(Agent):
    def __init__(self, unique_id):
        self.state = State.susceptible
        self.next_state = None
        self.unique_id = unique_id

    def step(self, model):
        if self.state == State.susceptible:
            self.next_state = State.susceptible
            for neighbor in model.network.get_neighbors(self):
                if model.si_trans >= random():
                    self.next_state = State.infected
                    break
        elif self.state == State.infected:
            if model.ir_trans >= random():
                self.next_state = State.resistant
            else:
                self.next_state = State.infected
        else:
            pass # resistant nodes just don't care

    def advance(self,model):
        self.state = self.next_state
 
class SIR_Network_Model(Model):
    def __init__(self, g=None, outbreak_size=3, si_trans=0.025, ir_trans=0.05):
        self.schedule = SimultaneousActivation(self)
        
        if g is None:
            g = nx.random_graphs.watts_strogatz_graph(100, 4, 0.05) 

        self.si_trans = si_trans
        self.ir_trans = ir_trans

        nodes = g.nodes()
        agent_nodes = list(map(lambda x: SIR_Agent(x), nodes))
        n_map = dict(zip(nodes, agent_nodes))
        agent_edges = list(map(lambda e: (n_map[e[0]], n_map[e[1]])  , g.edges()))

        for agent in agent_nodes:
            self.schedule.add(agent)
        # set the initial outbreak
        for node in sample(list(agent_nodes), outbreak_size):
            node.state = State.infected

        self.network = NetworkSpace(agent_nodes, agent_edges)
        self.dc = DataCollector({"susceptible": lambda m: self.count_state(m, State.susceptible),
                                "infected": lambda m: self.count_state(m, State.infected),
                                "resistant": lambda m: self.count_state(m, State.resistant)},
                                {"state": lambda a: a.state.value}
                                )
        self.dc.collect(self) #initial state

        self.running = True

    def step(self):
        self.schedule.step()
        self.dc.collect(self)

        # disease dead?
        if self.count_state(self, State.infected) == 0:
            self.running = False

    @staticmethod
    def count_state(model,state):
        count = 0
        for agent in model.schedule.agents:
            if agent.state == state:
                count +=1
        return count


if __name__ == "__main__":
    sir_model = SIR_Network_Model()
    sir_model.run_model()
    results = sir_model.dc.get_agent_vars_dataframe()
    print(results)
    results.plot()


