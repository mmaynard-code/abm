import random

from mapping import get_neighbour_maps_by_treatment_id


def assign_network_id(model, network_agents, treatment_id):
    """
    Assigns each agent a network_id based on the total_networks using the
    get_neighbour_maps_by_treatment_id logical mapping
    This is only run once at the start of the model
    """
    current_network = 1
    while current_network <= model.total_networks:
        current_agent = 1
        for a in model.schedule.agents:
            if a.unique_id < (network_agents * current_network) and a.network_id is None:
                a.network_id = current_network
                a.agent_id = current_agent
                agent_neighbour_list = get_neighbour_maps_by_treatment_id(
                    agent_id=a.agent_id, network_agents=network_agents, treatment_id=treatment_id
                )
                a.neighbours_list = agent_neighbour_list
                current_agent += 1
        current_agent = 1
        current_network += 1


def assign_neighbour_values(agent):
    current_neighbour = 1
    for i in agent.neighbours_list:
        neighbour_column_list = [
            "neighbour_" + str(current_neighbour),
            "neighbour_" + str(current_neighbour) + "_AgentID",
            "neighbour_" + str(current_neighbour) + "_reputation",
        ]
        if agent.model.schedule.steps == 0:
            setattr(
                agent,
                neighbour_column_list[0],
                [x for x in agent.model.schedule.agents if (x.network_id == agent.network_id) & (x.agent_id == i)][0],
            )
            setattr(agent, neighbour_column_list[1], getattr(agent, neighbour_column_list[0]).unique_id)
        reputation_column = "agent_" + str(getattr(agent, neighbour_column_list[0]).unique_id) + "_reputation"
        setattr(agent, neighbour_column_list[2], getattr(agent, reputation_column))
        current_neighbour += 1


def assign_random_group_id(model):
    """
    Randomly assigns each agent a group_id
    This is run once in each step of the model
    """
    for a in model.schedule.agents:
        a.group_id = 0
    full_groups = 0
    number_of_groups = int(model.num_agents / 4)
    available_groups = list(range(1, number_of_groups + 1))
    while full_groups < number_of_groups:
        random_group = random.choice(available_groups)
        for a in model.schedule.agents:
            a.group_id = random_group
            agent_group_ids = [agent.group_id for agent in model.schedule.agents]
            agents_in_group = len([x for x in agent_group_ids if x == random_group])
            if agents_in_group == 4:
                available_groups.remove(random_group)
                full_groups += 1
            if len(available_groups) > 0:
                random_group = random.choice(available_groups)


def assign_random_player_id(model):
    """
    Randomly assigns each agent in a group a player_id
    This is run once in each step of the model
    """
    current_group = 1
    number_of_groups = int(model.num_agents / 4)
    while current_group <= number_of_groups:
        available_players = list(range(1, 5))
        for a in model.schedule.agents:
            if a.group_id == current_group:
                random_player = random.choice(available_players)
                a.player_id = random_player
                available_players.remove(random_player)
        current_group += 1


def assign_agent_base_attributes(agent):
    """
    Sets all base attributes for each agent
    This is run once during agent creation
    """
    agent.steps = 0
    agent.advances = 0
    agent.agent_id = None
    agent.network_id = None
    agent.group_id = None
    agent.player_id = None
    agent.pd_game_opponent_1 = None
    agent.pd_game_opponent_1_AgentID = None
    agent.pd_game_opponent_1_pd_game_decision_1 = None
    agent.pd_game_decision_1 = None
    agent.pd_game_opponent_2 = None
    agent.pd_game_opponent_2_AgentID = None
    agent.pd_game_opponent_2_pd_game_decision_2 = None
    agent.pd_game_decision_2 = None
    agent.payoff_1 = None
    agent.payoff_2 = None
    agent.payoff_total = 0
    agent.payoff_mean = 0
    agent.result_1 = None
    agent.result_2 = None


def assign_agent_reputation_attributes(agent):
    """
    Sets all required reputation attributes for each agent
    This is run once during agent creation
    """
    if agent.model.game_type == "random":
        pass
    else:
        for i in range(0, agent.model.num_agents):
            setattr(agent, "agent_" + str(i) + "_reputation", None)
    # elif agent.model.game_type == "reputation":
    #     for i in range(0, agent.model.num_agents):
    #         setattr(agent, "agent_" + str(i) + "_reputation", None)
    # elif agent.model.game_type == "gossip":
    #     for i in range(0, agent.model.num_agents):
    #         setattr(agent, "agent_" + str(i) + "_reputation", None)
    #         for j in agent.neighbours:
    #             setattr(agent, "agent_" + str(j) + "_gossip_" + str(i), None)
