import random

import numpy as np
from mapping import get_neighbour_maps_by_treatment_ref
from mapping import list_unless_value

from pd_model.mapping import refactor_reputation_scores


def assign_network_id(model, network_agents: int, treatment_ref: str):
    """
    Assigns each agent a network_id based on the total_networks using the
    get_neighbour_maps_by_treatment_ref logical mapping
    This is only run once at the start of the model
    """
    current_index = 0
    current_network = 1
    while current_network <= model.total_networks:
        current_agent = 1
        for a in model.schedule.agents:
            if a.unique_id < (network_agents * current_network) and a.network_id is None:
                a.index_id = current_index
                a.network_id = current_network
                a.agent_id = current_agent
                agent_neighbour_list = get_neighbour_maps_by_treatment_ref(
                    agent_id=a.agent_id, network_agents=network_agents, treatment_ref=treatment_ref
                )
                a.neighbours_list = agent_neighbour_list
                current_agent += 1
                current_index += 1
        current_agent = 1
        current_network += 1


def assign_neighbour_values(agent):
    """
    Assigns each agent values initial values for their neighbours and updates the reputation for each neighbour
    from the agents reputation score for the column with the corresponding agent_id of the neighbour
    This is run once in each step of the model
    """
    current_neighbour = 1
    for i in agent.neighbours_list:
        current_neighbour_col = "neighbour_" + str(current_neighbour)
        current_neighbour_id_col = "neighbour_" + str(current_neighbour) + "_AgentID"
        current_neighbour_reputation_col = "neighbour_" + str(current_neighbour) + "_reputation"
        if agent.model.schedule.steps == 0:
            setattr(
                agent,
                current_neighbour_col,
                [x for x in agent.model.schedule.agents if (x.network_id == agent.network_id) & (x.agent_id == i)][0],
            )
            setattr(agent, current_neighbour_id_col, getattr(agent, current_neighbour_col).unique_id)
        agent_reputation_column = "agent_" + str(getattr(agent, current_neighbour_col).unique_id) + "_reputation"
        setattr(agent, current_neighbour_reputation_col, getattr(agent, agent_reputation_column))
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
    agent.pd_opponent_1 = None
    agent.pd_opponent_1_AgentID = None
    agent.pd_opponent_1_pd_decision_1 = None
    agent.pd_opponent_1_reputation = None
    agent.pd_decision_1 = None
    agent.pd_opponent_2 = None
    agent.pd_opponent_2_AgentID = None
    agent.pd_opponent_2_pd_decision_2 = None
    agent.pd_opponent_2_reputation = None
    agent.pd_decision_2 = None
    agent.payoff_1 = None
    agent.payoff_2 = None
    agent.payoff_total = 0
    agent.payoff_mean = 0
    agent.result_1 = None
    agent.result_2 = None
    agent.reputation_change_count = 0
    agent.reputation_change_count_grouped = 0


def assign_agent_reputation_attributes(agent):
    """
    Sets all required reputation attributes for each agent
    This is run once during agent creation
    """
    for i in range(0, agent.model.num_agents):
        setattr(agent, "agent_" + str(i) + "_reputation", None)
        setattr(agent, "agent_" + str(i) + "_played", 0)
        setattr(agent, "agent_" + str(i) + "_cooperated", 0)
        setattr(agent, "agent_" + str(i) + "_cooperated_proportion", None)
        setattr(agent, "agent_" + str(i) + "_post_pd_reputation", None)
        setattr(agent, "agent_" + str(i) + "_final_reputation", None)
        setattr(agent, "agent_" + str(i) + "_post_pd_reputation_grouped", None)
        setattr(agent, "agent_" + str(i) + "_final_reputation_grouped", None)
    for i in range(0, 11):
        setattr(agent, "count_" + str(i), 0)


