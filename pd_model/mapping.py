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

scoring_distributions_by_payoff_result = {
    6: [10, 9, 8, 7, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    5: [10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 5, 5, 4, 3, 2, 1, 0],
    2: [10, 9, 8, 7, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    0: [10, 9, 8, 7, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
}

pd_decision_distributions_by_score = {
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

simple_gossip_decision_neighbour_distributions_by_score = {
    10: ["All", "All", "All", "All", "All", "High", "High", "Low", "Low", "None"],
    9: ["All", "All", "All", "High", "High", "High", "Low", "Low", "Low", "None"],
    8: ["All", "All", "All", "High", "High", "High", "Low", "Low", "Low", "None"],
    7: ["All", "All", "High", "High", "High", "Low", "Low", "Low", "None", "None"],
    6: ["All", "All", "High", "High", "Low", "Low", "Low", "None", "None", "None"],
    5: ["All", "High", "High", "Low", "Low", "Low", "None", "None", "None", "None"],
    4: ["All", "High", "High", "Low", "Low", "None", "None", "None", "None", "None"],
    3: ["All", "High", "Low", "Low", "None", "None", "None", "None", "None", "None"],
    2: ["All", "High", "Low", "Low", "None", "None", "None", "None", "None", "None"],
    1: ["All", "High", "Low", "Low", "None", "None", "None", "None", "None", "None"],
    0: ["All", "High", "Low", "None", "None", "None", "None", "None", "None", "None"],
    None: ["All", "High", "Low", "None"],
}

complex_gossip_decision_neighbour_distributions_by_score = {
    10: [True, True, True, True, True, True, True, True, True, False],  # 90%
    9: [True, True, True, True, True, True, True, True, True, False],  # 90%
    8: [True, True, True, True, True, True, True, True, False, False],  # 80%
    7: [True, True, True, True, True, True, True, False, False, False],  # 70%
    6: [True, True, True, True, True, True, False, False, False, False],  # 60%
    5: [True, True, True, True, True, False, False, False, False, False],  # 50%
    4: [True, True, True, True, False, False, False, False, False, False],  # 40%
    3: [True, True, True, False, False, False, False, False, False, False],  # 30%
    2: [True, True, False, False, False, False, False, False, False, False],  # 20%
    1: [True, False, False, False, False, False, False, False, False, False],  # 10%
    0: [True, False, False, False, False, False, False, False, False, False],  # 10%
    None: [True, True, True, False],  # 75%
}

complex_gossip_decision_subject_distributions_by_score = {
    10: [True, True, True, True, True, True, True, True, False, False],  # 80%
    9: [True, True, True, True, True, True, False, False, False, False],  # 60%
    8: [True, True, True, True, True, False, False, False, False, False],  # 50%
    7: [True, True, True, True, False, False, False, False, False, False],  # 40%
    6: [True, True, True, False, False, False, False, False, False, False],  # 30%
    5: [True, True, False, False, False, False, False, False, False, False],  # 20%
    4: [True, True, True, False, False, False, False, False, False, False],  # 30%
    3: [True, True, True, True, False, False, False, False, False, False],  # 40%
    2: [True, True, True, True, True, False, False, False, False, False],  # 50%
    1: [True, True, True, True, True, True, False, False, False, False],  # 60%
    0: [True, True, True, True, True, True, True, True, False, False],  # 80%
    None: [False, False, False, False],  # 0%
}

update_decision_distributions_by_score = {
    10: [True, True, True, True, True, True, True, True, True, False],  # 90%
    9: [True, True, True, True, True, True, True, True, True, False],  # 90%
    8: [True, True, True, True, True, True, True, True, False, False],  # 80%
    7: [True, True, True, True, True, True, True, False, False, False],  # 70%
    6: [True, True, True, True, True, True, False, False, False, False],  # 60%
    5: [True, True, True, True, True, False, False, False, False, False],  # 50%
    4: [True, True, True, True, False, False, False, False, False, False],  # 40%
    3: [True, True, True, False, False, False, False, False, False, False],  # 30%
    2: [True, True, False, False, False, False, False, False, False, False],  # 20%
    1: [True, False, False, False, False, False, False, False, False, False],  # 10%
    0: [True, False, False, False, False, False, False, False, False, False],  # 10%
    None: [True, True, True, True, False, False, False, False, False, False],  # 40%
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
