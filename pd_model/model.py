import random

import mesa
import numpy as np
from assign import assign_agent_base_attributes
from assign import assign_agent_reputation_attributes
from assign import assign_neighbour_values
from assign import assign_network_id
from assign import assign_random_group_id
from assign import assign_random_player_id
from decisions import gossip_value_distribution_by_neighbour_score
from decisions import neighbour_reputation_for_gossip_update
from decisions import pd_decision_distributions_by_score
from decisions import pd_scoring_distributions_by_payoff_result
from decisions import update_decision_distribution_for_simple_gossip_grouped_neighbour_scores
from mapping import list_unless_none
from mapping import pd_payoff_matrix
from mapping import pd_result_matrix
from mapping import random_group_matching
from mapping import refactor_reputation_scores
from mapping import stage_lists_by_game_type
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
        self.result_2 = pd_result_matrix[self.pd_decision_2][self.pd_opponent_2.pd_decision_2]
        self.payoff_1 = pd_payoff_matrix[self.pd_decision_1][self.pd_opponent_1.pd_decision_1]
        self.payoff_2 = pd_payoff_matrix[self.pd_decision_2][self.pd_opponent_2.pd_decision_2]
        self.payoff_total += self.payoff_1 + self.payoff_2
        if self.model.schedule.steps > 0:
            self.payoff_mean = (self.payoff_total / 2) / self.model.schedule.steps
        else:
            self.payoff_mean = self.payoff_total / 2

    def set_cooperation_values(self):

        current_rounds_played = getattr(self, "agent_" + str(self.pd_opponent_1_AgentID) + "_played") + 1
        setattr(self, "agent_" + str(self.pd_opponent_1_AgentID) + "_played", current_rounds_played)
        current_cooperation_count = getattr(self, "agent_" + str(self.pd_opponent_1_AgentID) + "_cooperated")

        if self.result_1 == pd_result_matrix["Cooperate"]["Cooperate"]:
            current_cooperation_count += 1
            setattr(self, "agent_" + str(self.pd_opponent_1_AgentID) + "_cooperated", current_cooperation_count)

        current_cooperation_proportion = current_cooperation_count / current_rounds_played
        setattr(
            self, "agent_" + str(self.pd_opponent_1_AgentID) + "_cooperated_proportion", current_cooperation_proportion
        )

        current_rounds_played = getattr(self, "agent_" + str(self.pd_opponent_2_AgentID) + "_played") + 1
        setattr(self, "agent_" + str(self.pd_opponent_2_AgentID) + "_played", current_rounds_played + 1)
        current_cooperation_count = getattr(self, "agent_" + str(self.pd_opponent_2_AgentID) + "_cooperated")

        if self.result_2 == pd_result_matrix["Cooperate"]["Cooperate"]:
            current_cooperation_count += 1
            setattr(self, "agent_" + str(self.pd_opponent_2_AgentID) + "_cooperated", current_cooperation_count)

        current_cooperation_proportion = current_cooperation_count / current_rounds_played
        setattr(
            self, "agent_" + str(self.pd_opponent_1_AgentID) + "_cooperated_proportion", current_cooperation_proportion
        )

    def set_pd_scoring(self):
        """
        Sets reputation scores for opponents through the selection of a random value from a probability matrix
        """
        opponent_1_reputation = "agent_" + str(self.pd_opponent_1.unique_id) + "_reputation"
        opponent_2_reputation = "agent_" + str(self.pd_opponent_2.unique_id) + "_reputation"
        setattr(
            self,
            opponent_1_reputation,
            int(random.choice(pd_scoring_distributions_by_payoff_result.get(self.payoff_1, None))),
        )
        setattr(
            self,
            opponent_2_reputation,
            int(random.choice(pd_scoring_distributions_by_payoff_result.get(self.payoff_2, None))),
        )

    def set_gossip_dictionary(self):
        """
        Sets the gossip_dictionary variable for each neighbour

        The gossip_dictionary contains the reputation scores that the agent is choosing to share with
        each neighbour.
        """
        if len(self.neighbours_list) == 2:
            setattr(self, "gossip_dictionary_3", {})
        for i in range(1, len(self.neighbours_list) + 1):
            gossip_dictionary = {}
            neighbour_reputation = getattr(self, "neighbour_" + str(i) + "_reputation")
            for j in range(0, self.model.num_agents):
                current_reputation = getattr(self, "agent_" + str(j) + "_reputation")
                if current_reputation is None:
                    continue
                else:
                    current_choice = random.choice(
                        gossip_value_distribution_by_neighbour_score.get(neighbour_reputation).get(current_reputation)
                    )
                    if current_choice:
                        new_dictionary = {j: current_reputation}
                        gossip_dictionary = {**gossip_dictionary, **new_dictionary}
            setattr(self, "gossip_dictionary_" + str(i), gossip_dictionary)

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
                        new_update_dictionary = {self.neighbours_list[i - 1]: current_gossip_dictionary}

                    update_dictionary = {**update_dictionary, **new_update_dictionary}
        self.update_dictionary = update_dictionary

    def set_agent_values_from_gossip(self):
        """
        Sets the gossip_values for each agents' reputation score based on the update_dictionary
        """
        for i in range(0, self.model.num_agents):
            neighbour_reputations = []
            neighbour_reputations_grouped = []
            available_gossip_values = []
            available_gossip_values_grouped = []
            agent_reputation = getattr(self, "agent_" + str(i) + "_reputation")
            agent_reputation_grouped = refactor_reputation_scores(agent_reputation)
            for j in range(1, len(self.neighbours_list) + 1):
                current_gossip_value = self.update_dictionary.get(j, {}).get(i, None)
                if current_gossip_value is not None:
                    current_neighbour_reputation = getattr(self, "neighbour_" + str(j) + "_reputation")
                    current_neighbour_reputation_grouped = refactor_reputation_scores(current_neighbour_reputation)
                    current_gossip_value_grouped = refactor_reputation_scores(current_gossip_value)
                    neighbour_reputations += [current_neighbour_reputation]
                    neighbour_reputations_grouped += [current_neighbour_reputation_grouped]
                    available_gossip_values += [current_gossip_value]
                    available_gossip_values_grouped += [current_gossip_value_grouped]
            gossip_consensus = np.nanvar(available_gossip_values_grouped)
            if any([np.isnan(gossip_consensus), gossip_consensus is None]):
                continue
            elif gossip_consensus == 0:
                chosen_gossip_value = max(available_gossip_values)
                current_update_decision = random.choice(
                    update_decision_distribution_for_simple_gossip_grouped_neighbour_scores.get(
                        neighbour_reputations_grouped[0]
                    )
                    .get(agent_reputation_grouped)
                    .get(available_gossip_values_grouped[0])
                )
            else:
                neighbour_reputation_for_gossip_update_filtered = [
                    i for i in neighbour_reputation_for_gossip_update if i in neighbour_reputations_grouped
                ]
                neighbour_reputation_weighted_gossip_selection = random.choice(
                    neighbour_reputation_for_gossip_update_filtered
                )
                available_gossip_selection = []
                available_gossip_selection_grouped = []
                for j in range(0, len(neighbour_reputations_grouped)):
                    if neighbour_reputations_grouped[j] == neighbour_reputation_weighted_gossip_selection:
                        available_gossip_selection += [available_gossip_values[j]]
                        available_gossip_selection_grouped += [available_gossip_values_grouped[j]]
                if len(available_gossip_selection) == 1:
                    chosen_gossip_value = available_gossip_selection[0]
                    current_update_decision = random.choice(
                        update_decision_distribution_for_simple_gossip_grouped_neighbour_scores.get(
                            neighbour_reputation_weighted_gossip_selection
                        )
                        .get(agent_reputation_grouped)
                        .get(available_gossip_selection_grouped[0])
                    )
                else:
                    random_selection = random.choice(range(0, len(available_gossip_selection)))
                    chosen_gossip_value = available_gossip_selection[random_selection]
                    random_gossip_selection_grouped = available_gossip_selection_grouped[random_selection]
                    current_update_decision = random.choice(
                        update_decision_distribution_for_simple_gossip_grouped_neighbour_scores.get(
                            neighbour_reputation_weighted_gossip_selection
                        )
                        .get(agent_reputation_grouped)
                        .get(random_gossip_selection_grouped)
                    )
            if current_update_decision:
                setattr(self, "agent_" + str(i) + "_post_pd_reputation", agent_reputation)
                setattr(self, "agent_" + str(i) + "_final_reputation", chosen_gossip_value)
                setattr(self, "agent_" + str(i) + "_reputation", chosen_gossip_value)
            else:
                setattr(self, "agent_" + str(i) + "_post_pd_reputation", agent_reputation)
                setattr(self, "agent_" + str(i) + "_final_reputation", agent_reputation)

    def get_gossip_consensus(self):
        session_agents = [agent for agent in self.model.schedule.agents]
        network_agents = [agent for agent in session_agents if agent.network_id == self.network_id]
        neighbour_agents = [agent for agent in network_agents if agent.agent_id in self.neighbours_list]
        all_session_consensus = []
        all_network_consensus = []
        all_neighbour_consensus = []
        all_session_cooperation = []
        all_network_cooperation = []
        all_neighbour_cooperation = []
        for i in range(0, self.model.num_agents):
            session_reputation = []
            network_reputation = []
            neighbour_reputation = []
            session_cooperation = []
            network_cooperation = []
            neighbour_cooperation = []
            for j in session_agents:
                current_agent_consensus = getattr(j, "agent_" + str(i) + "_reputation")
                current_agent_cooperation = getattr(j, "agent_" + str(i) + "_cooperated_proportion")
                if self.model.consensus_type == "grouped":
                    current_agent_consensus = refactor_reputation_scores(current_agent_consensus)
                session_reputation += [current_agent_consensus]
                session_cooperation += [current_agent_cooperation]
                if j in network_agents:
                    network_reputation += [current_agent_consensus]
                    network_cooperation += [current_agent_cooperation]
                if j in neighbour_agents:
                    neighbour_reputation += [current_agent_consensus]
                    neighbour_cooperation += [current_agent_cooperation]
            agent_session_consensus = round(np.nanvar(list_unless_none(session_reputation)), 3)
            agent_network_consensus = round(np.nanvar(list_unless_none(network_reputation)), 3)
            agent_neighbour_consensus = round(np.nanvar(list_unless_none(neighbour_reputation)), 3)
            agent_session_cooperation = round(np.mean(session_cooperation), 3)
            agent_network_cooperation = round(np.mean(network_cooperation), 3)
            agent_neighbour_cooperation = round(np.mean(neighbour_cooperation), 3)
            all_session_consensus += [agent_session_consensus]
            all_network_consensus += [agent_network_consensus]
            all_neighbour_consensus += [agent_neighbour_consensus]
            all_session_cooperation += [agent_session_cooperation]
            all_network_cooperation += [agent_network_cooperation]
            all_neighbour_cooperation += [agent_neighbour_cooperation]
            setattr(self, "agent_" + str(i) + "_session_consensus", agent_session_consensus)
            setattr(self, "agent_" + str(i) + "_network_consensus", agent_network_consensus)
            setattr(self, "agent_" + str(i) + "_neighbour_consensus", agent_neighbour_consensus)
        session_consensus = round(np.nanmean(list_unless_none(all_session_consensus)), 3)
        network_consensus = round(np.nanmean(list_unless_none(all_network_consensus)), 3)
        neighbour_consensus = round(np.nanmean(list_unless_none(all_neighbour_consensus)), 3)
        session_cooperation = round(np.mean(all_session_cooperation), 3)
        network_cooperation = round(np.mean(all_network_cooperation), 3)
        neighbour_cooperation = round(np.mean(all_neighbour_cooperation), 3)
        setattr(self, "session_cooperation", session_cooperation)
        setattr(self, "network_cooperation", network_cooperation)
        setattr(self, "neighbour_cooperation", neighbour_cooperation)
        setattr(self, "session_consensus", session_consensus)
        setattr(self, "network_consensus", network_consensus)
        setattr(self, "neighbour_consensus", neighbour_consensus)

    def step_start(self):
        assign_neighbour_values(self)

    def step_pd(self):
        self.get_pd_opponents()
        self.set_pd_decisions()

    def step_payoffs(self):
        self.calculate_pd_payoffs()

    def step_scoring(self):
        self.set_pd_scoring()
        self.set_cooperation_values()

    def step_gossip(self):
        self.set_gossip_dictionary()

    def step_reflect(self):
        self.set_update_dictionary()

    def step_update(self):
        self.set_agent_values_from_gossip()

    def step_consensus(self):
        self.get_gossip_consensus()

    def step_collect(self):
        self.model.datacollector.collect(self.model)


class SimpleModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, network_groups, total_networks, treatment_ref, game_type, consensus_type):
        self.num_agents = network_groups * 4 * total_networks
        self.network_agents = network_groups * 4
        self.total_networks = total_networks
        self.game_type = game_type
        self.consensus_type = consensus_type
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
