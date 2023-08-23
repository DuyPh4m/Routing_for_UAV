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

        self.Generate_Nodes()

        for r in range(self.num):

            self.leach = LeachProtocol(p=0.2, min_per=0.1, max_per=0.2, data=self.data, round=r)
            # self.ant_colony = AntColonyOptimization(distances=self.distances, n_ants=1, n_best=1, n_iterations=100, decay=0.95, alpha=1, beta=1) 
            self.leach.Run()            
            # self.ant_colony.Run()

            self.Draw()
            self.Data_Reset()

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

    def Generate_Nodes(self):
            
        for i in range(5):
            start_X = i * 20

            for j in range(5):
                start_Y = j * 20

                while True:

                    x = random.uniform(start_X, start_X + 20)
                    y = random.uniform(start_Y, start_Y + 20)
                    valid = True

                    for node in self.data.norm_nodes:
                        dx = node.x - x
                        dy = node.y - y

                        dist_between = math.sqrt(dx**2 + dy**2)

                        if dist_between < 20:
                            valid = False
                            break

                    if valid:
                        node = Node(i * 5 + j , x, y)
                        self.data.nodes.append(node)
                        self.data.norm_nodes.append(node)
                        break

    def Add_CHs(self):

        H = nx.Graph()
        
        for CH_node in self.data.CH_nodes:
            H.add_node(CH_node.id, x=CH_node.x, y=CH_node.y, comm_range=CH_node.comm_range)
        
        for CH_node1 in self.data.CH_nodes:
            for CH_node2 in self.data.CH_nodes:
                if CH_node1 != CH_node2 and distance(CH_node1, CH_node2) < CH_node1.comm_range:
                    H.add_edge(CH_node1.id, CH_node2.id)

        # while (nx.is_connected(H) == False)
        #     print

    def Draw(self):

        G = nx.Graph()

        for node in self.data.nodes:
            G.add_node(node.id, x=node.x, y=node.y, isCH=node.isCH, cluster_ID=node.cluster_ID, sens_range=node.sens_range, comm_range=node.comm_range)

        for node in self.data.nodes:
            for CH_node in self.data.CH_nodes:

                if node.cluster_ID == CH_node.id and node.id != CH_node.id:
                    G.add_edge(node.id, CH_node.id, style='solid', edge_color='green')
            
        for CH_node1 in self.data.CH_nodes:

            for CH_node2 in self.data.CH_nodes:
                
                if CH_node1.id != CH_node2.id:
                    dist = distance(CH_node1, CH_node2)
                    if dist < CH_node2.comm_range:
                        G.add_edge(CH_node1.id, CH_node2.id, style='solid', edge_color='red')

        node_colors = ["lightgreen" if G.nodes[node].get("isCH") else "lightblue" for node in G.nodes]
        
        edge_styles = [G[u][v]['style'] for u, v in G.edges()]
        edge_colors = [G[u][v]['edge_color'] for u, v in G.edges()]

        pos = {node: (G.nodes[node].get("x"), G.nodes[node].get("y")) for node in G.nodes}

        fig, ax = plt.subplots(figsize=(8, 8))

        for node in G.nodes():
            if G.nodes[node]["isCH"]:
                
                x = G.nodes[node].get("x")
                y = G.nodes[node].get("y")
                sens_range = G.nodes[node].get("sens_range")
                comm_range = G.nodes[node].get("comm_range")

                sens_circle = plt.Circle((x, y), sens_range, edgecolor="green", facecolor="none", linestyle="--")
                comm_circle = plt.Circle((x, y), comm_range, edgecolor="pink", facecolor="none", linestyle="--")

                ax.add_patch(sens_circle)
                ax.add_patch(comm_circle)

        nx.draw_networkx_nodes(G, pos, node_size=200, node_color=node_colors, edgecolors="black", ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, ax=ax, style=edge_styles)
        
        labels = {node: node for node in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_color="black")

        plt.xlim(-50, 150)
        plt.ylim(-50, 150)
        plt.axis("off")
        plt.show()

    def Data_Reset(self):

        for CH_node in self.data.CH_nodes:
            CH_node.isCH = False
            CH_node.cluster_ID = None

        self.data.CH_nodes.clear()