stage_lists_by_game_type = {
    "random": ["play_pd_game"],
    "reputation_scoring": ["play_pd_game", "update_reputation_scores"],
    "gossip_sharing": ["play_pd_game", "update_reputation_scores", "gossip", "update_reputation_scores"],
}


def neighbour_maps_by_treatment_id(agent_id, network_agents, treatment_id):
    neighbour_list = [
        agent_id + 1,
        agent_id - 1,
        agent_id + (network_agents - 1),
        agent_id - (network_agents - 1),
    ]
    if treatment_id == 3:
        neighbour_list += []
    elif treatment_id == 4:
        neighbour_list += [
            agent_id + (network_agents / 2),
            agent_id - (network_agents / 2),
        ]

    filtered_neighbour_list = [x for x in neighbour_list if x >= agent_id and x <= network_agents]
    return filtered_neighbour_list
