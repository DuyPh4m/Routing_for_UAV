import random
import math
import networkx as nx
import matplotlib.pyplot as plt

from Calculation import distance
from ACO import AntColonyOptimization
from LEACH import LeachProtocol
from Node import Node
from Data import Data

class Simulation(object):
    
    def __init__(self, num, rounds):
        self.num = num
        self.rounds = rounds
        self.data = Data()
   
    def Run(self):

        self.GenerateNodes()

        for r in range(self.num):

            self.leach = LeachProtocol(p=0.2, min_per=0.1, max_per=0.2, data=self.data, round=r)
            # self.ant_colony = AntColonyOptimization(distances=self.distances, n_ants=1, n_best=1, n_iterations=100, decay=0.95, alpha=1, beta=1) 
            self.leach.Run()            
            # self.ant_colony.Run()

            self.Draw()

    def GenerateNodes(self):

        x = random.uniform(0, 100)
        y = random.uniform(0, 100)

        node = Node(0, x, y)

        self.data.nodes.append(node)
        self.data.norm_nodes.append(node)

        for i in range(self.num - 1):

            while True:

                dist = random.uniform(15, 30)
                angle = random.uniform(0, 2 * math.pi)

                dx = dist * math.cos(angle)
                dy = dist * math.sin(angle)

                k = random.randint(0, len(self.data.nodes) - 1)

                x = self.data.nodes[k].x + dx
                y = self.data.nodes[k].y + dy

                if x > 100 or y > 100:
                    continue

                valid = True

                for node in self.data.norm_nodes:

                    dx = node.x - x 
                    dy = node.y - y
                    dist_between = math.sqrt(dx**2 + dy**2)

                    if dist_between < 15 or dist_between > 30:
                        valid = False
                        break
                
                if valid:
                    node = Node(i + 1, x, y)
                    self.data.nodes.append(node)
                    self.data.norm_nodes.append(node)
                    break

    def Draw(self):

        G = nx.Graph()

        for node in self.data.nodes:
            G.add_node(node.id, x=node.x, y=node.y, isCH=node.isCH, cluster_ID=node.cluster_ID, sens_range=node.sens_range, comm_range=node.comm_range)

        node_colors = ["lightgreen" if G.nodes[node].get("isCH") else "lightblue" for node in G.nodes]

        pos = {node: (G.nodes[node].get("x"), G.nodes[node].get("y")) for node in G.nodes}

        fig, ax = plt.subplots(figsize=(10, 10))

        nx.draw_networkx_nodes(G, pos, node_size=200, node_color=node_colors, edgecolors="black", ax=ax)

        labels = {node: node for node in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_color="black")

        plt.xlim(-50, 150)
        plt.ylim(-50, 150)
        plt.axis("off")
        plt.show()