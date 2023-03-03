import numpy as np
from mapping import pd_payoff_matrix


def get_round_proportion_cooperation(model):
    """Get the proportion of Cooperative outcomes in the round for all agents"""
    all_agent_decision = [agent.result_1 for agent in model.schedule.agents] + [
        agent.result_2 for agent in model.schedule.agents
    ]
    all_agent_cooperation = [decision for decision in all_agent_decision if decision == "Cooperation"]
    round_cooperation = round(len(all_agent_cooperation) / len(all_agent_decision), 3)
    return round_cooperation


def get_round_cooperation_level(model):
    """Get the absolute level of Cooperation for the round"""
    agent_round_payoff = [sum([agent.payoff_1, agent.payoff_2]) for agent in model.schedule.agents]
    round_maximum_total_payoff = model.num_agents * pd_payoff_matrix.get("Cooperate").get("Cooperate") * 2
    round_cooperation_level = round(sum(agent_round_payoff) / round_maximum_total_payoff, 3)
    return round_cooperation_level


def get_all_agents_known(model):
    """Gets the step number when all agents knew all other agents by reputation"""
    all_agents_known = [agent.agents_known for agent in model.schedule.agents]
    proportion_known = np.min(all_agents_known) / (model.num_agents - 1)
    return proportion_known


def get_all_agents_played(model):
    """Gets the step number when all agents played all other agents"""
    all_agents_played = [agent.agents_played for agent in model.schedule.agents]
    proportion_played = np.mean(all_agents_played) / (model.num_agents - 1)
    print("step: ", model.schedule.steps, "played: ", proportion_played)
    return proportion_played


random_model_reporters = {
    "cooperation": get_round_proportion_cooperation,
    "cooperation_round": get_round_cooperation_level,
    "proportion_known": get_all_agents_known,
    "proportion_played": get_all_agents_played,
}


model_reporters_by_game_type = {
    "random": {**random_model_reporters},
    "reputation": {**random_model_reporters},
    "gossip": {**random_model_reporters},
}


baseline_reporters = {
    "network_id": "network_id",
    "agent_id": "agent_id",
    "agents_played": "agents_played",
    "agents_known": "agents_known",
    "count_0": "count_0",
    "count_1": "count_1",
    "count_2": "count_2",
    "count_3": "count_3",
    "count_4": "count_4",
    "count_5": "count_5",
    "count_6": "count_6",
    "count_7": "count_7",
    "count_8": "count_8",
    "count_9": "count_9",
    "count_10": "count_10",
    "reputation_change_count": "reputation_change_count",
    "reputation_change_count_grouped": "reputation_change_count_grouped",
}


pd_game_reporters = {
    "pd_opponent_1": "pd_opponent_1",
    "pd_opponent_2": "pd_opponent_2",
    "agent_payoff_1": "payoff_1",
    "agent_payoff_2": "payoff_2",
    "pd_opponent_1_pre_pd_reputation": "pd_opponent_1_reputation",
    "pd_opponent_2_pre_pd_reputation": "pd_opponent_2_reputation",
    "payoff_total": "payoff_total",
    "payoff_mean": "payoff_mean",
}


gossip_reporters = {
    "neighbour_1": "neighbour_1",
    "neighbour_2": "neighbour_2",
    "neighbour_3": "neighbour_3",
    "neighbour_1_reputation": "neighbour_1_reputation",
    "neighbour_2_reputation": "neighbour_2_reputation",
    "neighbour_3_reputation": "neighbour_3_reputation",
    "gossip_dictionary_1": "gossip_dictionary_1",
    "gossip_dictionary_2": "gossip_dictionary_2",
    "gossip_dictionary_3": "gossip_dictionary_3",
    "update_dictionary": "update_dictionary",
    "session_absolute_gossip": "session_absolute_gossip",
    "network_absolute_gossip": "network_absolute_gossip",
    "neighbour_absolute_gossip": "neighbour_absolute_gossip",
    "session_mean_gossip": "session_mean_gossip",
    "network_mean_gossip": "network_mean_gossip",
    "neighbour_mean_gossip": "neighbour_mean_gossip",
}


aggregate_reporters = {
    "session_consensus": "session_consensus",
    "network_consensus": "network_consensus",
    "neighbour_consensus": "neighbour_consensus",
    "session_relative_cooperation": "session_relative_cooperation",
    "network_relative_cooperation": "network_relative_cooperation",
    "neighbour_relative_cooperation": "neighbour_relative_cooperation",
    "session_absolute_cooperation": "session_absolute_cooperation",
    "network_absolute_cooperation": "network_absolute_cooperation",
    "neighbour_absolute_cooperation": "neighbour_absolute_cooperation",
    "session_mean_cooperation": "session_mean_cooperation",
    "network_mean_cooperation": "network_mean_cooperation",
    "neighbour_mean_cooperation": "neighbour_mean_cooperation",
}


def get_model_reporters_from_reporter_config(model):
    return {}


def get_agent_reporters_from_reporter_config(model):
    agent_reporters = baseline_reporters
    if "pd_game" in model.reporter_config:
        agent_reporters = {**agent_reporters, **pd_game_reporters}
    if "aggregate" in model.reporter_config:
        agent_reporters = {**agent_reporters, **aggregate_reporters}
    if "gossip" in model.reporter_config and model.game_type == "gossip":
        agent_reporters = {**agent_reporters, **gossip_reporters}
    if "agent" in model.reporter_config and model.game_type == "random":
        for i in range(0, model.num_agents):
            new_reporter = {
                "agent_" + str(i) + "_cooperated_proportion": "agent_" + str(i) + "_cooperated_proportion",
                "agent_" + str(i) + "_cooperated": "agent_" + str(i) + "_cooperated",
                "agent_" + str(i) + "_reputation": "agent_" + str(i) + "_reputation",
            }
            agent_reporters = {**agent_reporters, **new_reporter}
    if "agent" in model.reporter_config and model.game_type != "random":
        for i in range(0, model.num_agents):
            new_reporter = {
                "agent_" + str(i) + "_post_pd_reputation": "agent_" + str(i) + "_post_pd_reputation",
                "agent_" + str(i) + "_final_reputation": "agent_" + str(i) + "_final_reputation",
            }
            agent_reporters = {**agent_reporters, **new_reporter}
    return agent_reporters
