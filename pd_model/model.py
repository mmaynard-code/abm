import random

import mesa
from assign import assign_agent_base_attributes
from assign import assign_agent_reputation_attributes
from assign import assign_network_id
from assign import assign_random_group_id
from assign import assign_random_player_id
from mapping import decision_distributions_by_score
from mapping import payoff_matrix
from mapping import random_group_matching
from mapping import scoring_distributions_by_payoff_result
from mapping import stage_lists_by_game_type
from reporters import get_agent_reporters_by_game_type
from reporters import model_reporters_by_game_type


class SimpleAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        assign_agent_base_attributes(self)
        assign_agent_reputation_attributes(self)

    def pd_game(self):
        self.get_pd_opponents()
        self.get_pd_choices()
        self.get_pd_payoffs()

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
        if self.model.schedule.steps > 0:
            if self.model.game_type == "random":
                self.decision_1 = random.choice(["Defect", "Cooperate"])
                self.decision_2 = random.choice(["Defect", "Cooperate"])
            elif self.model.game_type == "reputation":
                opponent_1_reputation = getattr(self, "agent_" + str(self.pd_game_opponent_1.unique_id) + "_reputation")
                opponent_2_reputation = getattr(self, "agent_" + str(self.pd_game_opponent_2.unique_id) + "_reputation")
                self.decision_1 = random.choice(decision_distributions_by_score.get(opponent_1_reputation, None))
                self.decision_2 = random.choice(decision_distributions_by_score.get(opponent_2_reputation, None))
            elif self.model.game_type == "gossip" and self.payoff_1 is not None:
                self.decision_1 = random.choice(["Defect", "Cooperate"])
                self.decision_2 = random.choice(["Defect", "Cooperate"])
        else:
            self.decision_1 = None
            self.decision_2 = None

    def get_pd_payoffs(self):
        if self.model.schedule.steps > 0:
            self.payoff_1 = int(payoff_matrix[self.decision_1][self.pd_game_opponent_1.decision_1])
            self.payoff_2 = int(payoff_matrix[self.decision_2][self.pd_game_opponent_2.decision_2])
            self.payoff += self.payoff_1 + self.payoff_2

    def set_pd_scoring(self):
        # if self.model.schedule.steps > 0:

        opponent_1_reputation = "agent_" + str(self.pd_game_opponent_1.unique_id) + "_reputation"
        opponent_2_reputation = "agent_" + str(self.pd_game_opponent_2.unique_id) + "_reputation"
        if self.payoff_1 is not None:
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

    def step_start(self):
        assign_random_group_id(self.model)
        assign_random_player_id(self.model)

    def step_pd(self):
        self.get_pd_opponents()
        self.set_pd_choices()

    def step_scoring(self):
        self.set_pd_scoring()

    def step_end(self):
        self.get_pd_payoffs()

    def step(self):
        self.get_pd_opponents()
        self.set_pd_choices()
        if self.model.game_type in ["reputation", "gossip"]:
            self.set_pd_scoring()
        self.get_pd_payoffs()


class SimpleModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, network_agents, total_networks, treatment_id, game_type):
        self.num_agents = network_agents * total_networks
        self.total_networks = total_networks
        self.game_type = game_type
        self.schedule = mesa.time.StagedActivation(self, stage_list=stage_lists_by_game_type[game_type])
        self.running = True
        # Create agents

        for i in range(self.num_agents):
            a = SimpleAgent(i, self)
            self.schedule.add(a)

        assign_network_id(model=self, network_agents=network_agents, treatment_id=treatment_id)

        self.datacollector = mesa.DataCollector(
            model_reporters=model_reporters_by_game_type[game_type],
            agent_reporters=get_agent_reporters_by_game_type(self),
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
