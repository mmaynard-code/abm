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
        "session.code": "session_id",
    }
    column_filter_list = [
        "participant",
        "game",
        "session",
        "p1_survey",
        "end_survey",
        "payment_info",
    ]
    column_filters = []
    for i in column_filter_list:
        column_filters += [col for col in df if col.startswith(i)]
    df = df[column_filters].rename(columns=column_names_to_remap)
    df.columns = df.columns.str.replace(".", "_", regex=True)
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
    return player_lookup_df.sort_values(by="id")


def replace_player_labels_with_ids(df, player_lookup_df):
    for j in player_lookup_df["label"]:
        player_label_id = int(player_lookup_df.query(f"label == '{j}'")["id"])
        df = df.replace(to_replace=j, value=str(player_label_id), regex=True)
    return df


def get_game_session_df(df, player_lookup_df):
    round_number = 1
    while round_number <= 16:
        game_filter = ["session_id", "id"]
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
            neighbours = str(game_round_df["player_neighbours"].get(i)).split(",")
            current_other_players = str(game_round_df["player_other_players"].get(i)).split(",")
            final_reputation = str(game_round_df["player_my_ratings"].get(i)).split(",")[0:15]
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


def get_player_level_variables(df):
    session_list = df.session_id.unique()
    row_number = 0
    for i in session_list:
        session_df = df.query(f"session_id == '{i}'")
        player_ids = session_df.index.unique()
        for j in player_ids:
            player_df = session_df.query(f"index == {j}")
            round_list = player_df.subsession_round_number.unique()
            known_opponents_list = []
            known_gossip_list = []
            known_all_list = []
            for k in round_list:
                round_df = player_df.query(f"subsession_round_number == {k}")
                # Add in known_opponents
                opponents = str(round_df["player_opponents"].get(j)).split(",")
                neighbours = str(round_df["player_neighbours"].get(j)).split(",")
                received_ratings = round_df["received_reputation_dict"].get(j)
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
                round_df = round_df.drop("known_all", axis=1)

                # Clean player reputation cols
                final_reputation_dict = round_df["final_reputation_dict"].get(j)
                if k >= 6:
                    post_pd_reputation_dict = round_df["post_pd_reputation_dict"].get(j)
                else:
                    post_pd_reputation_dict = round_df["final_reputation_dict"].get(j)
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
                pre_pd_reputation_dict = round_df["pre_pd_reputation_dict"].get(j)
                post_pd_reputation_dict = round_df["post_pd_reputation_dict"].get(j)
                final_reputation_dict = round_df["final_reputation_dict"].get(j)
                if k == 1:
                    opponent_1_pre_pd_reputation = None
                    opponent_2_pre_pd_reputation = None
                else:
                    opponent_1_pre_pd_reputation = pre_pd_reputation_dict.get(int(opponents[0]))
                    opponent_2_pre_pd_reputation = pre_pd_reputation_dict.get(int(opponents[1]))
                opponent_1_post_pd_reputation = post_pd_reputation_dict.get(int(opponents[0]))
                opponent_2_post_pd_reputation = post_pd_reputation_dict.get(int(opponents[1]))
                opponent_1_final_reputation = final_reputation_dict.get(int(opponents[0]))
                opponent_2_final_reputation = final_reputation_dict.get(int(opponents[1]))
                if k >= 6:
                    neighbour_1_share_reputation = post_pd_reputation_dict.get(int(neighbours[0]))
                    neighbour_2_share_reputation = post_pd_reputation_dict.get(int(neighbours[1]))
                    neighbour_1_final_reputation = final_reputation_dict.get(int(neighbours[0]))
                    neighbour_2_final_reputation = final_reputation_dict.get(int(neighbours[1]))
                    if len(neighbours) == 3:
                        neighbour_3_share_reputation = post_pd_reputation_dict.get(int(neighbours[2]))
                        neighbour_3_final_reputation = final_reputation_dict.get(int(neighbours[2]))
                    else:
                        neighbour_3_share_reputation = None
                        neighbour_3_final_reputation = None
                else:
                    neighbour_1_share_reputation = None
                    neighbour_2_share_reputation = None
                    neighbour_1_final_reputation = None
                    neighbour_2_final_reputation = None
                    neighbour_3_share_reputation = None
                    neighbour_3_final_reputation = None
                round_df.insert(27, "opponent_1_pre_pd_reputation", [opponent_1_pre_pd_reputation])
                round_df.insert(28, "opponent_1_post_pd_reputation", [opponent_1_post_pd_reputation])
                round_df.insert(29, "opponent_1_final_reputation", [opponent_1_final_reputation])
                round_df.insert(30, "opponent_2_pre_pd_reputation", [opponent_2_pre_pd_reputation])
                round_df.insert(31, "opponent_2_post_pd_reputation", [opponent_2_post_pd_reputation])
                round_df.insert(32, "opponent_2_final_reputation", [opponent_2_final_reputation])
                round_df.insert(33, "neighbour_1_share_reputation", [neighbour_1_share_reputation])
                round_df.insert(34, "neighbour_1_final_reputation", [neighbour_1_final_reputation])
                round_df.insert(35, "neighbour_2_share_reputation", [neighbour_2_share_reputation])
                round_df.insert(36, "neighbour_2_final_reputation", [neighbour_2_final_reputation])
                round_df.insert(37, "neighbour_3_share_reputation", [neighbour_3_share_reputation])
                round_df.insert(38, "neighbour_3_final_reputation", [neighbour_3_final_reputation])

                output_round_df = round_df
                if row_number == 0:
                    output_df = output_round_df
                result = pd.concat([output_df, output_round_df])
                output_df = result
                row_number += 1
        print(i)
    return output_df


def filter_dict_by_list(dict_to_filter, list):
    new_dict = {}
    for key, value in dict_to_filter.items():
        if key in list:
            new_dict[key] = value
    return new_dict


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
