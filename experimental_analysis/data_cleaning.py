import os

import numpy as np
import pandas as pd


def get_experimental_csv_files_from_directory(directory, file_extension):
    file_list = []
    for root, dir, files in os.walk(directory):
        for file in files:
            file_matching_logic = [os.path.splitext(file)[1] == file_extension, file[0:4] == "all_"]
            if all(file_matching_logic):
                file_list += [os.path.join(root, file)]
    return file_list


def read_experimental_data_from_csv(file_path):
    df = pd.read_csv(file_path).rename(str.lower, axis="columns")
    column_names_to_remap = {
        "participant.id_in_session": "id",
        "participant.code": "unique_id",
        "session.code": "session_id",
    }
    column_filter_list = [
        "participant",
        "game",
        "session",
        "gdpr",
        "p1_survey",
        "end_survey",
        "payment_info",
    ]
    column_filters = []
    for i in column_filter_list:
        column_filters += [col for col in df if col.startswith(i)]
    df = df[column_filters].rename(columns=column_names_to_remap)
    df.columns = df.columns.str.replace(".", "_", regex=True)
    df = df.drop(drop_column_list, axis=1)
    return df


def get_new_experimental_data_from_df(existing_df, new_df):
    new_experimental_data = new_df[~new_df["session_id"].isin(existing_df["session_id"])]
    return new_experimental_data


def merge_all_experimental_data_from_file_list(file_list):
    counter = 0
    for i in file_list:
        if counter == 0:
            df = read_experimental_data_from_csv(i)
        else:
            new_df = read_experimental_data_from_csv(i)
            filtered_new_df = get_new_experimental_data_from_df(df, new_df)
            if len(filtered_new_df.session_id.unique()) > 0:
                result = pd.concat([df, filtered_new_df])
                df = result
        counter += 1
    return df


def get_session_player_lookup_df(df):
    player_lookup_df = pd.DataFrame(columns=["label", "id"])
    for j in range(1, 3):
        query_df = df.query(f"id == {j}")
        query_value = list(query_df["game_1_player_other_players"])[0].split(",")
        new_players_df = pd.DataFrame(list(zip(query_value, other_player_mapping[j])), columns=["label", "id"])
        result = pd.concat([player_lookup_df, new_players_df])
        player_lookup_df = result
        player_lookup_df = player_lookup_df.drop_duplicates()

    unique_id_lookup_df = df[["id", "unique_id", "session_id"]].sort_values(by="id")
    new_lookup_df = player_lookup_df.merge(unique_id_lookup_df, how="left", on="id")
    return new_lookup_df.sort_values(by="id")


def replace_player_labels_with_ids(df, player_lookup_df):
    for j in player_lookup_df["label"]:
        player_label_id = int(player_lookup_df.query(f"label == '{j}'")["id"])
        df = df.replace(to_replace=j, value=str(player_label_id), regex=True)
    return df


