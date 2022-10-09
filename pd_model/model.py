import random

import mesa
import numpy as np
from assign import assign_agent_base_attributes
from assign import assign_agent_reputation_attributes
from assign import assign_neighbour_values
from assign import assign_network_id
from assign import assign_random_group_id
from assign import assign_random_player_id
from mapping import gossip_decision_distributions_by_score
from mapping import pd_game_decision_distributions_by_score
from mapping import pd_payoff_matrix
from mapping import pd_result_matrix
from mapping import random_group_matching
from mapping import scoring_distributions_by_payoff_result
from mapping import stage_lists_by_game_type
from mapping import update_decision_distributions_by_score
from reporters import get_agent_reporters_by_game_type
from reporters import model_reporters_by_game_type


class SimpleAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        assign_agent_base_attributes(self)
        assign_agent_reputation_attributes(self)

    def get_pd_opponents(self):
        self.pd_game_opponent_1 = [
            agent
            for agent in self.model.schedule.agents
            if agent.group_id == self.group_id and agent.player_id == random_group_matching[self.player_id][0]
        ][0]
        self.pd_game_opponent_1_AgentID = self.pd_game_opponent_1.unique_id
        self.pd_game_opponent_2 = [
            agent
            for agent in self.model.schedule.agents
            if agent.group_id == self.group_id and agent.player_id == random_group_matching[self.player_id][1]
        ][0]
        self.pd_game_opponent_2_AgentID = self.pd_game_opponent_2.unique_id

    def set_pd_choices(self):
        if self.model.game_type == "random":
            self.pd_game_decision_1 = random.choice(["Defect", "Cooperate"])
            self.pd_game_decision_2 = random.choice(["Defect", "Cooperate"])
        else:
            opponent_1_reputation = getattr(self, "agent_" + str(self.pd_game_opponent_1.unique_id) + "_reputation")
            opponent_2_reputation = getattr(self, "agent_" + str(self.pd_game_opponent_2.unique_id) + "_reputation")
            self.pd_game_decision_1 = random.choice(
                pd_game_decision_distributions_by_score.get(opponent_1_reputation, None)
            )
            self.pd_game_decision_2 = random.choice(
                pd_game_decision_distributions_by_score.get(opponent_2_reputation, None)
            )

    def get_pd_payoffs(self):
        self.result_1 = pd_result_matrix[self.pd_game_decision_1][self.pd_game_opponent_1.pd_game_decision_1]
        self.result_2 = pd_result_matrix[self.pd_game_decision_2][self.pd_game_opponent_1.pd_game_decision_2]
        self.pd_game_opponent_2_pd_game_decision_2 = self.pd_game_opponent_1.pd_game_decision_2
        self.payoff_1 = pd_payoff_matrix[self.pd_game_decision_1][self.pd_game_opponent_1.pd_game_decision_1]
        self.payoff_2 = pd_payoff_matrix[self.pd_game_decision_2][self.pd_game_opponent_1.pd_game_decision_2]
        self.payoff_total += self.payoff_1 + self.payoff_2
        if self.model.schedule.steps > 0:
            self.payoff_mean = (self.payoff_total / 2) / self.model.schedule.steps
        else:
            self.payoff_mean = self.payoff_total / 2

    def set_pd_scoring(self):
        opponent_1_reputation = "agent_" + str(self.pd_game_opponent_1.unique_id) + "_reputation"
        opponent_2_reputation = "agent_" + str(self.pd_game_opponent_2.unique_id) + "_reputation"
        setattr(
            self,
            opponent_1_reputation,
            int(random.choice(scoring_distributions_by_payoff_result.get(self.payoff_1, None))),
        )
        setattr(
            self,
            opponent_2_reputation,
            int(random.choice(scoring_distributions_by_payoff_result.get(self.payoff_2, None))),
        )

    def set_gossip_choices(self):
        for i in range(1, len(self.neighbours_list) + 1):
            setattr(
                self,
                "gossip_decision_" + str(i),
                random.choice(
                    gossip_decision_distributions_by_score.get(
                        getattr(self, "neighbour_" + str(i) + "_reputation"), None
                    )
                ),
            )

    def set_gossip_dictionary(self):
        for i in range(1, len(self.neighbours_list) + 1):
            current_gossip_choice = getattr(self, "gossip_decision_" + str(i))
            gossip_dictionary = {}
            if current_gossip_choice in ["All", "High"]:
                for j in range(0, self.model.num_agents):
                    current_reputation = getattr(self, "agent_" + str(j) + "_reputation")
                    if current_reputation is None:
                        continue
                    elif current_reputation >= 8:
                        new_dictionary = {j: current_reputation}
                        gossip_dictionary = {**gossip_dictionary, **new_dictionary}
            if current_gossip_choice in ["All", "Low"]:
                for j in range(0, self.model.num_agents):
                    current_reputation = getattr(self, "agent_" + str(j) + "_reputation")
                    if current_reputation is None:
                        continue
                    elif current_reputation <= 3:
                        new_dictionary = {j: current_reputation}
                        gossip_dictionary = {**gossip_dictionary, **new_dictionary}
            setattr(self, "gossip_dictionary_" + str(i), gossip_dictionary)

    def set_update_choices(self):
        for i in range(1, len(self.neighbours_list) + 1):
            setattr(
                self,
                "update_decision_" + str(i),
                random.choice(
                    update_decision_distributions_by_score.get(
                        getattr(self, "neighbour_" + str(i) + "_reputation"), None
                    )
                ),
            )

    def get_gossip_dictionary(self):
        score_update_dictionary = {}
        for i in range(1, len(self.neighbours_list) + 1):
            new_score_update_dictionary = {}
            for j in range(1, len(self.neighbours_list) + 1):
                current_neighbour = getattr(self, "neighbour_" + str(i))
                current_neighbour_match = self.unique_id == getattr(
                    current_neighbour,
                    "neighbour_" + str(j) + "_AgentID",
                )
                current_gossip_dictionary = {}
                if current_neighbour_match:
                    current_gossip_dictionary = getattr(current_neighbour, "gossip_dictionary_" + str(j))
                    if current_gossip_dictionary != {}:
                        new_score_update_dictionary = {i: current_gossip_dictionary}

                    score_update_dictionary = {**score_update_dictionary, **new_score_update_dictionary}
        self.score_update_dictionary = score_update_dictionary

    def set_gossip_values(self):
        for i in range(0, self.model.num_agents):
            gossip_values = []
            for j in range(1, len(self.neighbours_list) + 1):
                current_gossip_value = None
                current_update_decision = getattr(self, "update_decision_" + str(j))
                if self.model.gossip_logic == "simple":
                    current_gossip_value = self.score_update_dictionary.get(j, {}).get(i, None)
                elif self.model.gossip_logic == "complex":
                    if current_update_decision:
                        current_gossip_value = self.score_update_dictionary.get(j, {}).get(i, None)
                if current_gossip_value is not None:
                    gossip_values += [current_gossip_value]
            setattr(self, "agent_" + str(i) + "_reputation_gossip", gossip_values)

    def set_gossip_scoring(self):
        for i in range(0, self.model.num_agents):
            current_reputation = getattr(self, "agent_" + str(i) + "_reputation")
            gossip_values = getattr(self, "agent_" + str(i) + "_reputation_gossip")
            if len(gossip_values) > 0:
                not_divergent_opinions = np.var(gossip_values) > 5
                gossip_consensus = round(np.mean(gossip_values), 0)
            else:
                not_divergent_opinions = True
                gossip_consensus = None
            if self.model.gossip_logic == "simple":
                simple_logic_rules = [
                    not_divergent_opinions,
                    len(gossip_values) > 0,
                ]
                if all(simple_logic_rules):
                    setattr(self, "agent_" + str(i) + "_reputation", gossip_consensus)
            elif self.model.gossip_logic == "complex":
                not_large_score_difference = abs(gossip_consensus, current_reputation) > 5
                complex_logic_rules = [not_divergent_opinions, len(gossip_values) > 0, not_large_score_difference]
                if all(complex_logic_rules):
                    setattr(self, "agent_" + str(i) + "_reputation", gossip_consensus)

    def step_start(self):
        assign_neighbour_values(self)

    def step_pd(self):
        self.get_pd_opponents()
        self.set_pd_choices()

    def step_payoffs(self):
        self.get_pd_payoffs()

    def step_scoring(self):
        self.set_pd_scoring()

    def step_gossip(self):
        self.set_gossip_choices()
        self.set_gossip_dictionary()

    def step_reflect(self):
        self.set_update_choices()
        self.get_gossip_dictionary()
        self.set_gossip_values()

    def step_update(self):
        self.set_gossip_scoring()

    def step_collect(self):
        self.model.datacollector.collect(self.model)


class SimpleModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, network_groups, total_networks, treatment_id, game_type, gossip_logic="simple"):
        self.num_agents = network_groups * 4 * total_networks
        self.network_agents = network_groups * 4
        self.total_networks = total_networks
        self.game_type = game_type
        self.gossip_logic = gossip_logic
        self.schedule = mesa.time.StagedActivation(self, stage_list=stage_lists_by_game_type[game_type])
        self.running = True
        # Create agents

        for i in range(self.num_agents):
            a = SimpleAgent(i, self)
            self.schedule.add(a)

        assign_network_id(model=self, network_agents=self.network_agents, treatment_id=treatment_id)

        assign_random_group_id(self)
        assign_random_player_id(self)

        self.datacollector = mesa.DataCollector(
            model_reporters=model_reporters_by_game_type[game_type],
            agent_reporters=get_agent_reporters_by_game_type(self),
        )

    def step(self):
        self.schedule.step()
        assign_random_group_id(self)
        assign_random_player_id(self)
