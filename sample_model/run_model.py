# import matplotlib.pyplot as plt
import mesa
import pandas as pd
from simple_model import SimpleModel

# from money_model import MoneyModel


# import numpy as np

# params = {"width": 10, "height": 10, "N": range(10, 500, 10)}

# empty_model = SimpleModel(8, 2)
# empty_model.step()

results = mesa.batch_run(
    SimpleModel,
    parameters={"network_agents": 8, "total_networks": 2},
    iterations=1,
    max_steps=5,
    number_processes=1,
    data_collection_period=1,
    display_progress=True,
)

results_df = pd.DataFrame(results)

# print(results_df)

# results = mesa.batch_run(
#     MoneyModel,
#     parameters=params,
#     iterations=5,
#     max_steps=100,
#     number_processes=1,
#     data_collection_period=1,
#     display_progress=True,
# )

# results_df = pd.DataFrame(results)

# results_filtered = results_df[(results_df.AgentID == 0) & (results_df.Step == 100)]
# N_values = results_filtered.N.values
# gini_values = results_filtered.Gini.values
# plt.scatter(N_values, gini_values)
