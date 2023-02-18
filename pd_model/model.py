import random

import mesa
import numpy as np
from assign import assign_agent_base_attributes
from assign import assign_agent_reputation_attributes
from assign import assign_aggregate_reporters
from assign import assign_neighbour_values
from assign import assign_network_id
from assign import assign_random_group_id
from assign import assign_random_player_id
from decisions import gossip_decision_distribution_by_subject_score_and_target_score
from decisions import neighbour_reputation_for_gossip_update
from decisions import pd_decision_distributions_by_score
from decisions import pd_scoring_distributions_by_payoff_result
from decisions import update_decision_distribution_for_simple_gossip_grouped_neighbour_scores
from mapping import list_unless_value
from mapping import pd_payoff_matrix
from mapping import pd_result_matrix
from mapping import random_group_matching
from mapping import refactor_reputation_scores
from mapping import stage_lists_by_game_type
from reporters import get_agent_reporters_from_reporter_config
from reporters import get_model_reporters_from_reporter_config


class SimpleAgent(mesa.Agent):
    """
    An agent playing a Prisoner's Dilemma game with reputation, memory, and gossip dependent on model parameters
    """

    def __init__(self, unique_id, model):
        """
        Sets the base attributes for the agent
        """
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
            pd_opponent_1_reputation = getattr(self, "agent_" + str(self.pd_opponent_1.unique_id) + "_reputation")
            pd_opponent_2_reputation = getattr(self, "agent_" + str(self.pd_opponent_2.unique_id) + "_reputation")
            self.pd_decision_1 = random.choice(pd_decision_distributions_by_score[pd_opponent_1_reputation])
            self.pd_decision_2 = random.choice(pd_decision_distributions_by_score[pd_opponent_2_reputation])
            if "pd_game" in self.model.reporter_config:
                setattr(self, "pd_opponent_1_reputation", pd_opponent_1_reputation)
                setattr(self, "pd_opponent_2_reputation", pd_opponent_2_reputation)

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
        setattr(self, "agent_" + str(self.pd_opponent_2_AgentID) + "_played", current_rounds_played)
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
        pd_opponent_1_reputation = "agent_" + str(self.pd_opponent_1.unique_id) + "_reputation"
        pd_opponent_2_reputation = "agent_" + str(self.pd_opponent_2.unique_id) + "_reputation"
        if self.model.game_type == "random":
            opponent_1_score = int(random.choice(range(0, 11)))
            opponent_2_score = int(random.choice(range(0, 11)))
        else:
            opponent_1_score = int(random.choice(pd_scoring_distributions_by_payoff_result.get(self.payoff_1, None)))
            opponent_2_score = int(random.choice(pd_scoring_distributions_by_payoff_result.get(self.payoff_2, None)))
        setattr(self, pd_opponent_1_reputation, opponent_1_score)
        setattr(self, pd_opponent_2_reputation, opponent_2_score)
        if self.pd_opponent_1 in self.neighbours_list:
            current_neighbour = 1
            for i in self.neighbours_list:
                if self.pd_opponent_1 == i:
                    setattr(self, "neighbour_" + str(current_neighbour) + "_reputation", opponent_1_score)
                current_neighbour += 1
        if self.pd_opponent_2 in self.neighbours_list:
            current_neighbour = 1
            for i in self.neighbours_list:
                if self.pd_opponent_2 == i:
                    setattr(self, "neighbour_" + str(current_neighbour) + "_reputation", opponent_2_score)
                current_neighbour += 1
        current_count = getattr(self, f"count_{opponent_1_score}")
        setattr(self, f"count_{opponent_1_score}", current_count + 1)
        current_count = getattr(self, f"count_{opponent_2_score}")
        setattr(self, f"count_{opponent_2_score}", current_count + 1)

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
                if current_reputation is None or j == self.index_id:
                    continue
                else:
                    current_choice = random.choice(
                        gossip_decision_distribution_by_subject_score_and_target_score.get(neighbour_reputation).get(
                            current_reputation
                        )
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
            if i == self.index_id:
                continue
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

    def get_aggregate_reporters(self):
        """
        Wrapper function for aggregate reporters for later analytics
        """
        assign_aggregate_reporters(self, "agent_reputation", "var", "consensus")
        assign_aggregate_reporters(self, "agent_cooperated_proportion", "mean", "relative_cooperation")
        assign_aggregate_reporters(self, "agent_cooperated", "mean", "mean_cooperation")
        assign_aggregate_reporters(self, "agent_cooperated", "sum", "absolute_cooperation")
        assign_aggregate_reporters(self, "update_dictionary", "mean", "mean_gossip", length=True)
        assign_aggregate_reporters(self, "update_dictionary", "sum", "absolute_gossip", length=True)

    def get_players_known_played(self):
        """
        Gets the number of other agents that the agent has played a game with, or have received a reputation for
        """
        all_agents_known = []
        all_agents_played = []
        for i in range(0, self.model.num_agents):
            current_agent_played = getattr(self, "agent_" + str(i) + "_played")
            current_agent_known = getattr(self, "agent_" + str(i) + "_reputation")
            all_agents_played += [current_agent_played]
            all_agents_known += [current_agent_known]
        agents_played = len(list_unless_value(all_agents_played, 0))
        agents_known = len(list_unless_value(all_agents_known))
        setattr(self, "agents_played", agents_played)
        setattr(self, "agents_known", agents_known)

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

    def step_end(self):
        self.get_aggregate_reporters()
        self.get_players_known_played()

    def step_collect(self):
        self.model.datacollector.collect(self.model)


class SimpleModel(mesa.Model):
    """
    A Prisoner's Dilemma model with a number of agents in a number of networks, treatments, and game types.

    The config parameters enable reporters to be configured to streamline analysis to desired variables
    """

    def __init__(self, network_groups, total_networks, treatment_ref, game_type, consensus_type, reporter_config):
        """_summary_

        Parameters
        ----------
        network_groups : _type_
            _description_
        total_networks : _type_
            _description_
        treatment_ref : _type_
            _description_
        game_type : _type_
            _description_
        consensus_type : _type_
            _description_
        reporter_config : _type_
            _description_
        """
        self.num_agents = network_groups * 4 * total_networks
        self.network_agents = network_groups * 4
        self.total_networks = total_networks
        self.game_type = game_type
        self.consensus_type = consensus_type
        self.reporter_config = reporter_config
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
            model_reporters=get_model_reporters_from_reporter_config(self),
            agent_reporters=get_agent_reporters_from_reporter_config(self),
        )

    def step(self):
        self.schedule.step()
        assign_random_group_id(self)
        assign_random_player_id(self)
