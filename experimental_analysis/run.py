import traceback

import pandas as pd
from data_cleaning import get_experimental_csv_files_from_directory
from data_cleaning import get_game_session_df
from data_cleaning import get_player_level_variables
from data_cleaning import get_session_player_lookup_df
from data_cleaning import merge_all_experimental_data_from_file_list

directory = "C:/Users/mattu/OneDrive - Linköpings universitet/MSc Thesis/ResultsCSVs"
csv_file_paths = get_experimental_csv_files_from_directory(directory, ".csv")
df = merge_all_experimental_data_from_file_list(csv_file_paths)
game_1 = [col for col in df if col.startswith("game_1_")]
session_ids = df.session_id.unique()
valid_files_processed = 0
invalid_files = 0
for i in session_ids:
    print(i)
    session_df = df.query(f"session_id == '{i}'")
    print(session_df.head())
    invalid_session_ids = ["kwxymf3f", "n8260zfz", "kfqtdyhc", "d0kgewwv", "y0qju3fl", "i6p3092c", "881ii9en"]
    if i in invalid_session_ids:
        continue
    try:
        player_lookup_df = get_session_player_lookup_df(session_df)
        game_session_df = get_game_session_df(session_df, player_lookup_df)
        valid_files_processed += 1
    except Exception:
        traceback.print_exc()
        invalid_files += 1
        break
    if i == "d837pvak":
        all_session_df = game_session_df
    else:
        result = pd.concat([all_session_df, game_session_df])
        all_session_df = result

print(all_session_df.columns)
print("Number of valid sessions processed: " + str(valid_files_processed))
print("Number of invalid sessions found: " + str(invalid_files))

output_df = get_player_level_variables(all_session_df)
# print(output_df.columns)
print(output_df.head())
print(len(output_df.index))
print(26 * 16 * 16)

output_df.sort_values(by=["session_id", "subsession_round_number", "id"]).to_csv(
    "experimental_data.csv", sep=",", na_rep=None, index=False
)