def update_reputation_change_count(agent, previous_reputation: int, current_reputation: int, grouped: bool = False):
    """
    Updates the reputation_change_count relevant

    Parameters
    ----------
    agent : agent in the model
    previous_reputation : int
        the previous reputation to compare against
    current_reputation : int
        the current reputation post reputation
    grouped : bool, optional
        toggle to use _grouped logic
    """
    column_to_update = "reputation_change_count"
    if grouped:
        previous_reputation = refactor_reputation_scores(previous_reputation)
        current_reputation = refactor_reputation_scores(current_reputation)
        column_to_update = "reputation_change_count_grouped"
    if previous_reputation != current_reputation:
        current_update_count = getattr(agent, column_to_update)
        setattr(agent, column_to_update, current_update_count + 1)


def assign_aggregate_reporters(agent, variable: str, transformation: str, output_name: str, length: bool = False):
    """
    Assigns the aggregate reporters of the variable for session, network, and neighbour agent sets value using the specified transformation

    Parameters
    ----------
    agent : agent in the model
    variable : str
        base variable name to aggregate
    transformation : str
        type of aggregation transformation to use: must be one of var, mean, sum
    output_name : str
        output varialbe name to save aggregation as
    length : bool, optional
        indicates whether the aggregation should be the length of the variable passed through
    """
    session_agents = [a for a in agent.model.schedule.agents]
    network_agents = [a for a in session_agents if a.network_id == agent.network_id]
    neighbours = [a for a in network_agents if a.agent_id in agent.neighbours_list]
    neighbour_group_agents = [*neighbours, agent]
    all_session = []
    all_network = []
    all_neighbour = []
    for i in range(0, agent.model.num_agents):
        raw_session = []
        raw_network = []
        raw_neighbour = []
        for j in session_agents:
            if "agent" in variable:
                variable_suffix = variable.split("_")[1]
                variable_value = getattr(j, "agent_" + str(i) + f"_{variable_suffix}")
            else:
                variable_value = getattr(j, variable)
            if length:
                variable_value = len(variable_value)
            raw_session += [variable_value]
            if j in network_agents:
                raw_network += [variable_value]
            if j in neighbour_group_agents:
                raw_neighbour += [variable_value]
        if transformation == "mean":
            transformed_session = round(np.nanmean(list_unless_value(raw_session)), 3)
            transformed_network = round(np.nanmean(list_unless_value(raw_network)), 3)
            transformed_neighbour = round(np.nanmean(list_unless_value(raw_neighbour)), 3)
        elif transformation == "var":
            transformed_session = round(np.nanvar(list_unless_value(raw_session)), 3)
            transformed_network = round(np.nanvar(list_unless_value(raw_network)), 3)
            transformed_neighbour = round(np.nanvar(list_unless_value(raw_neighbour)), 3)
        elif transformation == "sum":
            transformed_session = np.nansum(list_unless_value(raw_session))
            transformed_network = np.nansum(list_unless_value(raw_network))
            transformed_neighbour = np.nansum(list_unless_value(raw_neighbour))
        all_session += [transformed_session]
        all_network += [transformed_network]
        all_neighbour += [transformed_neighbour]
    if transformation == "mean":
        transformed_all_session = round(np.nanmean(list_unless_value(all_session)), 3)
        transformed_all_network = round(np.nanmean(list_unless_value(all_network)), 3)
        transformed_all_neighbour = round(np.nanmean(list_unless_value(all_neighbour)), 3)
    elif transformation == "var":
        transformed_all_session = round(np.nanvar(list_unless_value(all_session)), 3)
        transformed_all_network = round(np.nanvar(list_unless_value(all_network)), 3)
        transformed_all_neighbour = round(np.nanvar(list_unless_value(all_neighbour)), 3)
    elif transformation == "sum":
        transformed_all_session = np.nansum(list_unless_value(all_session))
        transformed_all_network = np.nansum(list_unless_value(all_network))
        transformed_all_neighbour = np.nansum(list_unless_value(all_neighbour))
    setattr(agent, f"session_{output_name}", transformed_all_session)
    setattr(agent, f"network_{output_name}", transformed_all_network)
    setattr(agent, f"neighbour_{output_name}", transformed_all_neighbour)
