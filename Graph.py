from Agent import *
from BeliefBase import *
from typing import *
import random
import copy

type Connection = List[Tuple[int, Agent]]
type GraphEdges = Dict[Agent, List[Connection]]
type UpdateRule = Callable[[Agent], List[Interpretation]]
type TiebreakRule = Callable[[List[Interpretation]], Interpretation]

class Graph:
    def __init__(self, agenda: BeliefBase, agents: list[Agent]=list()) -> None:
        self.agenda: BeliefBase = agenda
        self.graph: GraphEdges = {agent: [] for agent in agents}


    def add_connections(self, agent: Agent, connections: list[Connection]) -> None:
        self.graph[agent] = connections
    

    def remove_connection(self, agent: Agent, connection: Agent) -> None:
        self.graph[agent].remove(connection)


    def complete_graph(self) -> None:
        for agent in self.graph:
            self.add_connections(agent, list(self.graph.keys()))


    def update(self) -> None:
        results = []

        for agent in self.graph:
            candidates = self.hamming_distance_rule(agent)
            result = self.tiebreaker_chance(candidates)
            results.append(result)

        for i, agent in enumerate(self.graph):
            agent.update_beliefs(results[i])


    def tiebreaker_chance(self, interps: List[Interpretation]) -> Interpretation:
        return random.choice(interps)


    def hamming_distance(self, x: Interpretation, y: Interpretation) -> int:
        count: int = 0

        for a, b in zip(x, y):
            if a != b:
                count += 1

        return count
    

    def hamming_distance_rule(self, agent: Agent) -> List[Interpretation]:
        candidates: List[Interpretation] = list()
        candidate_minimum: float = float('inf')

        for model in self.agenda.models:
            # print(f"The current model is {model}")
            current_distance: int = 0

            for connection in self.graph[agent]:
                for agent_model in connection.models:
                    distance_to_agent_model = self.hamming_distance(model, agent_model)
                    # print(f"The distance from {model} to {agent_model} is {distance_to_agent_model}.")
                    current_distance += distance_to_agent_model
                    # print(f"The total distance for {model} is {current_distance}.")

            if current_distance < candidate_minimum:
                candidates = [model]
                candidate_minimum = current_distance
            elif current_distance == candidate_minimum:
                candidates.append(model)

            # print(f"The current list of models is: {candidates}")

        # Commented out because we are now doing selection by random distribution
        # res: List[Interpretation] = list()
        # agent_minimum: int = candidate_minimum

        # for model in candidates:
        #     for agent_model in agent.models:
        #         current_distance: int = self.hamming_distance(model, agent_model)

        #         if current_distance < agent_minimum:
        #             res = [model]
        #             agent_minimum = current_distance
        #         elif current_distance == agent_minimum:
        #             res.append(model)

        return candidates
    
    
    def __str__(self):
        result = "The graph contains the following agents and their models:\n"

        for agent, connections in self.graph.items():
            result += f"Agent {agent.name} with models {agent.models}:\n"

            # for connection in connections:
            #     result += f"  Connected to: {connection.name}, Models: {connection.models}\n"

        return result
    
    def __eq__(self, other: 'Graph'):
        self_models = set()
        other_models = set()

        for self_agent in self.graph:
            self_models.add(self_agent.models[0])

        for other_agent in other.graph:
            other_models.add(other_agent.models[0])

        return self_models == other_models