import os

import pandas as pd
import plotly.express as px

directory = "C:/Users/mattu/Repos/abm/pd_model"

file_list = []
for root, dir, files in os.walk(directory):
    for file in files:
        file_matching_logic = [os.path.splitext(file)[1] == ".csv", file[0:6] == "result"]
        if all(file_matching_logic):
            file_list += [os.path.join(root, file)]

for file in file_list:
    data = pd.read_csv(file)

    figure = px.histogram(
        data.query("opponent_pre_pd_reputation != -1"),
        x="opponent_pre_pd_reputation",
        range_y=[0, 2000],
        color="player_decision",
        # barnorm="percent",
        facet_col="treatment_ref",
        marginal="box",
        color_discrete_sequence=px.colors.qualitative.Set3,
        category_orders=dict(
            player_decision=["Cooperate", "Defect"],
            RunId=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            treatment_ref=["A", "B", "C"],
        ),
        labels={
            "player_decision": "Game Decision",
            "opponent_pre_pd_reputation": "Opponent Reputation",
            "treatment_ref": "Network Type",
        },
        title="Player Game Decision by Opponent Reputation",
    )