def get_game_session_df(df, player_lookup_df):
    round_number = 1
    while round_number <= 16:
        game_filter = ["session_id", "id", "unique_id"]
        game_filter += [col for col in df if col.startswith(f"game_{round_number}_")]
        game_round_df = df[game_filter]
        game_round_df.columns = game_round_df.columns.str.replace(f"game_{round_number}_", "")
        game_round_df = replace_player_labels_with_ids(game_round_df, player_lookup_df)
        num_neighbours = int(np.mean(game_round_df.player_n_neighbours))
        player_ids = game_round_df.index.unique()

        all_players_post_pd_reputation_list = []
        all_players_shared_reputation_list = []
        all_players_received_reputation_list = []
        all_players_final_reputation_list = []
        for i in player_ids:
            neighbours = str(game_round_df.query(f"index == {i}").iloc[0]["player_neighbours"]).split(",")
            current_other_players = str(game_round_df.query(f"index == {i}").iloc[0]["player_other_players"]).split(",")
            final_reputation = str(game_round_df.query(f"index == {i}").iloc[0]["player_my_ratings"]).split(",")[0:15]
            if round_number >= 6:
                post_pd_reputation = str(game_round_df["player_my_ratings_results"].get(i)).split(",")[0:15]
                neighbour_1_shared_reputation = str(game_round_df["player_shared_ratings"].get(i)).split(",")[:-1][
                    0::num_neighbours
                ]
                neighbour_2_shared_reputation = str(game_round_df["player_shared_ratings"].get(i)).split(",")[
                    1::num_neighbours
                ]
                neighbour_1_shared_reputation_dictionary = convert_reputation_str_dict_to_int_dict(
                    dict(zip(current_other_players, neighbour_1_shared_reputation)), True, True, True
                )
                neighbour_2_shared_reputation_dictionary = convert_reputation_str_dict_to_int_dict(
                    dict(zip(current_other_players, neighbour_2_shared_reputation)), True, True, True
                )
                neighbour_1_shared_dictionary = convert_reputation_str_dict_to_int_dict(
                    {neighbours[0]: neighbour_1_shared_reputation_dictionary}, True, False, False
                )
                neighbour_2_shared_dictionary = convert_reputation_str_dict_to_int_dict(
                    {neighbours[1]: neighbour_2_shared_reputation_dictionary}, True, False, False
                )
                neighbour_1_received_reputation = str(game_round_df["player_received_ratings"].get(i)).split(",")[:-1][
                    0:15
                ]
                neighbour_2_received_reputation = str(game_round_df["player_received_ratings"].get(i)).split(",")[16:30]
                neighbour_1_received_reputation_dictionary = convert_reputation_str_dict_to_int_dict(
                    dict(zip(current_other_players, neighbour_1_received_reputation)), True, True, True
                )
                neighbour_2_received_reputation_dictionary = convert_reputation_str_dict_to_int_dict(
                    dict(zip(current_other_players, neighbour_2_received_reputation)), True, True, True
                )
                neighbour_1_received_dictionary = convert_reputation_str_dict_to_int_dict(
                    {neighbours[0]: neighbour_1_received_reputation_dictionary}, True, False, False
                )
                neighbour_2_received_dictionary = convert_reputation_str_dict_to_int_dict(
                    {neighbours[1]: neighbour_2_received_reputation_dictionary}, True, False, False
                )
                if num_neighbours == 3:
                    neighbour_3_shared_reputation = str(game_round_df["player_shared_ratings"].get(i)).split(",")[
                        2::num_neighbours
                    ]
                    neighbour_3_shared_reputation_dictionary = convert_reputation_str_dict_to_int_dict(
                        dict(zip(current_other_players, neighbour_3_shared_reputation)), True, True, True
                    )
                    neighbour_3_shared_dictionary = convert_reputation_str_dict_to_int_dict(
                        {neighbours[2]: neighbour_3_shared_reputation_dictionary}, True, False, False
                    )
                    neighbour_3_received_reputation = str(game_round_df["player_received_ratings"].get(i)).split(",")[
                        31:45
                    ]
                    neighbour_3_received_reputation_dictionary = convert_reputation_str_dict_to_int_dict(
                        dict(zip(current_other_players, neighbour_3_received_reputation)), True, True, True
                    )
                    neighbour_3_received_dictionary = convert_reputation_str_dict_to_int_dict(
                        {neighbours[2]: neighbour_3_received_reputation_dictionary}, True, False, False
                    )
                else:
                    neighbour_3_shared_dictionary = {}
                    neighbour_3_received_dictionary = {}
                player_post_pd_reputation_dictionary = convert_reputation_str_dict_to_int_dict(
                    dict(zip(current_other_players, post_pd_reputation)), True, True, False
                )
                neighbours_shared_reputation_dictionary = {
                    **neighbour_1_shared_dictionary,
                    **neighbour_2_shared_dictionary,
                    **neighbour_3_shared_dictionary,
                }
                neighbours_received_reputation_dictionary = {
                    **neighbour_1_received_dictionary,
                    **neighbour_2_received_dictionary,
                    **neighbour_3_received_dictionary,
                }
            else:
                player_post_pd_reputation_dictionary = {}
                neighbours_shared_reputation_dictionary = {}
                neighbours_received_reputation_dictionary = {}

            player_final_reputation_dictionary = convert_reputation_str_dict_to_int_dict(
                dict(zip(current_other_players, final_reputation)), True, True, False
            )

            all_players_post_pd_reputation_list += [[player_post_pd_reputation_dictionary]]
            all_players_shared_reputation_list += [[neighbours_shared_reputation_dictionary]]
            all_players_received_reputation_list += [[neighbours_received_reputation_dictionary]]
            all_players_final_reputation_list += [[player_final_reputation_dictionary]]

        game_round_df.insert(20, "post_pd_reputation_dict", all_players_post_pd_reputation_list)
        game_round_df.insert(21, "shared_reputation_dict", all_players_shared_reputation_list)
        game_round_df.insert(22, "received_reputation_dict", all_players_received_reputation_list)
        game_round_df.insert(23, "final_reputation_dict", all_players_final_reputation_list)
        if round_number == 1:
            game_session_df = game_round_df
        else:
            result = pd.concat([game_session_df, game_round_df])
            game_session_df = result
        round_number += 1
    return game_session_df


