import numpy as np
from mapping import list_unless_none


def get_consensus_variance(model):
    agent_session_consensus = [agent.session_consensus for agent in model.schedule.agents]
    agents_in_network_1 = round(np.nanmean(list_unless_none(agent_session_consensus)), 3)
    return agents_in_network_1


random_model_reporters = {
    "Consensus": get_consensus_variance,
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
    "opponent_1_AgentID": "pd_opponent_1_AgentID",
    "opponent_2_AgentID": "pd_opponent_2_AgentID",
    "decision_1": "pd_decision_1",
    "decision_2": "pd_decision_2",
    "payoff_1": "payoff_1",
    "payoff_2": "payoff_2",
    "payoff_total": "payoff_total",
    "payoff_mean": "payoff_mean",
    "result_1": "result_1",
    "result_2": "result_2",
}


def get_agent_reporters_by_game_type(model):
    agent_reporters = random_agent_reporters
    if model.game_type != "random":
        for i in range(0, model.num_agents):
            new_reporter = {
                "agent_" + str(i) + "_reputation": "agent_" + str(i) + "_reputation",
                "agent_" + str(i) + "_post_pd_reputation": "agent_" + str(i) + "_post_pd_reputation",
                "agent_" + str(i) + "_final_reputation": "agent_" + str(i) + "_final_reputation",
            }
            agent_reporters = {**agent_reporters, **new_reporter}
    if model.game_type == "gossip":
        for i in range(0, model.num_agents):
            new_reporter = {
                "agent_" + str(i) + "_neighbour_consensus": "agent_" + str(i) + "_neighbour_consensus",
                "agent_" + str(i) + "_network_consensus": "agent_" + str(i) + "_network_consensus",
                "agent_" + str(i) + "_session_consensus": "agent_" + str(i) + "_session_consensus",
            }
            agent_reporters = {**agent_reporters, **new_reporter}
        for i in range(1, len(model.schedule.agents[0].neighbours_list) + 1):
            new_reporter = {
                "gossip_dictionary_" + str(i): "gossip_dictionary_" + str(i),
            }
            agent_reporters = {**agent_reporters, **new_reporter}
        new_reporters = {
            "update_dictionary": "update_dictionary",
            "session_consensus": "session_consensus",
            "network_consensus": "network_consensus",
            "neighbour_consensus": "neighbour_consensus",
        }
        agent_reporters = {**agent_reporters, **new_reporters}
    return agent_reporters
