import random
import math
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk

num = 25 # Number of nodes
rounds = 30 # Number of rounds
p = 0.2 # Initial CH selection probability
Eo = 1 # Initial energy of nodes
Et = Eo # Total energy
# k = math.ceil(n * p) # Number of cluster heads per round
CH_id = [] # store CH_id
clusters = [] # List to store clusters
E_broadcast = 50 * 0.00001
E_elec = 50 * 0.00001
E_fs = 50 * 0.00001
ETX = 50 * 0.00001
ERX = 50 * 0.00001
a = 0.2 * num
b = 0.4 * num
min_CHs = math.ceil(a)
max_CHs = math.ceil(b)
# x_min = 0
# x_max = 0
# y_min = 200
# y_max = 200
# a = 0,3 * num
# b = 0,5 * num
# # min_CHs = math.ceil(a) # minimum number of CHs in network
# # max_CHs = math.ceil(b) # maximum number of CHs in network
# bits = 128 # length of data transmitted
dead_IDs = []
node_attributes = []
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
        self.comm_range = 20
        self.Tk = p / (1 - p * (1.0 % (1 / p)))  # CH election probability in round 1
        self.CHr = -1
    # def set_CHr(self, round):
    #     self.CHr = round

nodes = [] # total nodes
norm_nodes = [] # nodes haven't been become CH in the last [1/p] rounds

def distance(node1, node2):
    return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

for i in range(num):
    x = random.uniform(0, 100)
    y = random.uniform(0, 100)
    # print("Node {}: x={}, y={}".format(i,x,y))
    node = Node(i, x, y)
    attributes = {"id": i, "x": x, "y": y, "comm_range": node.comm_range, "cluster_head": False, "dead": False}
    
    # print("Node {}: x={}, y={}".format(node.id,node.x,node.y))
    nodes.append(node)
    norm_nodes.append(node)
    G.add_node(i, **attributes)
# x_min -= node.comm_range
# x_max += node.comm_range
# y_min -= node.comm_range
# y_min += node.comm_range
# print("{} {} {} {}".format(x_min, x_max, y_min, y_max))
# for node in G.nodes:
    # print("Node {}: x={}, y={}".format(node, G.nodes[node].get("x"), G.nodes[node].get("y")))
for node1 in nodes:
    for node2 in nodes:
        if node2 != node1:
            while(distance(node1, node2) < 10):
                node2.x = random.uniform(0, 100)
                node2.y = random.uniform(0, 100)
            G.nodes[node2.id]["x"] = node2.x
            G.nodes[node2.id]["y"] = node2.y    


def select_CH(round):
    # CH_id = []
    for node in norm_nodes:
        temp = random.uniform(0,1)
        if temp < node.Tk and len(CH_id) < max_CHs:
            node.cluster_head = True
            G.nodes[node.id]['cluster_head'] = True
            node.cluster_id = node.id
            CH_id.append(node.id)
            node.CHr = round
            # if node in norm_nodes:
            norm_nodes.remove(node)
        else:
            node.cluster_head = False
            G.nodes[node.id]['cluster_head'] = False
            node.cluster_id = None

def update_G(round):
    p = 1 - len(norm_nodes) / len(nodes)
    if (p < (min_CHs / num)):
        p = min_CHs / num
    if (p > (max_CHs / num)):
        p = max_CHs / num
    n = math.ceil(1 / p)
    for node in nodes:
        if 0 <= node.CHr <= (round - n):
            if node not in norm_nodes:
                norm_nodes.append(node)
                node.cluster_head = False
                node.cluster_id = None
                G.nodes[node.id]["cluster_head"] = False
        if node.energy == 0:
            node.dead = True
            dead_IDs.append(node.id)
            for n in G.nodes:
                if node.id == G.nodes[n].get("id"):
                    G.nodes[n]["dead"] = True
                    print("Node {} is dead".format(G.nodes[n]["id"]))

def update_Tk(round):
    for node in nodes:
        if node not in norm_nodes:
            node.Tk = 0
        else:
            node.Tk = p / (1 - p * (float(round) % (1/ p)))

