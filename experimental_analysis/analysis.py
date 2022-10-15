import numpy as np
import pandas as pd


def get_pd_decision_data(input_df):
    df = pd.DataFrame(input_df[["player_decision1", "opponent_1_pre_pd_reputation", "treatment_ref"]])
    df.columns = ["player_decision2", "opponent_2_pre_pd_reputation", "treatment_ref"]
    result = pd.concat([df, input_df[["player_decision2", "opponent_2_pre_pd_reputation", "treatment_ref"]]])
    df = result
    df.columns = ["player_decision", "opponent_pre_pd_reputation", "treatment_ref"]
    int_pd_rep = df["opponent_pre_pd_reputation"]
    df.insert(2, "opponent_pre_pd_reputation_neg", int_pd_rep.replace(np.nan, -1))
    return df


def get_share_decision_data(input_df):
    df = input_df[
        [
            "neighbour_1_post_pd_reputation",
            "neighbour_1_final_reputation",
            "neighbour_1_share_decision",
            "neighbour_1_share_number",
            "neighbour_1_share_low",
            "neighbour_1_share_high",
            "treatment_ref",
        ]
    ]
    df.columns = [
        "neighbour_2_post_pd_reputation",
        "neighbour_2_final_reputation",
        "neighbour_2_share_decision",
        "neighbour_2_share_number",
        "neighbour_2_share_low",
        "neighbour_2_share_high",
        "treatment_ref",
    ]
    result = pd.concat(
        [
            df,
            input_df[
                [
                    "neighbour_2_post_pd_reputation",
                    "neighbour_2_final_reputation",
                    "neighbour_2_share_decision",
                    "neighbour_2_share_number",
                    "neighbour_2_share_low",
                    "neighbour_2_share_high",
                    "treatment_ref",
                ]
            ],
        ]
    )
    df = result
    df.columns = [
        "neighbour_3_post_pd_reputation",
        "neighbour_3_final_reputation",
        "neighbour_3_share_decision",
        "neighbour_3_share_number",
        "neighbour_3_share_low",
        "neighbour_3_share_high",
        "treatment_ref",
    ]
    result = pd.concat(
        [
            df,
            input_df[
                [
                    "neighbour_3_post_pd_reputation",
                    "neighbour_3_final_reputation",
                    "neighbour_3_share_decision",
                    "neighbour_3_share_number",
                    "neighbour_3_share_low",
                    "neighbour_3_share_high",
                    "treatment_ref",
                ]
            ],
        ]
    )
    df = result
    df.columns = [
        "neighbour_post_pd_reputation",
        "neighbour_final_reputation",
        "neighbour_share_decision",
        "neighbour_share_number",
        "neighbour_share_low",
        "neighbour_share_high",
        "treatment_ref",
    ]
    df.insert(0, "n", 1)
    return df
