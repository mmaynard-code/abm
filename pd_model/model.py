import random

import mesa
import numpy as np
from assign import assign_agent_base_attributes
from assign import assign_agent_reputation_attributes
from assign import assign_neighbour_values
from assign import assign_network_id
from assign import assign_random_group_id
from assign import assign_random_player_id
from mapping import complex_gossip_decision_neighbour_distributions_by_score
from mapping import complex_gossip_decision_subject_distributions_by_score
from mapping import pd_decision_distributions_by_score
from mapping import pd_payoff_matrix
from mapping import pd_result_matrix
from mapping import random_group_matching
from mapping import scoring_distributions_by_payoff_result
from mapping import simple_gossip_decision_neighbour_distributions_by_score
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
        """
        Gets pd_opponent_1 and pd_opponent_2 for each agent based on the preassigned
        group_id and player_id using the random_group_matching lookup mapping

        Dependent on assign_random_group_ids and assign_random_player_ids functions creating required values
        """
        self.pd_opponent_1 = [
            agent
            for agent in self.model.schedule.agents
            if agent.group_id == self.group_id and agent.player_id == random_group_matching[self.player_id][0]
        ][0]
        self.pd_opponent_1_AgentID = self.pd_opponent_1.unique_id
        self.pd_opponent_2 = [
            agent
            for agent in self.model.schedule.agents
            if agent.group_id == self.group_id and agent.player_id == random_group_matching[self.player_id][1]
        ][0]
        self.pd_opponent_2_AgentID = self.pd_opponent_2.unique_id

    def set_pd_decisions(self):
        """
        Sets pd_decisions for each agent based on the game_type parameter. In all other than random game_types the decision
        is made through selection of a random value from a probability matrix
        """
        if self.model.game_type == "random":
            self.pd_decision_1 = random.choice(["Defect", "Cooperate"])
            self.pd_decision_2 = random.choice(["Defect", "Cooperate"])
        else:
            opponent_1_reputation = getattr(self, "agent_" + str(self.pd_opponent_1.unique_id) + "_reputation")
            opponent_2_reputation = getattr(self, "agent_" + str(self.pd_opponent_2.unique_id) + "_reputation")
            self.pd_decision_1 = random.choice(pd_decision_distributions_by_score.get(opponent_1_reputation, None))
            self.pd_decision_2 = random.choice(pd_decision_distributions_by_score.get(opponent_2_reputation, None))

    def calculate_pd_payoffs(self):
        """
        Calculates all pd_payoff variables for each agent based on their and their opponents decision as specified in
        the pd_result_matrix.
        """
        self.result_1 = pd_result_matrix[self.pd_decision_1][self.pd_opponent_1.pd_decision_1]
        self.result_2 = pd_result_matrix[self.pd_decision_2][self.pd_opponent_1.pd_decision_2]
        self.pd_opponent_2_pd_decision_2 = self.pd_opponent_1.pd_decision_2
        self.payoff_1 = pd_payoff_matrix[self.pd_decision_1][self.pd_opponent_1.pd_decision_1]
        self.payoff_2 = pd_payoff_matrix[self.pd_decision_2][self.pd_opponent_1.pd_decision_2]
        self.payoff_total += self.payoff_1 + self.payoff_2
        if self.model.schedule.steps > 0:
            self.payoff_mean = (self.payoff_total / 2) / self.model.schedule.steps
        else:
            self.payoff_mean = self.payoff_total / 2

    def set_pd_scoring(self):
        """
        Sets reputation scores for opponents through the selection of a random value from a probability matrix
        """
        opponent_1_reputation = "agent_" + str(self.pd_opponent_1.unique_id) + "_reputation"
        opponent_2_reputation = "agent_" + str(self.pd_opponent_2.unique_id) + "_reputation"
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

    def set_gossip_decisions(self):
        """
        Sets gossip_decisions for each agent with logic dependent on the gossip_logic parameter.

        simple
            the decision as to whether to gossip is dependent on the reputation score that the agent has
            for each neighbour, it has four possibilities:
                All - share all reputation scores with neighbour
                High - share reputations scores >= 8 with neighbour
                Low - share reputation scores <= 3 with neighbour
                None - share no reputation scores with neighbour
            with the probability of All / High / Low increasing with reputation score value
        complex
            the decision as to whether to gossip is dependent on both the reputation score that the agent has
            for each neighbour, as well as the reputation score for the gossip subject. Each of these values
            is boolean and gossip requires both to be True.
        """
        if self.model.gossip_logic == "simple":
            for i in range(1, len(self.neighbours_list) + 1):
                setattr(
                    self,
                    "gossip_decision_neighbour_" + str(i),
                    random.choice(
                        simple_gossip_decision_neighbour_distributions_by_score.get(
                            getattr(self, "neighbour_" + str(i) + "_reputation"), None
                        )
                    ),
                )
        elif self.model.gossip_logic == "complex":
            for i in range(0, self.model.num_agents):
                setattr(
                    self,
                    "gossip_decision_subject_" + str(i),
                    random.choice(
                        complex_gossip_decision_subject_distributions_by_score.get(
                            getattr(self, "agent_" + str(i) + "_reputation"), None
                        )
                    ),
                )
            for i in range(1, len(self.neighbours_list) + 1):
                setattr(
                    self,
                    "gossip_decision_neighbour_" + str(i),
                    random.choice(
                        complex_gossip_decision_neighbour_distributions_by_score.get(
                            getattr(self, "neighbour_" + str(i) + "_reputation"), None
                        )
                    ),
                )

    def set_gossip_dictionary(self):
        """
        Sets the gossip_dictionary variable for each neighbour based on the gossip_logic parameter.
        The gossip_dictionary contains the reputation scores that the agent is choosing to share with
        each neighbour.
        """
        if self.model.gossip_logic == "simple":
            for i in range(1, len(self.neighbours_list) + 1):
                current_gossip_choice = getattr(self, "gossip_decision_neighbour_" + str(i))
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
        elif self.model.gossip_logic == "complex":
            for i in range(1, len(self.neighbours_list) + 1):
                current_gossip_choice = getattr(self, "gossip_decision_neighbour_" + str(i))
                gossip_dictionary = {}
                for j in range(0, self.model.num_agents):
                    neighbour_gossip_choice = getattr(self, "gossip_decision_neighbour_" + str(i))
                    subject_gossip_choice = getattr(self, "gossip_decision_subject_" + str(j))
                    current_gossip_choice = all([neighbour_gossip_choice, subject_gossip_choice])
                    if current_gossip_choice:
                        current_reputation = getattr(self, "agent_" + str(j) + "_reputation")
                        if current_reputation is None:
                            continue
                        elif current_reputation >= 8:
                            new_dictionary = {j: current_reputation}
                            gossip_dictionary = {**gossip_dictionary, **new_dictionary}
                setattr(self, "gossip_dictionary_" + str(i), gossip_dictionary)

    def set_update_decisions(self):
        """
        Set update_decisions for each agent as to whether they choose to update their reputations scores
        based on the gossip values they receive for each neighbour. This is through the selection of a
        random value from a probability matrix
        """
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

    def set_update_dictionary(self):
        """
        Sets the update_dictionary for the agent based on the available gossip_dictionaries that their
        neighbours have shared with them as well as the agents update_decision value.
        """
        update_dictionary = {}
        for i in range(1, len(self.neighbours_list) + 1):
            new_update_dictionary = {}
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
                        new_update_dictionary = {i: current_gossip_dictionary}

                    update_dictionary = {**update_dictionary, **new_update_dictionary}
        self.update_dictionary = update_dictionary

    def set_gossip_values(self):
        """
        Sets the gossip_values for each agents' reputation score based on the update_dictionary
        """
        for i in range(0, self.model.num_agents):
            gossip_values = []
            for j in range(1, len(self.neighbours_list) + 1):
                current_gossip_value = None
                current_update_decision = getattr(self, "update_decision_" + str(j))
                if self.model.gossip_logic == "simple":
                    current_gossip_value = self.update_dictionary.get(j, {}).get(i, None)
                elif self.model.gossip_logic == "complex":
                    if current_update_decision:
                        current_gossip_value = self.update_dictionary.get(j, {}).get(i, None)
                if current_gossip_value is not None:
                    gossip_values += [current_gossip_value]
            setattr(self, "agent_" + str(i) + "_reputation_gossip", gossip_values)

    def set_gossip_scoring(self):
        """
        Sets the agents reputation scores for each agent based on the gossip_values for each other agent
        when the relevant logic_rules are met.
        """
        for i in range(0, self.model.num_agents):
            current_reputation = getattr(self, "agent_" + str(i) + "_reputation")
            gossip_values = getattr(self, "agent_" + str(i) + "_reputation_gossip")
            not_divergent_opinions = False
            gossip_consensus = None
            not_large_score_difference = False
            if len(gossip_values) > 0:
                not_divergent_opinions = np.var(gossip_values) < 5
                gossip_consensus = round(np.mean(gossip_values), 0)
                if current_reputation is not None:
                    not_large_score_difference = abs(gossip_consensus - current_reputation) < 5

            if self.model.gossip_logic == "simple":
                simple_logic_rules = [
                    not_divergent_opinions,
                    len(gossip_values) > 0,
                ]
                if all(simple_logic_rules):
                    setattr(self, "agent_" + str(i) + "_reputation", gossip_consensus)
            elif self.model.gossip_logic == "complex":
                complex_logic_rules = [not_divergent_opinions, len(gossip_values) > 0, not_large_score_difference]
                if all(complex_logic_rules):
                    setattr(self, "agent_" + str(i) + "_reputation", gossip_consensus)

    def step_start(self):
        assign_neighbour_values(self)

    def step_pd(self):
        self.get_pd_opponents()
        self.set_pd_decisions()

    def step_payoffs(self):
        self.calculate_pd_payoffs()

    def step_scoring(self):
        self.set_pd_scoring()

    def step_gossip(self):
        self.set_gossip_decisions()
        self.set_gossip_dictionary()

    def step_reflect(self):
        self.set_update_decisions()
        self.set_update_dictionary()
        self.set_gossip_values()

    def step_update(self):
        self.set_gossip_scoring()

    def step_collect(self):
        self.model.datacollector.collect(self.model)


class SimpleModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, network_groups, total_networks, treatment_ref, game_type, gossip_logic="simple"):
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

        assign_network_id(model=self, network_agents=self.network_agents, treatment_ref=treatment_ref)

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
