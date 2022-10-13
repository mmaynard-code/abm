import os
from collections import defaultdict
from itertools import chain

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
        # "game.1.player.treatment_id": "treatment_id",
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

        neighbours_dictionary = game_round_df["player_neighbours"]
        other_players_dictionary = game_round_df["player_other_players"]

        post_pd_reputation_dictionary = game_round_df["player_my_ratings_results"]
        shared_reputation_dictionary = game_round_df["player_shared_ratings"]
        # received_reputation_dictionary = game_round_df["player_received_ratings"]
        final_reputation_dictionary = game_round_df["player_my_ratings"]
        all_players_shared_reputation_list = []
        all_players_post_pd_reputation_list = []
        all_players_final_reputation_list = []
        for i in player_ids:
            # opponents = str(opponents_dictionary.get(i)).split(",")
            neighbours = str(neighbours_dictionary.get(i)).split(",")
            current_other_players = str(other_players_dictionary.get(i)).split(",")

            post_pd_reputation = str(post_pd_reputation_dictionary.get(i)).split(",")[0:15]
            final_reputation = str(final_reputation_dictionary.get(i)).split(",")[0:15]

            neighbour_1_shared_reputation = str(shared_reputation_dictionary.get(i)).split(",")[0::num_neighbours]
            neighbour_2_shared_reputation = str(shared_reputation_dictionary.get(i)).split(",")[1::num_neighbours]
            neighbour_1_shared_reputation_dictionary = dict(zip(current_other_players, neighbour_1_shared_reputation))
            neighbour_2_shared_reputation_dictionary = dict(zip(current_other_players, neighbour_2_shared_reputation))
            neighbour_1_dictionary = {neighbours[0]: neighbour_1_shared_reputation_dictionary}
            neighbour_2_dictionary = {neighbours[1]: neighbour_2_shared_reputation_dictionary}
            if num_neighbours == 3:
                neighbour_3_shared_reputation = str(shared_reputation_dictionary.get(i)).split(",")[2::num_neighbours]
                neighbour_3_shared_reputation_dictionary = dict(
                    zip(current_other_players, neighbour_3_shared_reputation)
                )
                neighbour_3_dictionary = {neighbours[2]: neighbour_3_shared_reputation_dictionary}
            else:
                neighbour_3_dictionary = {}

            player_post_pd_reputation_dictionary = dict(zip(current_other_players, post_pd_reputation))
            neighbours_shared_reputation_dictionary = {
                **neighbour_1_dictionary,
                **neighbour_2_dictionary,
                **neighbour_3_dictionary,
            }
            player_final_reputation_dictionary = dict(zip(current_other_players, final_reputation))

            all_players_post_pd_reputation_list += [[player_post_pd_reputation_dictionary]]
            all_players_shared_reputation_list += [[neighbours_shared_reputation_dictionary]]
            all_players_final_reputation_list += [[player_final_reputation_dictionary]]
        game_round_df.insert(20, "post_pd_reputation_dict", all_players_post_pd_reputation_list)
        game_round_df.insert(21, "shared_reputation_dict", all_players_shared_reputation_list)
        game_round_df.insert(22, "final_reputation_dict", all_players_final_reputation_list)
        if round_number == 1:
            game_session_df = game_round_df
        else:
            result = pd.concat([game_session_df, game_round_df])
            game_session_df = result
        round_number += 1
    return game_session_df


def get_player_level_variables(df):
    session_list = df.session_id.unique()
    # print(session_list)
    # valid_count = 0
    # invalid_count = 0
    row_number = 0
    for i in session_list:
        session_df = df.query(f"session_id == '{i}'")
        player_ids = session_df.index.unique()
        for j in player_ids:
            player_df = session_df.query(f"index == {j}")
            round_list = player_df.subsession_round_number.unique()
            known_opponents_list = []
            for k in round_list:
                round_df = player_df.query(f"subsession_round_number == {k}")
                # known_opponents_list += round_df["player_opponents"]
                opponents_dictionary = round_df["player_opponents"]
                # timeout_dictionary = round_df["player_timed_out"]
                final_rating_dictionary = round_df["final_reputation_dict"]
                opponents = str(opponents_dictionary.get(j)).split(",")
                # timeout = str(timeout_dictionary.get(j)).split(",")
                final_rating = final_rating_dictionary.get(j)
                print(final_rating)
                known_opponents_list += opponents
                round_df.insert(23, "known_opponents", list(set(known_opponents_list)))
                if row_number == 0:
                    output_df = round_df
                else:
                    result = pd.concat([output_df, round_df])
                    output_df = result
                # print("player " + str(j) + " round " + str(k) + " knows " + str(len(list(dict.fromkeys(known_opponents_list)))))
            # print(known_opponents_list)
        print(i)
    return output_df
    # print("Valid player rounds = " + str(valid_count))
    # print("Invalid player rounds = " + str(invalid_count))
    # print("Total player rounds = " + str(invalid_count + valid_count))


def get_known_opponents_in_game_session_df(df):
    opponent_filter = ["session_id", "id", "subsession_round_number", "player_opponents"]
    opponent_lookup_df = df[opponent_filter]
    round_number = 1
    known_opponents_dict = defaultdict(list)
    while round_number <= 16:
        round_opponents_df = opponent_lookup_df.query(f"subsession_round_number == {round_number}")
        player_number = 1
        round_opponents_dict = {}
        while player_number <= 16:
            player_opponent_1 = int(list(round_opponents_df["player_opponents"])[player_number - 1].split(",")[0])
            player_opponent_2 = int(list(round_opponents_df["player_opponents"])[player_number - 1].split(",")[1])
            player_opponents = [player_opponent_1, player_opponent_2]
            player_opponents_dict = {player_number: player_opponents}
            round_opponents_dict = {**round_opponents_dict, **player_opponents_dict}
            player_number += 1
            if round_number == 1:
                known_opponents_dict = defaultdict(list)
            for key, value in round_opponents_dict.items():
                known_opponents_dict[key].append(value)
        player_number = 1
        if round_number == 1:
            known_opponents_list = []
        while player_number <= 16:
            player_known_opponents = set(chain(*known_opponents_dict.get(player_number)))
            known_opponents_list += [player_known_opponents]
            player_number += 1
        round_number += 1
    return known_opponents_list


def expand_opponent_and_neighbour_columns(df):
    df[["opponent_1", "opponent_2"]] = df["player_opponents"].str.split(",", expand=True)
    return df


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
