from mesa import Agent, Model
from space import MultilayerNetworkSpace
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
import networkx as nx
import numpy as np
from random import sample, randrange

class Travel_Agent(Agent):
    def __init__(self, start_pos, dest, start_time, unique_id):
        self.pos = start_pos
        self.dest = dest
        self.unique_id = unique_id
        self.travel_time = start_time


    def _probability_distribution(self, distances):
        dists = np.array(distances, dtype=np.float)
        
        # zero improvements have together half prob. as the smallest improvement
        zeros = dists==0
        zerodist = dists[dists.nonzero()].min()/ (2* sum(zeros) ) 
        dists[dists == 0] = zerodist
 
        dists = dists/dists.sum() # normalize

        return dists

    def step(self, model):
        if self.pos == self.dest:
            return # TODO: respawn or remove from scheduler?
        dests = []
        dists = []
        season = model.get_season(self.travel_time) # what year is it?
        if model.network.path_exists(self.pos, self.dest, season):
            dist = model.network.shortest_path_to(self.pos, self.dest, season)
            for neighbor in model.network.get_neighbors(self.pos, season):
                n_dist = dist - model.network.shortest_path_to(neighbor, self.dest, season)
                if n_dist < 0:
                    continue # no backtracking
                dests.append(neighbor)
                dists.append(n_dist)
            dests_dists = dict(zip(dests,dists))
            dists = self._probability_distribution(dists)

            next_dest = np.random.choice(dests, p=dists)

            # update traveled time
            #TODO select edge!
            self.travel_time += dests_dists[next_dest]
            
            # off you go
            self.pos = next_dest
        else:
            # sit and wait for summer
            self.travel_time += model.season_length

    def __str__(self):
        templ = "Travel_Agent: {pos: %d, dest: %d, unique_id: %d, travel_time: %d}" 
        text = templ %(self.pos,self.dest, self.unique_id, self.travel_time)
        return text

class Travel_Model(Model):
    def __init__(self, networks=None, season_length=91, n_agents=100, max_steps=1000):
        self.n_steps = 0
        self.max_steps = max_steps
        self.season_length = season_length
        self.schedule = BaseScheduler(self)
        if networks is None:
            networks = self._demo_networks()
        self.n_seasons = len(networks)
        
        # space
        nodes = networks[0].nodes()
        edges = []
        for network in networks:
            edges.append(network.edges(data=True))

        self.network = MultilayerNetworkSpace(nodes,edges)

        # agents
        for n in range(n_agents):
            start, dest = sample(nodes,2)
            start_time = randrange(self.n_seasons * self.season_length )
            agent = Travel_Agent(start,dest,start_time,n)

            self.schedule.add(agent)
        
        # data collection
        self.dc = DataCollector(
                {
                    "enroute": lambda m: self.count_en_route(m)
                    },
                {
                    "position": lambda a: a.pos,
                    "travel_time": lambda a: a.travel_time
                    }
                )
        self.dc.collect(self)

        self.running = True

    def step(self):
        self.schedule.step()
        self.dc.collect(self)
        self.n_steps +=1

        if self.count_en_route(self) == 0 or self.n_steps >= self.max_steps:
            self.running = False

    def get_season(self, time):
        return (time // self.season_length) % self.n_seasons 


    def _demo_networks(self):
        networks = []
        for i in range(3):
            g = nx.random_graphs.watts_strogatz_graph(100, 2, 0.05)
            dists = np.random.randint(1,30, g.number_of_edges())
            dists = dict(zip(g.edges(),dists))
            nx.set_edge_attributes(g, 'distance', dists)
            networks.append(g)
        return networks

    @staticmethod
    def count_en_route(model):
        count = len(model.schedule.agents)
        for agent in model.schedule.agents:
            if agent.pos == agent.dest:
                count -=1
        return count
