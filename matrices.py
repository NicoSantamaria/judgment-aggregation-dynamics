import numpy as np
from itertools import product
from functools import reduce
from Graph import *
from typing import *
from AgentFromModels import *
from GraphFromModels import *
from copy import deepcopy

# comments:
# 1. convert to matrices to np.ndarray for better performance

type Matrix = np.ndarray
type StateGraphMatrix = List[List[int]]
type State = List[Tuple[str, Interpretation]]

class MarkovChain:
    def __init__(self, graph: GraphFromModels):
        # can probably remove the self.graph ultimately...
        self.graph: GraphFromModels = graph
        self.agents: List[AgentFromModels] = list(graph.graph)
        self.model_matrix: Matrix = np.matrix_transpose(graph.models)

        self.coord_matrix: Matrix = self._get_coord_matrix(self.agents, self.model_matrix)
        self.adjacency = self._get_adjacency_matrix(self.agents, graph)
        self.states: List[State] = self._generate_states(self.agents, graph)
        # self.state_graph_matrix: StateGraphMatrix = self.build_state_graph()

    @staticmethod
    def _get_coord_matrix(agents: List[AgentFromModels], model_matrix: Matrix) -> Matrix:
        rows: int = len(model_matrix[0])
        cols: int = len(agents)
        coord_matrix: Matrix = np.zeros((rows, cols))
        
        for i, agent in enumerate(agents):
            for j, model in enumerate(np.transpose(model_matrix)):
                if agent.model == tuple(model):
                    coord_matrix[j, i] = 1

        return coord_matrix


    @staticmethod
    def _get_adjacency_matrix(agents: List[AgentFromModels], graph: GraphFromModels) -> Matrix:
        dim: int = len(agents)
        adjacency: Matrix = np.zeros((dim, dim))

        for i in range(dim):
            for j in range(dim):
                agent = agents[i]
                connection = agents[j]

                if connection in graph.graph[agent]:
                    adjacency[i, j] = 1

        return adjacency


    @staticmethod
    def _generate_states(agents: List[AgentFromModels], graph: GraphFromModels) -> List[Matrix]:
        index: int = 0
        length: int = len(graph.models) ** len(agents)
        states: List[Matrix] = [None] * length

        for combo in product(graph.models, repeat=len(agents)):
            state: Matrix = np.matrix(combo)
            # may need the transpose instead -- test
            states[index] = state
            index += 1

        return states

    
    @staticmethod
    def model_distances(mat1: Matrix, mat2: Matrix) -> Matrix:
        rows: int = mat1.shape[0]
        cols: int = mat2.shape[1]
        distance_matrix: Matrix = np.zeros((rows, cols))

        for i, model1 in enumerate(mat1):
            for j, model2 in enumerate(np.transpose(mat2)):
                distance: int = 0

                for pos1, pos2 in zip(tuple(model1), tuple(model2)):
                    if pos1 != pos2:
                        distance += 1

                distance_matrix[i, j] = distance

        return distance_matrix
    

    def matrix_update_rule(self) -> Matrix:
        next_coord_matrix: Matrix = np.matmul(
            self.model_distances(
                np.transpose(self.model_matrix), 
                np.matmul(self.model_matrix, self.coord_matrix)
            ),
            np.transpose(self.adjacency)
        )

        for i, col in enumerate(np.transpose(next_coord_matrix)):
            col_min: int = min(col)
            
            for j, entry in enumerate(col):
                if entry == col_min:
                    next_coord_matrix[j, i] = 1
                else:
                    next_coord_matrix[j, i] = 0

        return next_coord_matrix
    

    def build_state_graph(self) -> StateGraphMatrix:
        return
    

    # works, as far as I can tell
    def hamming_distance_rule(self, models: List[Interpretation]) -> List[Interpretation]:
        candidates: List[Interpretation] = self.graph.models
        candidate_minimum: float = float('inf')

        for candidate in candidates:
            current_distance: int = 0

            for model in models:
                distance_to_model = self.graph.hamming_distance(candidate, model)
                current_distance += distance_to_model

            if current_distance < candidate_minimum:
                candidates = [candidate]
                candidate_minimum = current_distance
            elif current_distance == candidate_minimum:
                candidates.append(candidate)

        return candidates
    
    
    def fast_exponent(self, mat: Matrix) -> Matrix:
        eigenvalues, eigenvectors = np.linalg.eig(mat)
        diagonal = np.diag(eigenvalues)
        trans_matrix_inv = np.linalg.inv(eigenvectors)

        return reduce(np.matmul, [
            eigenvectors, 
            np.linalg.matrix_power(diagonal, 1000), 
            trans_matrix_inv
        ])

    def find_stationary(self, mat: Matrix) -> Matrix:
        eigenvalues, eigenvectors = np.linalg.eig(mat)
        stationary_index = np.where(np.isclose(eigenvalues, 1))[0][0]
        stationary_distribution = eigenvectors[:, stationary_index]
        stationary_distribution /= np.sum(stationary_distribution)

        return stationary_distribution
    
props = ['p', 'q', 'r']
I = BeliefBase(props, [['iff', 'r', 'implies', 'p', 'q']])

J1 = AgentFromModels((1, 0, 0), 'A')
J2 = AgentFromModels((1, 1, 1), 'B')
J3 = AgentFromModels((0, 0, 1), 'C')

G = GraphFromModels(I.models, [J1, J2, J3])

G.add_connections(J1, [J1, J2, J3])
G.add_connections(J2, [J1, J2])
G.add_connections(J3, [J3])

MC = MarkovChain(G)

MC.matrix_update_rule()

# A = np.array([[0, 0, 1],
#               [1, 0, 0],
#               [0, 1, 1],
#               [1, 1, 1]])

# B = np.array([[1, 1, 0],
#               [0, 1, 0],
#               [0, 1, 1]])

# MC.model_distances(A, B)