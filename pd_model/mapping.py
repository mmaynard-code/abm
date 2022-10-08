stage_lists_by_game_type = {
    "random": ["step_start", "step_pd", "step_payoffs", "step_collect"],
    "reputation": ["step_start", "step_pd", "step_payoffs", "step_scoring", "step_collect"],
    "gossip": ["step_start", "step_pd", "step_payoffs", "step_scoring", "step_gossip", "step_update", "step_collect"],
}

scoring_distributions_by_payoff_result = {
    6: [10, 9, 8, 7, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    5: [10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 5, 5, 4, 3, 2, 1, 0],
    2: [10, 9, 8, 7, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    0: [10, 9, 8, 7, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
}

decision_distributions_by_score = {
    10: [
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Defect",
        "Defect",
    ],
    9: [
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Defect",
        "Defect",
    ],
    8: [
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Defect",
        "Defect",
        "Defect",
        "Defect",
    ],
    7: [
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Defect",
        "Defect",
        "Defect",
        "Defect",
        "Defect",
    ],
    6: [
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Cooperate",
        "Defect",
        "Defect",
        "Defect",
        "Defect",
        "Defect",
    ],
    5: ["Cooperate", "Cooperate", "Cooperate", "Cooperate", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect"],
    4: ["Cooperate", "Cooperate", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect"],
    3: ["Cooperate", "Cooperate", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect"],
    2: ["Cooperate", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect"],
    1: ["Cooperate", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect"],
    0: ["Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect", "Defect"],
    None: ["Cooperate", "Defect"],
}

payoff_matrix = {
    "Cooperate": {
        "Cooperate": 5,
        "Defect": 0,
    },
    "Defect": {
        "Cooperate": 6,
        "Defect": 2,
    },
}

random_group_matching = {1: [2, 4], 2: [1, 3], 3: [4, 2], 4: [3, 1]}


def get_neighbour_maps_by_treatment_id(agent_id, network_agents, treatment_id):
    neighbour_list = [
        agent_id + 1,
        agent_id - 1,
        agent_id + (network_agents - 1),
        agent_id - (network_agents - 1),
    ]
    if treatment_id == 3:
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
    elif treatment_id == 4:
        neighbour_list += [
            int(agent_id + (network_agents / 2)),
            int(agent_id - (network_agents / 2)),
        ]

    filtered_neighbour_list = [x for x in neighbour_list if x > 0 and x <= network_agents]
    return filtered_neighbour_list