drop_column_list = [
    "participant_mturk_worker_id",
    "participant_mturk_assignment_id",
    "session_mturk_hitid",
    "session_mturk_hitgroupid",
]


def convert_reputation_str_dict_to_int_dict(dict_to_convert, key_to_int, val_to_int, filter):
    new_dict = {}
    try:
        if all([key_to_int, val_to_int, filter]):
            for key, value in dict_to_convert.items():
                if int(value) >= 0:
                    new_dict[int(key)] = int(value)
        elif all([key_to_int, filter]):
            for key, value in dict_to_convert.items():
                if int(value) >= 0:
                    new_dict[int(key)] = value
        elif all([val_to_int, filter]):
            for key, value in dict_to_convert.items():
                if int(value) >= 0:
                    new_dict[key] = int(value)
        elif all([key_to_int, val_to_int]):
            for key, value in dict_to_convert.items():
                new_dict[int(key)] = int(value)
        elif all([key_to_int]):
            for key, value in dict_to_convert.items():
                new_dict[int(key)] = value
        elif all([val_to_int]):
            for key, value in dict_to_convert.items():
                new_dict[key] = int(value)
    except ValueError:
        print("Failed to clean NaN dict")
        pass

    return new_dict


def get_player_level_variables(df, lookup_df):
    session_list = df.session_id.unique()
    row_number = 0
    for i in session_list:
        player_lookup_df = lookup_df.query(f"session_id == '{i}'")
        session_df = df.query(f"session_id == '{i}'")
        player_ids = session_df.index.unique()
        round_list = session_df.subsession_round_number.unique()
        for j in player_ids:
            player_df = session_df.query(f"index == {j}")
            known_opponents_list = []
            known_gossip_list = []
            known_all_list = []
            for k in round_list:
                round_df = player_df.query(f"subsession_round_number == {k}")
                # Add in known_opponents
                neighbours = str(round_df.query(f"index == {j}").iloc[0]["player_neighbours"]).split(",")
                opponents = str(round_df.query(f"index == {j}").iloc[0]["player_opponents"]).split(",")
                received_ratings = round_df.query(f"index == {j}").iloc[0]["received_reputation_dict"]
                gossip_list = []
                if k >= 6:
                    for n in range(0, len(neighbours)):
                        gossip_list += list(received_ratings[0].get(int(neighbours[n])).keys())
                known_gossip_list += gossip_list
                known_opponents_list += opponents
                opponents_to_update = list(map(int, set(known_opponents_list)))
                gossip_to_update = list(map(int, set(known_gossip_list)))
                known_all_list += known_gossip_list
                known_all_list += known_opponents_list
                all_known_to_update = list(map(int, set(known_all_list)))
                round_df.insert(24, "known_opponents", [opponents_to_update])
                round_df.insert(25, "known_gossips", [gossip_to_update])
                round_df.insert(26, "known_all", [all_known_to_update])

                # Clean player reputation cols
                final_reputation_dict = round_df.query(f"index == {j}").iloc[0]["final_reputation_dict"]
                if k >= 6:
                    post_pd_reputation_dict = round_df.query(f"index == {j}").iloc[0]["post_pd_reputation_dict"]
                else:
                    post_pd_reputation_dict = round_df.query(f"index == {j}").iloc[0]["final_reputation_dict"]
                filtered_final_reputation_dict = filter_dict_by_list(final_reputation_dict[0], all_known_to_update)
                filtered_post_pd_reputation_dict = filter_dict_by_list(post_pd_reputation_dict[0], all_known_to_update)
                round_df = round_df.drop("final_reputation_dict", axis=1)
                round_df = round_df.drop("post_pd_reputation_dict", axis=1)
                round_df.insert(24, "final_reputation_dict", [filtered_final_reputation_dict])
                round_df.insert(25, "post_pd_reputation_dict", [filtered_post_pd_reputation_dict])

                # Add in pre_pd_reputation from previous round
                if k == 1:
                    pre_pd_reputation = np.nan
                    round_df.insert(24, "pre_pd_reputation_dict", pre_pd_reputation)
                    pre_pd_reputation = round_df["final_reputation_dict"]
                else:
                    round_df.insert(24, "pre_pd_reputation_dict", pre_pd_reputation)
                    pre_pd_reputation = round_df["final_reputation_dict"]

                # Add in opponent_reputation pre_pd and neighbour_reputation pre_share and neighbour_reputation post_share
                round_df = get_opponent_variables(round_df, k, j, player_lookup_df)
                round_df = get_neighbour_variables(round_df, k, j, player_lookup_df)
                round_df = get_other_player_reputations(round_df, k, j, player_lookup_df)

                output_round_df = round_df
                if row_number == 0:
                    output_df = output_round_df
                else:
                    result = pd.concat([output_df, output_round_df])
                    output_df = result
                row_number += 1
        print(i)
    return output_df


