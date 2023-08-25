class Node(object):
    def __init__(self, id, x, y, p=0):
        self.id = id
        self.x = x
        self.y = y
        self.cluster_ID = None
        self.sens_range = 30
        self.comm_range = 50
        self.dead = False
        self.isCH = False
        if p!= 0:
            self.Tk = p / (1 - p * (1.0 % (1 / p)))
        else:
            self.Tk = 0
        self.was_CH_in = -1