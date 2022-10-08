def list_network_id(model):
    agent_network_ids = [agent.network_id for agent in model.schedule.agents]
    agents_in_network_1 = len([x for x in agent_network_ids if x == 1])
    return agents_in_network_1


def list_agent_id(model):
    agent_network_ids = [agent.agent_id for agent in model.schedule.agents]
    # agents_in_network_1 = len([x for x in agent_network_ids if x == 1])
    return agent_network_ids


def list_network_neighbours(model):
    agent_neighbours = [agent.neighbours for agent in model.schedule.agents]
    return agent_neighbours


random_model_reporters = {
    "Networks": list_network_id,
    #   "Agent_ID": list_agent_id,
    #   "Neighbours": list_network_neighbours,
}


model_reporters_by_game_type = {
    "random": random_model_reporters,
    "reputation": random_model_reporters,
    "gossip": random_model_reporters,
}


random_agent_reporters = {
    "network_id": "network_id",
    "agent_id": "agent_id",
    "neighbours": "neighbours_list",
    "group_id": "group_id",
    "player_id": "player_id",
    "pd_game_opponent_1_AgentID": "pd_game_opponent_1_AgentID",
    "pd_game_opponent_2_AgentID": "pd_game_opponent_2_AgentID",
    "payoff_1": "payoff_1",
    "payoff_2": "payoff_2",
    "payoff": "payoff",
}


def get_agent_reporters_by_game_type(model):
    agent_reporters = random_agent_reporters
    if model.game_type != "random":
        for i in range(0, model.num_agents):
            new_reporter = {"agent_" + str(i) + "_reputation": "agent_" + str(i) + "_reputation"}
            agent_reporters = {**agent_reporters, **new_reporter}
    return agent_reporters