def get_consensus_variables(df):
    session_list = df.session_id.unique()
    row_number = 0
    for i in session_list:
        session_df = df.query(f"session_id == '{i}'")
        player_ids = session_df.index.unique()
        round_list = session_df.subsession_round_number.unique()
        for j in round_list:
            round_df = session_df.query(f"subsession_round_number == {j}")
            round_df = get_session_level_consensus(round_df)
            round_df = get_network_level_consensus(round_df, player_ids)
            round_df = get_neighbour_level_consensus(round_df, player_ids)
            output_round_df = round_df
            if row_number == 0:
                output_df = output_round_df
            else:
                result = pd.concat([output_df, output_round_df])
                output_df = result
            row_number += 1
        print(i)
    return output_df


def mean_unless_none(value_list):
    if len(value_list) > 0:
        return np.nanmean(value_list)
    else:
        return None


def var_unless_none(value_list):
    if len(value_list) > 0:
        return np.nanvar(value_list)
    else:
        return None


def get_session_level_consensus(df):
    for k in range(1, 17):
        other_player_pre_pd_reputation = list(df[f"other_player_{k}_pre_pd_reputation"])
        other_player_post_pd_reputation = list(df[f"other_player_{k}_post_pd_reputation"])
        other_player_final_reputation = list(df[f"other_player_{k}_final_reputation"])
        other_player_pre_pd_reputation = list(filter(lambda item: item is not None, other_player_pre_pd_reputation))
        other_player_post_pd_reputation = list(filter(lambda item: item is not None, other_player_post_pd_reputation))
        other_player_final_reputation = list(filter(lambda item: item is not None, other_player_final_reputation))
        other_player_pre_pd_reputation_session_mean = mean_unless_none(other_player_pre_pd_reputation)
        other_player_pre_pd_reputation_session_var = var_unless_none(other_player_pre_pd_reputation)
        other_player_post_pd_reputation_session_mean = mean_unless_none(other_player_post_pd_reputation)
        other_player_post_pd_reputation_session_var = var_unless_none(other_player_post_pd_reputation)
        other_player_final_reputation_session_mean = mean_unless_none(other_player_pre_pd_reputation)
        other_player_final_reputation_session_var = var_unless_none(other_player_pre_pd_reputation)
        df.insert(
            55, f"other_player_{k}_pre_pd_reputation_group_session_mean", other_player_pre_pd_reputation_session_mean
        )
        df.insert(
            56, f"other_player_{k}_pre_pd_reputation_group_session_var", other_player_pre_pd_reputation_session_var
        )
        df.insert(
            57, f"other_player_{k}_post_pd_reputation_group_session_mean", other_player_post_pd_reputation_session_mean
        )
        df.insert(
            58, f"other_player_{k}_post_pd_reputation_group_session_var", other_player_post_pd_reputation_session_var
        )
        df.insert(
            59, f"other_player_{k}_final_reputation_group_session_mean", other_player_final_reputation_session_mean
        )
        df.insert(60, f"other_player_{k}_final_reputation_group_session_var", other_player_final_reputation_session_var)
        defrag_df = df
        df = defrag_df
    output_df = defrag_df.copy()
    return output_df


