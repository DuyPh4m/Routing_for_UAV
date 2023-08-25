import random
import math
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from array import *
from ACO import AntColonyOptimization

num = 30 # Number of nodes
rounds = 30 # Number of rounds
p = 0.2 # Initial CH selection probability
Eo = 1 # Initial energy of nodes
Et = Eo # Total energy
E_broadcast = 50 * 0.00001
E_elec = 50 * 0.00001
E_fs = 50 * 0.00001
ETX = 50 * 0.00001
ERX = 50 * 0.00001
min_percentage = 0.1
max_percentage = 0.2
a = min_percentage * num
b = max_percentage * num
min_CHs = math.ceil(a)
max_CHs = math.ceil(b)
dead_IDs = []
node_attributes = []
norm_edge_list = []
CH_edge_list = []
cluster_edge_list = []
nodes = [] # total nodes
norm_nodes = [] # nodes haven't been become CH in the last [1/p] rounds
CH_nodes = [] # store CH_nodes
clusters = [] # List to store clusters

G = nx.Graph()

class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.energy = Eo
        self.cluster_head = False
        self.cluster_id = None
        self.dead = False
        self.sens_range = 25
        self.comm_range = 50
        self.Tk = p / (1 - p * (1.0 % (1 / p)))  # CH election probability in round 1
        self.CHr = -1

def distance(node1, node2):
    return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

def generate_nodes():
    global nodes, norm_nodes
    for i in range(num):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        node = Node(i, x, y)
        attributes = {"id": i, "x": x, "y": y,"sens_range": node.sens_range, "comm_range": node.comm_range, "cluster_head": False, "dead": False}
        nodes.append(node)
        norm_nodes.append(node)
        G.add_node(i, **attributes)

    for node1 in nodes:
        next_nodes = [node for node in nodes if node.id > node1.id]
        for node2 in next_nodes:
                dist = distance(node1, node2)
                while(dist < 15 or dist > 20):
                    node2.x = random.uniform(0, 100)
                    node2.y = random.uniform(0, 100)
                    dist = min(distance(node2, other_node) for other_node in nodes if other_node != node2)
                G.nodes[node2.id]["x"] = node2.x
                G.nodes[node2.id]["y"] = node2.y    

def select_CH(round):
    global norm_nodes, CH_nodes
    for node in norm_nodes:
        temp = random.uniform(0,1)
        dist = float('inf')
        if len(CH_nodes) != 0:
            dist = min(distance(node, CH_node) for CH_node in CH_nodes if node != CH_node)
        if temp < node.Tk and dist > 30:
            node.cluster_head = True
            G.nodes[node.id]['cluster_head'] = True
            node.cluster_id = node.id
            CH_nodes.append(node)
            node.CHr = round
            norm_nodes.remove(node)
        else:
            node.cluster_head = False
            G.nodes[node.id]['cluster_head'] = False
            node.cluster_id = None

def update_norm_nodes(round):
    global nodes, norm_nodes, dead_IDs
    p = 1 - len(norm_nodes) / len(nodes)
    if (p < min_percentage):
        p = min_percentage
    if (p > max_percentage):
        p = max_percentage
    n = math.ceil(1 / p)
    for node in nodes:
        if node.CHr >= 0 and round - node.CHr >= n:
            if node not in norm_nodes:
                norm_nodes.append(node)
                node.cluster_head = False
                node.cluster_id = None
                G.nodes[node.id]["cluster_head"] = False
        if node.energy == 0:
            node.dead = True
            dead_IDs.append(node.id)
            for n in G.nodes():
                if node.id == G.nodes[n].get("id"):
                    G.nodes[n]["dead"] = True
                    print("Node {} is dead".format(G.nodes[n]["id"]))

def update_Tk(round):
    global nodes, norm_nodes
    for node in nodes:
        if node not in norm_nodes:
            node.Tk = 0
        else:
            node.Tk = p / (1 - p * (float(round) % (1/ p)))

def form_clusters():
    global clusters, CH_nodes, norm_nodes
    clusters.clear()
    for node in nodes:
        if node.cluster_head:
            clusters.append([node])
    non_CH_nodes = [node for node in nodes if node not in CH_nodes]
    for node in non_CH_nodes:
        min_distance = float('inf')
        closest_CH = None
        for CH_node in CH_nodes:
            distance_to_CH = distance(node, CH_node)
            if distance_to_CH < min_distance:
                min_distance = distance_to_CH
                closest_CH = CH_node
                if min_distance <= CH_node.sens_range:
                    node.cluster_id = CH_node.id
        if min_distance <= (node.sens_range) and node.cluster_id == closest_CH.id:
            G.add_edge(node.id, closest_CH.id, style='solid', edge_color='green')           

def round_simulation():
    global clusters
    for cluster in clusters:
        cluster_head = cluster[0]
        cluster_head.energy -= E_broadcast
        members = [node for node in cluster if node != cluster_head]
        for node in members:
            node.energy -= ETX
            cluster_head.energy -= ERX 

