# from random import randint
import mesa


def list_network_id(model):
    agent_network_ids = [agent.network_id for agent in model.schedule.agents]
    agents_in_network_1 = len([x for x in agent_network_ids if x == 1])
    return agents_in_network_1


def list_agent_id(model):
    agent_network_ids = [agent.agent_id for agent in model.schedule.agents]
    # agents_in_network_1 = len([x for x in agent_network_ids if x == 1])
    return agent_network_ids


def list_network_neighbours(model):
    agent_neighbours = [agent.neighbours_list for agent in model.schedule.agents]
    return agent_neighbours


class SimpleAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1
        self.agent_id = 0
        self.network_id = 0


class SimpleModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, network_agents, total_networks):
        self.num_agents = network_agents * total_networks
        self.total_networks = total_networks
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        # Create agents
        for i in range(self.num_agents):
            a = SimpleAgent(i, self)
            self.schedule.add(a)

        current_network = 1
        while current_network <= self.total_networks:
            current_agent = 1
            for a in self.schedule.agents:
                if a.unique_id < (network_agents * current_network) and a.network_id == 0:
                    a.network_id = current_network
                    a.agent_id = current_agent
                    current_agent += 1
            current_agent = 1
            current_network += 1

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Networks": list_network_id,
                "Agent_ID": list_agent_id,
                # "Neighbours": list_network_neighbours,
            },
            agent_reporters={
                "network_id": "network_id",
                "agent_id": "agent_id",
                # "neighbours": "neighbours_list",
            },
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