def get_network_level_consensus(df, player_ids):
    for k in range(1, 17):
        for m in range(0, 2):
            network_consensus_df = df.query(f"index in {list(player_ids[m::2])}")
            other_player_pre_pd_reputation = list(network_consensus_df[f"other_player_{k}_pre_pd_reputation"])
            other_player_post_pd_reputation = list(network_consensus_df[f"other_player_{k}_post_pd_reputation"])
            other_player_final_reputation = list(network_consensus_df[f"other_player_{k}_final_reputation"])
            other_player_pre_pd_reputation = list(filter(lambda item: item is not None, other_player_pre_pd_reputation))
            other_player_post_pd_reputation = list(
                filter(lambda item: item is not None, other_player_post_pd_reputation)
            )
            other_player_final_reputation = list(filter(lambda item: item is not None, other_player_final_reputation))
            other_player_pre_pd_reputation_network_mean = mean_unless_none(other_player_pre_pd_reputation)
            other_player_pre_pd_reputation_network_var = var_unless_none(other_player_pre_pd_reputation)
            other_player_post_pd_reputation_network_mean = mean_unless_none(other_player_post_pd_reputation)
            other_player_post_pd_reputation_network_var = var_unless_none(other_player_post_pd_reputation)
            other_player_final_reputation_network_mean = mean_unless_none(other_player_pre_pd_reputation)
            other_player_final_reputation_network_var = var_unless_none(other_player_pre_pd_reputation)
            network_consensus_df.insert(
                55,
                f"other_player_{k}_pre_pd_reputation_group_network_mean",
                other_player_pre_pd_reputation_network_mean,
            )
            network_consensus_df.insert(
                56, f"other_player_{k}_pre_pd_reputation_group_network_var", other_player_pre_pd_reputation_network_var
            )
            network_consensus_df.insert(
                57,
                f"other_player_{k}_post_pd_reputation_group_network_mean",
                other_player_post_pd_reputation_network_mean,
            )
            network_consensus_df.insert(
                58,
                f"other_player_{k}_post_pd_reputation_group_network_var",
                other_player_post_pd_reputation_network_var,
            )
            network_consensus_df.insert(
                59, f"other_player_{k}_final_reputation_group_network_mean", other_player_final_reputation_network_mean
            )
            network_consensus_df.insert(
                60, f"other_player_{k}_final_reputation_group_network_var", other_player_final_reputation_network_var
            )
            if m == 0:
                temp_df = network_consensus_df
            else:
                result = pd.concat([temp_df, network_consensus_df])
                temp_df = result
    output_df = temp_df.copy()
    return output_df


def get_neighbour_level_consensus(df, player_ids):
    # np.seterr(all='ignore')
    for k in range(1, 17):
        for m in player_ids:
            player_df = df.query(f"index == {m}")
            neighbours = str(df.query(f"index == {m}").iloc[0]["player_neighbours"]).split(",")
            neighbours = [int(x) for x in neighbours]
            neighbour_consensus_df = df.query(f"index in {neighbours}")
            other_player_pre_pd_reputation = list(neighbour_consensus_df[f"other_player_{k}_pre_pd_reputation"])
            other_player_post_pd_reputation = list(neighbour_consensus_df[f"other_player_{k}_post_pd_reputation"])
            other_player_final_reputation = list(neighbour_consensus_df[f"other_player_{k}_final_reputation"])
            other_player_pre_pd_reputation = list(filter(lambda item: item is not None, other_player_pre_pd_reputation))
            other_player_post_pd_reputation = list(
                filter(lambda item: item is not None, other_player_post_pd_reputation)
            )
            other_player_final_reputation = list(filter(lambda item: item is not None, other_player_final_reputation))
            other_player_pre_pd_reputation_neighbour_mean = mean_unless_none(other_player_pre_pd_reputation)
            other_player_pre_pd_reputation_neighbour_var = var_unless_none(other_player_pre_pd_reputation)
            other_player_post_pd_reputation_neighbour_mean = mean_unless_none(other_player_post_pd_reputation)
            other_player_post_pd_reputation_neighbour_var = var_unless_none(other_player_post_pd_reputation)
            other_player_final_reputation_neighbour_mean = mean_unless_none(other_player_pre_pd_reputation)
            other_player_final_reputation_neighbour_var = var_unless_none(other_player_pre_pd_reputation)
            player_df.insert(
                55,
                f"other_player_{k}_pre_pd_reputation_group_neighbour_mean",
                other_player_pre_pd_reputation_neighbour_mean,
            )
            player_df.insert(
                56,
                f"other_player_{k}_pre_pd_reputation_group_neighbour_var",
                other_player_pre_pd_reputation_neighbour_var,
            )
            player_df.insert(
                57,
                f"other_player_{k}_post_pd_reputation_group_neighbour_mean",
                other_player_post_pd_reputation_neighbour_mean,
            )
            player_df.insert(
                58,
                f"other_player_{k}_post_pd_reputation_group_neighbour_var",
                other_player_post_pd_reputation_neighbour_var,
            )
            player_df.insert(
                59,
                f"other_player_{k}_final_reputation_group_neighbour_mean",
                other_player_final_reputation_neighbour_mean,
            )
            player_df.insert(
                60,
                f"other_player_{k}_final_reputation_group_neighbour_var",
                other_player_final_reputation_neighbour_var,
            )
            if m == player_ids[0]:
                temp_df = player_df
            else:
                result = pd.concat([temp_df, player_df])
                temp_df = result
    output_df = temp_df.copy()
    return output_df


