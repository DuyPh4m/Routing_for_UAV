class Node(object):
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.cluster_ID = None
        self.sens_range = 30
        self.comm_range = 50
        self.dead = False
        self.isCH = False
        self.Tk = 0.2 / (1 - 0.2 * (1.0 % (1 / 0.2)))
        self.was_CH_in = -1
