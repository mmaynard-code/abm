stage_lists_by_game_type = {
    "random": ["step_pd", "step_payoffs", "step_collect"],
    "reputation": ["step_start", "step_pd", "step_payoffs", "step_scoring", "step_collect"],
    "gossip": [
        "step_start",
        "step_pd",
        "step_payoffs",
        "step_scoring",
        "step_gossip",
        "step_reflect",
        "step_update",
        "step_collect",
    ],
}

pd_payoff_matrix = {
    "Cooperate": {
        "Cooperate": 5,
        "Defect": 0,
    },
    "Defect": {
        "Cooperate": 6,
        "Defect": 2,
    },
}

pd_result_matrix = {
    "Cooperate": {
        "Cooperate": "Cooperation",
        "Defect": "Betrayed",
    },
    "Defect": {
        "Cooperate": "Betrayer",
        "Defect": "Both Betray",
    },
}

random_group_matching = {1: [2, 4], 2: [1, 3], 3: [4, 2], 4: [3, 1]}


def get_neighbour_maps_by_treatment_ref(agent_id, network_agents, treatment_ref):
    """
    Creates a list of neighbour agent_ids based on both the treatment_ref and the number of network_agents
    in the model.
    This list is then filtered to remove invalid agent_id values and returned for
    """
    neighbour_list = [
        agent_id + 1,
        agent_id - 1,
        agent_id + (network_agents - 1),
        agent_id - (network_agents - 1),
    ]
    if treatment_ref == "B":
        if agent_id in [3, 4, 7, 8, 11, 12, 15, 16, 19, 20, 23, 24, 27, 28]:
            neighbour_list = [agent_id + 1, agent_id - 1, agent_id + 2]
        if agent_id in [5, 6, 9, 10, 13, 14, 17, 18, 21, 22, 25, 26, 29, 30]:
            neighbour_list = [agent_id + 1, agent_id - 1, agent_id - 2]
        if agent_id == 1:
            neighbour_list = [agent_id + 1, network_agents, network_agents - 1]
        if agent_id == 2:
            neighbour_list = [agent_id + 1, agent_id - 1, network_agents]
        if agent_id == network_agents:
            neighbour_list = [agent_id - 1, 1, 2]
        if agent_id == network_agents - 1:
            neighbour_list = [agent_id - 1, network_agents, 1]
    elif treatment_ref == "C":
        neighbour_list += [
            int(agent_id + (network_agents / 2)),
            int(agent_id - (network_agents / 2)),
        ]

    filtered_neighbour_list = [x for x in neighbour_list if x > 0 and x <= network_agents]
    return filtered_neighbour_list


def list_unless_none(value_list):
    if len(value_list) > 0:
        return list(filter(lambda item: item is not None, value_list))
    else:
        return list(None)


def refactor_reputation_scores(reputation_score_value):
    if reputation_score_value is None:
        reputation_score_value = 0
    elif reputation_score_value >= 7:
        reputation_score_value = 1
    elif reputation_score_value <= 4:
        reputation_score_value = -1
    else:
        reputation_score_value = 0
