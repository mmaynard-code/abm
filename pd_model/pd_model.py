import mesa

# from mapping import neighbour_maps_by_treatment_id
# from mapping import stage_lists_by_game_type


class pd_agent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.set_base_attributes()

    def set_base_agent_attributes(self):
        self.network_id = 0
        self.neighbours_list = []
        self.payoff = 0
        self.mean_payoff = 0
        self.cumulative_payoff = 0

    def update_agent_attributes(self):
        self.mean_payoff = 0

    def play_pd_game(self):
        self.update_attributes()

    def step(self):
        self.play_pd_game()


class pd_model(mesa.Model):
    def __init__(self, network_agents, total_networks, treatment_id, game_type):
        self.num_agents = network_agents * total_networks
        self.total_networks = total_networks
        self.treatment_id = (treatment_id,)
        self.game_type = game_type
        # self.schedule = mesa.time.StagedActivation(
        #     self,
        #     stage_list = stage_lists_by_game_type.get(game_type, ["play_pd_game"])
        # )
        self.schedule = mesa.time.RandomActivation(self)

        for i in range(self.num_agents):
            a = pd_agent(i, self)
            self.schedule.add(a)
            # current_network = 1
            # if a.unique_id < (self.num_agents / self.total_networks) * current_network:
            #     a.network_id = current_network

        current_network = 1
        while current_network <= self.total_networks:
            for a in self.schedule.agents:
                if a.unique_id < (self.num_agents / self.total_networks) * current_network and a.network_id != 0:
                    a.network_id = current_network
            current_network += 1

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
