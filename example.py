import numpy as np

from ACO import AntColonyOptimization

distances = np.array([[np.inf, 5, 7, 3, np.inf, np.inf, np.inf, np.inf],
                      [5, np.inf, np.inf, np.inf, 2, 10, np.inf, np.inf],
                      [7, np.inf, np.inf, np.inf, np.inf, np.inf, 1, np.inf],
                      [3, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 11],
                      [np.inf, 2, np.inf, np.inf, np.inf, np.inf, np.inf,9],
                      [np.inf, 10, np.inf, np.inf, np.inf, np.inf, np.inf, 4],
                      [np.inf, np.inf, 1, np.inf, np.inf, np.inf, np.inf, 6],
                      [np.inf, np.inf, np.inf, 6, 11, 9, 4, np.inf]])

ant_colony = AntColonyOptimization(distances, 1, 1, 100, 0.95, alpha=1, beta=1)
shortest_path = ant_colony.run()
print ("shorted_path: {}".format(shortest_path))