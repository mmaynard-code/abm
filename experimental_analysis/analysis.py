# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

# import plotly.graph_objects as go
# from bokeh.plotting import figure
# from bokeh.plotting import output_file
# from bokeh.plotting import show

df = pd.read_csv("experimental_data.csv")
print(df.columns)

# graph = figure(title = "Decision Bar Chart")
# data = df
# graph.vbar(
#     data["opponent_1_pre_pd_reputation"],
#     top=data["player_decision1"],
#     legend_label = "Decision 1 by Opponent Reputation",
#     color = "green")
# graph.vbar(
#     data["opponent_2_pre_pd_reputation"],
#     top=data["player_decision2"],
#     legend_label = "Decision 2 by Opponent Reputation",
#     color = "red")
# graph.legend.click_policy = "hide"
# show(graph)

data = df
int_treatment = data["subsession_treatment_id"]
print(int_treatment.replace(2, "Circle Network").replace(3, "Small World").replace(4, "Transitive"))
data.insert(
    39, "treatment_ref", int_treatment.replace(2, "Circle Network").replace(3, "Small World").replace(4, "Transitive")
)
data_treatment_2 = df.query("subsession_treatment_id == 2")
data_treatment_3 = df.query("subsession_treatment_id == 3")
data_treatment_4 = df.query("subsession_treatment_id == 4")

pd_decision_data = pd.DataFrame(data[["player_decision1", "opponent_1_pre_pd_reputation", "treatment_ref"]])
pd_decision_data.columns = ["player_decision2", "opponent_2_pre_pd_reputation", "treatment_ref"]
result = pd.concat([pd_decision_data, data[["player_decision2", "opponent_2_pre_pd_reputation", "treatment_ref"]]])
pd_decision_data = result
pd_decision_data.columns = ["player_decision", "opponent_pre_pd_reputation", "treatment_ref"]
print(pd_decision_data.columns)
int_pd_rep = pd_decision_data["opponent_pre_pd_reputation"]
print(int_pd_rep.replace(np.nan, -1))
pd_decision_data.insert(2, "opponent_pre_pd_reputation_neg", int_pd_rep.replace(np.nan, -1))


fig = px.histogram(
    pd_decision_data.query("opponent_pre_pd_reputation_neg >= 0"),
    x="opponent_pre_pd_reputation_neg",
    color="player_decision",
    facet_col="treatment_ref",
    marginal="box",
    category_orders=dict(player_decision=["X", "Y"], treatment_ref=["Circle Network", "Transitive", "Small World"]),
)
fig.show()
