import math

def distance(node1, node2):
    return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

# def distance(x1, y1, x2, y2):
#     return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)