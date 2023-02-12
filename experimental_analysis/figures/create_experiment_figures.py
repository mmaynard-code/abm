# import subprocess
import pandas as pd
import plotly.express as px

# subprocess.call("Rscript C:/Users/mattu/Repos/abm/experimental_analysis/analysis.R", shell=True)

pd_decision_data = pd.read_csv("pd_decision_data.csv")

pd_decision_fig = px.histogram(
    pd_decision_data.query("opponent_pre_pd_reputation != -1"),
    x="opponent_pre_pd_reputation",
    range_y=[0, 2000],
    color="player_decision",
    # barnorm="percent",
    facet_col="treatment_ref",
    marginal="box",
    color_discrete_sequence=px.colors.qualitative.Set3,
    category_orders=dict(
        player_decision=["Cooperate", "Defect"],
        opponent_pre_pd_reputation=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        treatment_ref=["A", "B", "C"],
    ),
    labels={
        "player_decision": "Game Decision",
        "opponent_pre_pd_reputation": "Opponent Reputation",
        "treatment_ref": "Network Type",
    },
    title="Player Game Decision by Opponent Reputation",
)
pd_decision_fig.update_xaxes(type="category")
pd_decision_fig.show()
pd_decision_fig.write_html("experimental_analysis/figures/pd_decision_fig.html")

pd_scoring_fig = px.histogram(
    pd_decision_data,
    x="player_payoff",
    # range_y=[0, 2000],
    color="opponent_post_pd_reputation",
    # barnorm="percent",
    facet_col="treatment_ref",
    # marginal="box",
    color_discrete_sequence=px.colors.qualitative.Set3,
    category_orders=dict(
        player_decision=["Cooperate", "Defect"],
        opponent_post_pd_reputation=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        treatment_ref=["A", "B", "C"],
    ),
    labels={
        "player_decision": "Game Decision",
        "opponent_pre_pd_reputation": "Opponent Reputation",
        "treatment_ref": "Network Type",
    },
    title="Player Scoring Decision by Opponent Decision",
)
pd_scoring_fig.update_xaxes(type="category")
pd_scoring_fig.show()
pd_scoring_fig.write_html("experimental_analysis/figures/pd_scoring_fig.html")

share_decision_data = pd.read_csv("share_decision_data.csv")
share_decision_fig = px.histogram(
    share_decision_data,
    x="neighbour_post_pd_reputation",
    range_y=[0, 2000],
    color="neighbour_share_decision",
    # barnorm="percent",
    facet_col="treatment_ref",
    marginal="box",
    color_discrete_sequence=px.colors.qualitative.Set3,
    category_orders=dict(
        neighbour_share_decision=["Share", "Won't share", "Can't share"],
        treatment_ref=["A", "B", "C"],
        neighbour_post_pd_reputation=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        neighbour_share_number=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        neighbour_share_low=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        neighbour_share_high=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    ),
    labels={
        "neighbour_share_decision": "Share Decision",
        "neighbour_post_pd_reputation": "Neighbour Reputation",
        "treatment_ref": "Network Type",
    },
    title="Player Share Decision by Neighbour Reputation",
)
share_decision_fig.update_xaxes(type="category")
share_decision_fig.show()
share_decision_fig.write_html("experimental_analysis/figures/share_decision_fig.html")

update_decision_data = pd.read_csv("update_decision_data_filtered_simple_gossip.csv")
update_decision_gossip_sender_reputation_fig = px.histogram(
    update_decision_data,
    x="neighbour_post_pd_reputation",
    range_y=[0, 2000],
    color="gossip_change_flag",
    # barnorm="percent",
    facet_col="treatment_ref",
    marginal="box",
    color_discrete_sequence=px.colors.qualitative.Set3,
    category_orders=dict(
        gossip_change_flag=[True, False],
        treatment_ref=["A", "B", "C"],
        neighbour_post_pd_reputation=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ),
    labels={
        "gossip_change_flag": "Update Decision",
        "neighbour_post_pd_reputation": "Gossip Sender Reputation",
        "treatment_ref": "Network Type",
    },
    title="Player Update Decision by Gossip Sender Reputation",
)
update_decision_gossip_sender_reputation_fig.update_xaxes(type="category")
update_decision_gossip_sender_reputation_fig.show()
update_decision_gossip_sender_reputation_fig.write_html(
    "experimental_analysis/figures/update_decision_gossip_sender_reputation_fig.html"
)

update_decision_gossip_target_reputation_fig = px.histogram(
    update_decision_data,
    x="neighbour_gossip",
    range_y=[0, 2000],
    color="gossip_change_flag",
    # barnorm="percent",
    facet_col="treatment_ref",
    marginal="box",
    color_discrete_sequence=px.colors.qualitative.Set3,
    category_orders=dict(
        gossip_change_flag=[True, False],
        treatment_ref=["A", "B", "C"],
        neighbour_gossip=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ),
    labels={
        "gossip_change_flag": "Update Decision",
        "neighbour_gossip": "Gossip Target Reputation",
        "treatment_ref": "Network Type",
    },
    title="Player Update Decision by Gossip Target Reputation",
)
update_decision_gossip_target_reputation_fig.update_xaxes(type="category")
update_decision_gossip_target_reputation_fig.show()
update_decision_gossip_target_reputation_fig.write_html(
    "experimental_analysis/figures/update_decision_gossip_target_reputation_fig.html"
)

update_decision_gossip_subject_reputation_fig = px.histogram(
    update_decision_data,
    x="post_pd_reputation",
    range_y=[0, 2000],
    color="gossip_change_flag",
    # barnorm="percent",
    facet_col="treatment_ref",
    marginal="box",
    color_discrete_sequence=px.colors.qualitative.Set3,
    category_orders=dict(
        gossip_change_flag=[True, False],
        treatment_ref=["A", "B", "C"],
        post_pd_reputation=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ),
    labels={
        "gossip_change_flag": "Update Decision",
        "post_pd_reputation": "Gossip Subject Reputation",
        "treatment_ref": "Network Type",
    },
    title="Player Update Decision by Gossip Subject Reputation",
)
update_decision_gossip_subject_reputation_fig.update_xaxes(type="category")
update_decision_gossip_subject_reputation_fig.show()
update_decision_gossip_subject_reputation_fig.write_html(
    "experimental_analysis/figures/update_decision_gossip_subject_reputation_fig.html"
)
