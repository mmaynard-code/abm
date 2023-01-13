import numpy as np
from mapping import list_unless_none
from mapping import pd_payoff_matrix


def get_consensus_variance(model):
    agent_consensus = [abs(agent.session_consensus - agent.neighbour_consensus) for agent in model.schedule.agents]
    all_agent_consensus = round(np.nanmean(list_unless_none(agent_consensus)), 3)
    return all_agent_consensus


def get_round_cooperation(model):
    all_agent_decision = [agent.result_1 for agent in model.schedule.agents] + [
        agent.result_2 for agent in model.schedule.agents
    ]
    all_agent_cooperation = [decision for decision in all_agent_decision if decision == "Cooperation"]
    round_cooperation = round(len(all_agent_cooperation) / len(all_agent_decision), 3)
    return round_cooperation


def get_round_gossip(model):
    round_gossip = sum(
        [
            sum(
                [
                    len(agent.gossip_dictionary_1.keys()),
                    len(agent.gossip_dictionary_2.keys()),
                    len(agent.gossip_dictionary_3.keys()),
                ]
            )
            for agent in model.schedule.agents
        ]
    )
    print(round_gossip)
    print(model.num_agents)
    round_gossip = round(round_gossip / model.num_agents, 3)
    return round_gossip


def get_round_effective_gossip(model):
    round_effective_gossip = sum([len(agent.update_dictionary.keys()) for agent in model.schedule.agents])
    round_effective_gossip = round(round_effective_gossip / model.num_agents, 3)
    return round_effective_gossip


def get_session_cooperation_level(model):
    agent_total_payoff = [agent.payoff_total for agent in model.schedule.agents]
    session_maximum_total_payoff = (model.num_agents * pd_payoff_matrix.get("Cooperate").get("Cooperate") * 2) * (
        model.schedule.steps + 1
    )
    session_cooperation_level = round(sum(agent_total_payoff) / session_maximum_total_payoff, 3)
    return session_cooperation_level


def get_round_cooperation_level(model):
    agent_round_payoff = [sum([agent.payoff_1, agent.payoff_2]) for agent in model.schedule.agents]
    round_maximum_total_payoff = model.num_agents * pd_payoff_matrix.get("Cooperate").get("Cooperate") * 2
    round_cooperation_level = round(sum(agent_round_payoff) / round_maximum_total_payoff, 3)
    return round_cooperation_level


random_model_reporters = {
    "Consensus": get_consensus_variance,
    "Cooperation": get_round_cooperation,
    "Cooperation_Round": get_round_cooperation_level,
    "Cooperation_Session": get_session_cooperation_level,
    "Gossip": get_round_gossip,
    "Updates": get_round_effective_gossip,
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