def select_additional_CH(round):
    global nodes, CH_nodes, G, H
    isolates = [node for node in nodes if node not in CH_nodes and node.cluster_id == None]
    ovlp_highest = 0
    chosen_one = None

    if len(isolates) <= 0:
        return False
    if len(isolates) > 0:
        for node in isolates:
            temp = 0
            for CH_node in CH_nodes:
                if distance(node, CH_node) <= CH_node.comm_range:
                    temp += 1
        if temp > ovlp_highest:
            ovlp_highest = temp
            chosen_one = node
    if chosen_one != None:
        G.nodes[chosen_one.id]["cluster_head"] = True
        G.nodes[chosen_one.id]["cluster_id"] = chosen_one.id
        CH_nodes.append(chosen_one)
        print("additional CH node: {}".format(chosen_one.id))
    else: 
        print("Cant select addtional CH nodes!")
        return False
    for node in isolates:
        if distance(node, chosen_one) <= node.sens_range and node != chosen_one:
            node.cluster_id = chosen_one.id
            G.add_edge(node.id, chosen_one.id, style='solid', edge_color='black')
        if node.id == chosen_one.id:
            node.CHr = round
            node.cluster_head = True
            node.cluster_id = chosen_one.id
            if node in norm_nodes:
                norm_nodes.remove(node)
    for CH_node in CH_nodes:
        if distance(CH_node, chosen_one) <= CH_node.comm_range and CH_node != chosen_one:
            H.add_node(chosen_one)
            H.add_edge(CH_node, chosen_one)
            G.add_edge(CH_node.id, chosen_one.id, style='solid', edge_color='blue')
    return True

def ACO_Simulation(CH_nodes):
    distances = []
    for CH_node1 in CH_nodes:
        dist = []
        for CH_node2 in CH_nodes:
            temp = distance(CH_node1, CH_node2)
            if 0 < temp < CH_node1.comm_range:
                dist.append(temp)
            else:
                dist.append(np.inf)
        distances.append(dist)
    print(distances)
    distances_matrix = np.array(distances)
    ant_colony = AntColonyOptimization(distances_matrix, 1, 1, 100, 0.95, alpha=1, beta=1)
    shortest_path = ant_colony.Run()
    if shortest_path == -1:
        print("error")
        return -1
    print ("shorted_path: {}".format(shortest_path))
    # sink_node = distance_matrix.shape[0] - 1
    # aco = AntColonyOptimization(num_ants=10, num_iterations=100, pheromone_weight=1.0, heuristic_weight=2.0, evaporation_rate=0.5)

generate_nodes()
print("min: {}, max: {}".format(min_CHs, max_CHs))
for round in range(rounds):
    update_norm_nodes(round)
    update_Tk(round)
        
    
    while(len(CH_nodes) < min_CHs):
        select_CH(round)  

    form_clusters()
    H = nx.Graph()
    H.add_nodes_from(CH_nodes)
    update_norm_nodes(round)
    
    for CH_node1 in CH_nodes:
        next_CH_nodes = [node for node in CH_nodes if node.id > CH_node1.id]
        for CH_node2 in next_CH_nodes:
            if distance(CH_node1, CH_node2) < CH_node1.comm_range:
                H.add_edge(CH_node1, CH_node2)
                G.add_edge(CH_node1.id, CH_node2.id, style='solid', edge_color='red')
    
    while(nx.is_connected(H) == False):
        if not select_additional_CH(round):
            break

    ACO_Simulation(CH_nodes)

    round_simulation()
    print(H),
    print("CH nodes:")
    for CH_node in CH_nodes:
        print(CH_node.id),
    
    edge_styles = [G[u][v]['style'] for u, v in G.edges()]
    edge_colors = [G[u][v]['edge_color'] for u, v in G.edges()]

    node_colors = ["red" if G.nodes[node]["dead"] else "lightgreen" if G.nodes[node].get("cluster_head", False) else "lightblue" for node in G.nodes]

    pos = {node: (G.nodes[node].get("x"), G.nodes[node].get("y")) for node in G.nodes if G.nodes[node].get("x") is not None and G.nodes[node].get("y") is not None}
    
    fig, ax = plt.subplots(figsize=(10, 10))

    nx.draw_networkx_nodes(G, pos, node_size=200, node_color=node_colors, edgecolors="black", ax=ax)
    
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, ax=ax, style=edge_styles)
    
    for node, (x, y) in pos.items():
        if G.nodes[node]["cluster_head"] == True:
            sens_range = G.nodes[node].get("sens_range")
            comm_range = G.nodes[node].get("comm_range")
            sens_circle = plt.Circle((x, y), sens_range, edgecolor="green", facecolor="none", linestyle="--")
            comm_circle = plt.Circle((x, y), comm_range, edgecolor="pink", facecolor="none", linestyle="--")
            ax.add_patch(sens_circle)
            ax.add_patch(comm_circle)
    
    labels = {node: node for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=labels, font_color="black")

    plt.xlim(-50, 150)
    plt.ylim(-50, 150)
    plt.axis("off")
    plt.show()

    # ACO_Simulation(CH_nodes)

    # round_simulation()

    CH_nodes.clear()
    for node in G.nodes:
        G.nodes[node]["cluster_head"] = False
    for node in nodes:
        node.cluster_head = False
        node.cluster_id = None

    for node in norm_nodes:
        node.cluster_id = None

    G.remove_edges_from(list(G.edges()))
    H.clear()