def filter_dict_by_list(dict_to_filter, list):
    new_dict = {}
    for key, value in dict_to_filter.items():
        if key in list:
            new_dict[key] = value
    return new_dict


def get_opponent_variables(df, round_number, player_id, lookup_df):
    opponents = str(df["player_opponents"].get(player_id)).split(",")
    pre_pd_reputation_dict = df["pre_pd_reputation_dict"].get(player_id)
    post_pd_reputation_dict = df["post_pd_reputation_dict"].get(player_id)
    final_reputation_dict = df["final_reputation_dict"].get(player_id)
    for i in range(0, len(opponents)):
        opponent_ref = i + 1
        opponent_unique_id = lookup_df.query(f"id == {opponents[i]}").iloc[0]["unique_id"]
        if round_number == 1:
            opponent_pre_pd_reputation = None
        else:
            opponent_pre_pd_reputation = pre_pd_reputation_dict.get(int(opponents[i]))
        opponent_post_pd_reputation = post_pd_reputation_dict.get(int(opponents[i]))
        opponent_final_reputation = final_reputation_dict.get(int(opponents[i]))
        df.insert(26, f"opponent_{opponent_ref}_unique_id", [opponent_unique_id])
        df.insert(27, f"opponent_{opponent_ref}_pre_pd_reputation", [opponent_pre_pd_reputation])
        df.insert(28, f"opponent_{opponent_ref}_post_pd_reputation", [opponent_post_pd_reputation])
        df.insert(29, f"opponent_{opponent_ref}_final_reputation", [opponent_final_reputation])
    output_df = df.copy()
    return output_df


def get_neighbour_variables(df, round_number, player_id, lookup_df):
    neighbours = str(df["player_neighbours"].get(player_id)).split(",")
    post_pd_reputation_dict = df["post_pd_reputation_dict"].get(player_id)
    shared_reputation_dict = df["shared_reputation_dict"].get(player_id)
    final_reputation_dict = df["final_reputation_dict"].get(player_id)
    if len(neighbours) == 2:
        df.insert(29, "neighbour_3_unique_id", [None])
        df.insert(30, "neighbour_3_post_pd_reputation", [None])
        df.insert(31, "neighbour_3_final_reputation", [None])
        df.insert(32, "neighbour_3_share_decision", [None])
        df.insert(33, "neighbour_3_share_available", [None])
        df.insert(34, "neighbour_3_share_number", [None])
        # df.insert(34, "neighbour_3_share_low", [None])
        # df.insert(35, "neighbour_3_share_high", [None])
        for j in range(0, 11):
            df.insert(35, f"neighbour_3_share_score_{j}", [None])
    for i in range(0, len(neighbours)):
        neighbour_ref = i + 1
        if round_number >= 6:
            neighbour_unique_id = lookup_df.query(f"id == {neighbours[i]}").iloc[0]["unique_id"]
            neighbour_post_pd_reputation = post_pd_reputation_dict.get(int(neighbours[i]))
            neighbour_final_reputation = final_reputation_dict.get(int(neighbours[i]))
            if len(list(shared_reputation_dict[0].get(int(neighbours[i])))) > 0:
                neighbour_share_decision = "Yes"
            else:
                neighbour_share_decision = "No"
            neighbour_share_available = len(post_pd_reputation_dict.keys())
            neighbour_share_number = len(list(shared_reputation_dict[0].get(int(neighbours[i]))))
            # neighbour_share_low = sum(j <= 3 for j in list(shared_reputation_dict[0].get(int(neighbours[i])).values()))
            # neighbour_share_high = sum(k >= 8 for k in list(shared_reputation_dict[0].get(int(neighbours[i])).values()))
            df.insert(29, f"neighbour_{neighbour_ref}_unique_id", [neighbour_unique_id])
            df.insert(30, f"neighbour_{neighbour_ref}_post_pd_reputation", [neighbour_post_pd_reputation])
            df.insert(31, f"neighbour_{neighbour_ref}_final_reputation", [neighbour_final_reputation])
            df.insert(32, f"neighbour_{neighbour_ref}_share_decision", [neighbour_share_decision])
            df.insert(33, f"neighbour_{neighbour_ref}_share_available", [neighbour_share_available])
            df.insert(34, f"neighbour_{neighbour_ref}_share_number", [neighbour_share_number])
            # df.insert(34, f"neighbour_{neighbour_ref}_share_low", [neighbour_share_low])
            # df.insert(35, f"neighbour_{neighbour_ref}_share_high", [neighbour_share_high])
            defrag_df = df.copy()
            df = defrag_df
            for j in range(0, 11):
                num_score_available = sum(k == j for k in list(post_pd_reputation_dict.values()))
                num_score_shared = sum(k == j for k in list(shared_reputation_dict[0].get(int(neighbours[i])).values()))
                try:
                    num_score_proportion = num_score_shared / num_score_available
                except ZeroDivisionError:
                    num_score_proportion = None
                df.insert(35, f"neighbour_{neighbour_ref}_share_score_{j}", [num_score_proportion])
        else:
            df.insert(29, f"neighbour_{neighbour_ref}_unique_id", [None])
            df.insert(30, f"neighbour_{neighbour_ref}_post_pd_reputation", [None])
            df.insert(31, f"neighbour_{neighbour_ref}_final_reputation", [None])
            df.insert(32, f"neighbour_{neighbour_ref}_share_decision", [None])
            df.insert(33, f"neighbour_{neighbour_ref}_share_available", [None])
            df.insert(34, f"neighbour_{neighbour_ref}_share_number", [None])
            # df.insert(34, f"neighbour_{neighbour_ref}_share_low", [None])
            # df.insert(35, f"neighbour_{neighbour_ref}_share_high", [None])
            for j in range(0, 11):
                df.insert(35, f"neighbour_{neighbour_ref}_share_score_{j}", [None])
    output_df = df.copy()
    return output_df


