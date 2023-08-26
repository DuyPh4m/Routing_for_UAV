import random
import math
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from Calculation import distance

class LeachProtocol(object): 
    def __init__(self, p, min_per, max_per, data, round):
        self.p = p
        self.min_per = min_per
        self.max_per = max_per
        self.data = data
        self.round = round
        self.clusters = []
       
    def Run(self):
        self.Select_CH()
        self.Form_Cluters()
        self.Update_Tk()
        self.Update_Norms()

    def Select_CH(self):
        num = len(self.data.nodes)
        current_amount = 0.0

        while current_amount < self.min_per * num or current_amount > self.max_per * num:
            
            for node in self.data.norm_nodes:

                prob = random.uniform(0, 1)

                if prob < node.Tk:

                    valid = True

                    for CH_node in self.data.CH_nodes:
                        dx = CH_node.x - node.x
                        dy = CH_node.y - node.y
                        dist = math.sqrt(dx**2 + dy**2)

                        if dist < 30 or dist > 70:
                            valid = False
                            break
                    
                    if valid:
                        node.isCH = True
                        node.Cluster_ID = node.id
                        self.data.CH_nodes.append(node)
                        self.data.norm_nodes.remove(node)
                        node.was_CH_in = self.round
                        current_amount += 1

    def Update_Tk(self):
        for node in self.data.nodes:

            if node in self.data.CH_nodes:
                node.Tk = 0
            else:
                node.Tk = self.p / (1 - self.p * (float(self.round) % (1/ self.p)))

    def Update_Norms(self):
        self.p = 1 - len(self.data.norm_nodes) / len(self.data.nodes)

        if self.p < self.min_per:
            self.p = self.min_per

        if self.p > self.max_per:
            self.p = self.max_per
        
        n = math.ceil(1 / self.p)

        for node in self.data.nodes:
            if node.was_CH_in >= 0 and self.round - node.was_CH_in >= n and node not in self.data.norm_nodes:
                self.data.norm_nodes.append(node)
                node.isCH = False
                node.cluster_ID = None

    def Form_Cluters(self):
        self.clusters.clear()

        for CH_node in self.data.CH_nodes:
            self.clusters.append([CH_node])

        for node in self.data.nodes:

            if node.isCH == False and node.id != -1:
                min_dis = float('inf')
                closest = None
                
                for CH_node in self.data.CH_nodes:
                    curr_dis = distance(node, CH_node)
                    if curr_dis < min_dis:
                        min_dis = curr_dis
                        closest = CH_node
                
                if min_dis <= node.sens_range:
                    node.cluster_ID = closest.id