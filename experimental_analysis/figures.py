import pandas as pd
import plotly.express as px

df = pd.read_csv("experimental_data.csv")
print(df.columns)

data = df

pd_decision_data = pd.read_csv("pd_decision_data.csv")

pd_decision_fig = px.histogram(
    pd_decision_data.query("opponent_pre_pd_reputation != -1"),
    x="opponent_pre_pd_reputation",
    color="player_decision",
    barnorm="percent",
    facet_col="treatment_ref",
    marginal="box",
    category_orders=dict(
        player_decision=["X", "Y"],
        opponent_pre_pd_reputation=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        treatment_ref=["Circle Network", "Transitive", "Small World"],
    ),
)
pd_decision_fig.update_xaxes(type="category")
pd_decision_fig.show()
pd_decision_no_rep_fig = px.histogram(
    pd_decision_data.query("opponent_pre_pd_reputation == -1"),
    x="opponent_pre_pd_reputation",
    color="player_decision",
    barnorm="percent",
    facet_col="treatment_ref",
    marginal="box",
    category_orders=dict(
        player_decision=["X", "Y"],
        # opponent_pre_pd_reputation=[0,1,2,3,4,5,6,7,8,9,10],
        treatment_ref=["Circle Network", "Transitive", "Small World"],
    ),
)
pd_decision_no_rep_fig.update_xaxes(type="category")
pd_decision_no_rep_fig.show()

share_decision_data = pd.read_csv("share_decision_data.csv")
share_decision_fig = px.histogram(
    share_decision_data,
    x="neighbour_post_pd_reputation",
    # range_x=[0,10],
    color="neighbour_share_decision",
    barnorm="percent",
    facet_col="treatment_ref",
    marginal="box",
    category_orders=dict(
        neighbour_share_decision=["Yes", "No", "Sharing Not Possible"],
        treatment_ref=["Circle Network", "Transitive", "Small World"],
        neighbour_post_pd_reputation=[0, 1, 2, 3, 4, -1, 5, 6, 7, 8, 9, 10],
        neighbour_share_number=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        neighbour_share_low=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        neighbour_share_high=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    ),
)
share_decision_fig.update_xaxes(type="category")
share_decision_fig.show()