def form_clusters():
    clusters.clear()
    for node in nodes:
        if node.cluster_head:
            clusters.append([node])
    CH_nodes = [node for node in nodes if node.cluster_head]
    nonCH_nodes = [node for node in nodes if not node.cluster_head]
    for node in nonCH_nodes:
        min_distance = float('inf')
        closest_CH = None
        for CH_node in CH_nodes:
            distance_to_CH = distance(node, CH_node)
            if distance_to_CH < min_distance:
                min_distance = distance_to_CH
                closest_CH = CH_node
        if min_distance <= (node.comm_range):
            G.add_edge(node.id, closest_CH.id)           

def round_simulation():
    for cluster in clusters:
        cluster_head = cluster[0]
        cluster_head.energy -= E_broadcast
        members = [node for node in cluster if node != cluster_head]
        for node in members:
            node.energy -= ETX
            # node.energy -= (E_elec*bits + E_fs*bits*distance(cluster_head, node)**2)
            cluster_head.energy -= ERX 
            # cluster_head.energy -= (E_elec*bits + E_fs*bits*distance(cluster_head, node)**2)
        print("Cluster head ID: {}, energy: {}".format(cluster_head.id, cluster_head.energy))
        # for node in members: 
            # print("Member ID: {}, energy: {}".format(node.id, node.energy))
        

for r in range(rounds):
    CH_id = []
    print("Round", r)
    update_Tk(r)
    while(len(CH_id) == 0 or len(CH_id) < min_CHs):
        select_CH(r)
    # print(CH_id)
    form_clusters()
    round_simulation()
    if r == 7:
        for node in G.nodes:
            if G.nodes[node]["id"] == 7:
                G.nodes[node]["dead"] = True
    update_G(r)
    node_colors = ["red" if G.nodes[node]["dead"] else "lightgreen" if G.nodes[node].get("cluster_head", False) else "lightblue" for node in G.nodes]
    pos = {node: (G.nodes[node].get("x"), G.nodes[node].get("y")) for node in G.nodes if G.nodes[node].get("x") is not None and G.nodes[node].get("y") is not None}
    
    fig, ax = plt.subplots(figsize=(10, 10))

    nx.draw_networkx_nodes(G, pos, node_size=200, node_color=node_colors, edgecolors="black", ax=ax)
    
    nx.draw_networkx_edges(G, pos, ax=ax)

    for node, (x, y) in pos.items():
        comm_range = G.nodes[node].get("comm_range", 5)
        circle = plt.Circle((x, y), comm_range, edgecolor="red", facecolor="none", linestyle="--")
        ax.add_patch(circle)
    
    labels = {node: node for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=labels, font_color="black")

    plt.xlim(-20, 120)
    plt.ylim(-20, 120)
    plt.axis("off")
    plt.show()


    # nx.draw(G, pos, with_labels=True, node_size=200, node_color=node_colors, edge_color="black")
    # plt.show()

    for node in G.nodes:
        # if G.nodes[node].get("dead", True) == True:
            # G.remove_node(node)
        # if G.nodes[node].get("id") not in dead_IDs:    
            G.nodes[node]["cluster_head"] = False
    for node in nodes:
        node.cluster_head = False
    G.remove_edges_from(list(G.edges()))

    # node_colors = ["lightgreen" if node.cluster_head else "lightblue" for node in G.nodes]
    # pos = {node.id: (node.x, node.y) for node in G.nodes}
    # nx.draw(G, pos, with_labels=True, node_size=200, node_color=node_colors)
    # plt.show()

# for node in nodes:
    # print("Node", node.id, "Energy:", node.energy)

# node_colors = ["green" if G.nodes[node]["CH"] else "lightblue" for node in G.nodes]
# pos = {node: (G.nodes[node]["x"], G.nodes[node]["y"]) for node in G.nodes}
# nx.draw(G, pos, with_labels=True, node_size=200, node_color=node_colors)
# plt.show()