def get_other_player_reputations(df, round_number, player_id, lookup_df):
    known_opponents = df["known_opponents"].get(player_id)
    neighbours = str(df["player_neighbours"].get(player_id)).split(",")
    pre_pd_reputation_dict = df["pre_pd_reputation_dict"].get(player_id)
    post_pd_reputation_dict = df["post_pd_reputation_dict"].get(player_id)
    received_reputation_dict = df["received_reputation_dict"].get(player_id)
    final_reputation_dict = df["final_reputation_dict"].get(player_id)
    for i in range(1, 17):
        other_player_unique_id = lookup_df.query(f"id == {i}").iloc[0]["unique_id"]
        if type(pre_pd_reputation_dict) is dict:
            pre_pd_reputation = pre_pd_reputation_dict.get(i)
        else:
            pre_pd_reputation = None
        post_pd_reputation = post_pd_reputation_dict.get(i)
        if round_number >= 6:
            if type(received_reputation_dict[0].get(int(neighbours[0]))) is dict:
                neighbour_1_gossip = received_reputation_dict[0].get(int(neighbours[0])).get(i)
            else:
                neighbour_1_gossip = None
            if type(received_reputation_dict[0].get(int(neighbours[1]))) is dict:
                neighbour_2_gossip = received_reputation_dict[0].get(int(neighbours[1])).get(i)
            else:
                neighbour_2_gossip = None
            if len(neighbours) == 3:
                if type(received_reputation_dict[0].get(int(neighbours[2]))) is dict:
                    neighbour_3_gossip = received_reputation_dict[0].get(int(neighbours[2])).get(i)
                else:
                    neighbour_3_gossip = None
            else:
                neighbour_3_gossip = None
        else:
            neighbour_1_gossip = None
            neighbour_2_gossip = None
            neighbour_3_gossip = None
        final_reputation = final_reputation_dict.get(i)
        gossip_1_new_flag = i not in known_opponents and neighbour_1_gossip is not None
        gossip_2_new_flag = i not in known_opponents and neighbour_2_gossip is not None
        gossip_3_new_flag = i not in known_opponents and neighbour_3_gossip is not None

        gossip_change = post_pd_reputation != final_reputation

        if post_pd_reputation is not None and final_reputation is not None:
            gossip_change_amount = abs(post_pd_reputation - final_reputation)
        elif post_pd_reputation is None and final_reputation is not None:
            gossip_change_amount = abs(5 - final_reputation)
        else:
            gossip_change_amount = None

        non_none_gossip_values = list(
            filter(lambda item: item is not None, [neighbour_1_gossip, neighbour_2_gossip, neighbour_3_gossip])
        )
        if all([neighbour_1_gossip is None, neighbour_2_gossip is None, neighbour_3_gossip is None]):
            gossip_available = None
            gossip_consensus = None
            neighbour_1_pre_gossip_consensus = None
            neighbour_1_post_gossip_consensus = None
            neighbour_2_pre_gossip_consensus = None
            neighbour_2_post_gossip_consensus = None
            neighbour_3_pre_gossip_consensus = None
            neighbour_3_post_gossip_consensus = None
        elif any([neighbour_1_gossip is not None, neighbour_2_gossip is not None, neighbour_3_gossip is not None]):
            gossip_available = len(non_none_gossip_values)
            gossip_consensus = np.var(non_none_gossip_values)
            if post_pd_reputation is not None:
                if neighbour_1_gossip is not None:
                    neighbour_1_pre_gossip_consensus = np.var([post_pd_reputation, neighbour_1_gossip])
                else:
                    neighbour_1_pre_gossip_consensus = None
                if neighbour_2_gossip is not None:
                    neighbour_2_pre_gossip_consensus = np.var([post_pd_reputation, neighbour_2_gossip])
                else:
                    neighbour_2_pre_gossip_consensus = None
                if neighbour_3_gossip is not None:
                    neighbour_3_pre_gossip_consensus = np.var([post_pd_reputation, neighbour_3_gossip])
                else:
                    neighbour_3_pre_gossip_consensus = None
            else:
                neighbour_1_pre_gossip_consensus = None
                neighbour_2_pre_gossip_consensus = None
                neighbour_3_pre_gossip_consensus = None

            if final_reputation is not None:
                if neighbour_1_gossip is not None:
                    neighbour_1_post_gossip_consensus = np.var([final_reputation, neighbour_1_gossip])
                else:
                    neighbour_1_post_gossip_consensus = None
                if neighbour_2_gossip is not None:
                    neighbour_2_post_gossip_consensus = np.var([final_reputation, neighbour_2_gossip])
                else:
                    neighbour_2_post_gossip_consensus = None
                if neighbour_3_gossip is not None:
                    neighbour_3_post_gossip_consensus = np.var([final_reputation, neighbour_3_gossip])
                else:
                    neighbour_3_post_gossip_consensus = None
            else:
                neighbour_1_post_gossip_consensus = None
                neighbour_2_post_gossip_consensus = None
                neighbour_3_post_gossip_consensus = None
        df.insert(35, f"other_player_{i}_unique_id", other_player_unique_id)
        df.insert(36, f"other_player_{i}_pre_pd_reputation", pre_pd_reputation)
        df.insert(37, f"other_player_{i}_post_pd_reputation", post_pd_reputation)
        df.insert(38, f"other_player_{i}_neighbour_1_gossip", neighbour_1_gossip)
        df.insert(39, f"other_player_{i}_neighbour_2_gossip", neighbour_2_gossip)
        df.insert(40, f"other_player_{i}_neighbour_3_gossip", neighbour_3_gossip)
        df.insert(41, f"other_player_{i}_final_reputation", final_reputation)
        defrag_df = df.copy()
        df = defrag_df
        df.insert(42, f"other_player_{i}_neighbour_1_gossip_new_flag", gossip_1_new_flag)
        df.insert(43, f"other_player_{i}_neighbour_2_gossip_new_flag", gossip_2_new_flag)
        df.insert(44, f"other_player_{i}_neighbour_3_gossip_new_flag", gossip_3_new_flag)
        df.insert(45, f"other_player_{i}_gossip_change_flag", gossip_change)
        df.insert(46, f"other_player_{i}_gossip_change_amount", gossip_change_amount)
        defrag_df = df.copy()
        df = defrag_df
        df.insert(47, f"other_player_{i}_gossip_available", gossip_available)
        df.insert(48, f"other_player_{i}_gossip_consensus", gossip_consensus)
        df.insert(49, f"other_player_{i}_neighbour_1_pre_gossip_consensus", neighbour_1_pre_gossip_consensus)
        df.insert(50, f"other_player_{i}_neighbour_2_pre_gossip_consensus", neighbour_2_pre_gossip_consensus)
        df.insert(51, f"other_player_{i}_neighbour_3_pre_gossip_consensus", neighbour_3_pre_gossip_consensus)
        df.insert(52, f"other_player_{i}_neighbour_1_post_gossip_consensus", neighbour_1_post_gossip_consensus)
        df.insert(53, f"other_player_{i}_neighbour_2_post_gossip_consensus", neighbour_2_post_gossip_consensus)
        df.insert(54, f"other_player_{i}_neighbour_3_post_gossip_consensus", neighbour_3_post_gossip_consensus)
        # defrag_df = df.copy()
        # df = defrag_df
        # df.insert(55, f"other_player_{i}_consensus_neighbour_group", )
        # df.insert(55, f"other_player_{i}_consensus_network", )
        # df.insert(55, f"other_player_{i}_consensus_session", )

    output_df = df.copy()
    return output_df


other_player_mapping = {
    1: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    2: [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    3: [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    4: [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    5: [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    6: [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    7: [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    8: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16],
    9: [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16],
    10: [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16],
    11: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16],
    12: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16],
    13: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16],
    14: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16],
    15: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16],
    16: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
}
