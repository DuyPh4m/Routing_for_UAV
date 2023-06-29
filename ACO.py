import numpy as np

class AntColonyOptimization:
    def __init__(self, num_ants, num_iterations, pheromone_weight, heuristic_weight, evaporation_rate):
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.pheromone_weight = pheromone_weight
        self.heuristic_weight = heuristic_weight
        self.evaporation_rate = evaporation_rate

    def find_optimal_path(self, distance_matrix):
        num_nodes = distance_matrix.shape[0]
        pheromone_matrix = np.ones((num_nodes, num_nodes))
        best_path = None
        best_distance = np.inf

        for iteration in range(self.num_iterations):
            ant_paths = self.construct_ant_paths(distance_matrix, pheromone_matrix)
            self.update_pheromone_matrix(pheromone_matrix, ant_paths)
            
            # Find the best ant path
            for path in ant_paths:
                distance = self.calculate_path_distance(path, distance_matrix)
                if distance < best_distance:
                    best_path = path
                    best_distance = distance

            # Evaporate pheromones
            pheromone_matrix *= (1 - self.evaporation_rate)

        return best_path, best_distance

    def construct_ant_paths(self, distance_matrix, pheromone_matrix):
        num_nodes = distance_matrix.shape[0]
        ant_paths = []

        for ant in range(self.num_ants):
            visited = np.zeros(num_nodes, dtype=bool)
            path = []
            current_node = np.random.randint(num_nodes)
            path.append(current_node)
            visited[current_node] = True

            while len(path) < num_nodes:
                probabilities = self.calculate_transition_probabilities(current_node, visited, distance_matrix, pheromone_matrix)
                next_node = np.random.choice(np.arange(num_nodes), p=probabilities)
                path.append(next_node)
                visited[next_node] = True
                current_node = next_node

            ant_paths.append(path)

        return ant_paths

    
    def calculate_transition_probabilities(self, current_node, visited, distance_matrix, pheromone_matrix):
        num_nodes = distance_matrix.shape[0]
        unvisited_nodes = np.where(~visited)[0]
        pheromone_values = pheromone_matrix[current_node, unvisited_nodes]
        heuristic_values = 1.0 / distance_matrix[current_node, unvisited_nodes]
    
        probabilities = np.zeros(num_nodes)
        probabilities[unvisited_nodes] = (pheromone_values**self.pheromone_weight) * (heuristic_values**self.heuristic_weight)
        probabilities /= np.sum(probabilities)
    
        return probabilities


    def update_pheromone_matrix(self, pheromone_matrix, ant_paths):
        num_nodes = pheromone_matrix.shape[0]

        for path in ant_paths:
            for i in range(num_nodes - 1):
                current_node = path[i]
                next_node = path[i+1]
                pheromone_matrix[current_node, next_node] += 1
                pheromone_matrix[next_node, current_node] += 1  # Add this line to update both directions


    def calculate_path_distance(self, path, distance_matrix):
        distance = 0

        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i+1]
            distance += distance_matrix[current_node, next_node]

        return distance
# Example usage
distance_matrix = np.array([[0, 2, 4, 5],
                            [2, 0, 7, 3],
                            [4, 7, 0, 8],
                            [5, 3, 8, 0]])

aco = AntColonyOptimization(num_ants=10, num_iterations=100, pheromone_weight=1.0, heuristic_weight=2.0, evaporation_rate=0.5)
best_path, best_distance = aco.find_optimal_path(distance_matrix)

print("Best path:", best_path)
print("Best distance:", best_distance)
