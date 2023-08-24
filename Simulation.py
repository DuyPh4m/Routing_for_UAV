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

            self.Add_CHs_2(round=r)

            self.Draw()
            self.Data_Reset()

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

    def Add_CHs(self, round):

        H = nx.Graph()

        for CH_node in self.data.CH_nodes:
            H.add_node(CH_node.id, x=CH_node.x, y=CH_node.y, comm_range=CH_node.comm_range)
        
        for CH_node1 in self.data.CH_nodes:
            for CH_node2 in self.data.CH_nodes:
                if CH_node1 != CH_node2 and distance(CH_node1, CH_node2) <= CH_node1.comm_range:
                    H.add_edge(CH_node1, CH_node2)

        while nx.is_connected(H) == False:
            
            isolates = [node for node in self.data.norm_nodes if node.cluster_ID == None]

            if len(isolates) == 0:
                print("cant connect CHs")
                return
            
            top_overlap = 0
            chosen_one = None

            for isolate in isolates:
                temp = 0

                for CH_node in self.data.CH_nodes:
                    if distance(isolate, CH_node) <= CH_node.comm_range:
                        temp += 1

                if temp > top_overlap:
                    top_overlap = temp
                    chosen_one = isolate

            if chosen_one == None:
                print("cant connect CHs")
                return

            chosen_one.isCH = True
            chosen_one.cluster_ID = chosen_one.id
            chosen_one.was_CH_in = round

            self.data.CH_nodes.append(chosen_one)
            self.data.norm_nodes.remove(chosen_one)

            H.add_node(chosen_one.id, x=chosen_one.x, y=chosen_one.y, comm_range=chosen_one.comm_range)

            for CH_node in self.data.CH_nodes:
                if CH_node != chosen_one and distance(CH_node, chosen_one) <= CH_node.comm_range:
                    H.add_edge(CH_node.id, chosen_one.id)

    def Add_CHs_2(self, round):

        H = nx.Graph()

        sum_x = 0.0
        sum_y = 0.0

        for CH_node in self.data.CH_nodes:
            H.add_node(CH_node.id, x=CH_node.x, y=CH_node.y, comm_range=CH_node.comm_range)
            sum_x += CH_node.x
            sum_y += CH_node.y

        
        for CH_node1 in self.data.CH_nodes:
            for CH_node2 in self.data.CH_nodes:
                if CH_node1 != CH_node2 and distance(CH_node1, CH_node2) <= CH_node1.comm_range:
                    H.add_edge(CH_node1, CH_node2)

        while nx.is_connected(H) == False:
            
            isolates = [node for node in self.data.nodes if node.cluster_ID == None]

            if len(isolates) == 0:
                return False
            
            closest_to_centroid = float('inf')
            chosen_one = None

            for isolate in isolates:
                
                centroid_x = sum_x / len(self.data.CH_nodes)
                centroid_y = sum_y / len(self.data.CH_nodes)

                temp = math.sqrt((isolate.x - centroid_x)**2 + (isolate.y - centroid_y)**2)

                if temp < closest_to_centroid:
                    closest_to_centroid = temp
                    chosen_one = isolate

            if chosen_one == None:
                return False

            chosen_one.isCH = True
            chosen_one.cluster_ID = chosen_one.id
            chosen_one.was_CH_in = round

            self.data.CH_nodes.append(chosen_one)
            if chosen_one in self.data.norm_nodes:
                self.data.norm_nodes.remove(chosen_one)

            sum_x += chosen_one.x
            sum_y += chosen_one.y

            H.add_node(chosen_one.id, x=chosen_one.x, y=chosen_one.y, comm_range=chosen_one.comm_range)

            for CH_node in self.data.CH_nodes:
                if CH_node != chosen_one and distance(CH_node, chosen_one) <= CH_node.comm_range:
                    H.add_edge(CH_node, chosen_one)

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

        for node in self.data.CH_nodes:
            node.isCH = False
            node.cluster_ID = None

        self.data.CH_nodes.clear()