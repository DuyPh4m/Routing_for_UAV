import numpy as np

from ACO import AntColonyOptimization

distances = np.array([[np.inf, 2, 5, 1],
                      [2, np.inf, 3, 6],
                      [5, 3, np.inf, 4],
                      [1, 6, 4, np.inf],])

ant_colony = AntColonyOptimization(distances=distances, n_ants=1, n_best=1, n_iterations=100, decay=0.95, alpha=1, beta=1)
shortest_path = ant_colony.Run()
print ("shorted_path: {}".format(shortest_path))