# import matplotlib.pyplot as plt
from multiprocessing import freeze_support

import mesa
import pandas as pd
from model import SimpleModel

# from money_model import MoneyModel


# import numpy as np

# params = {"width": 10, "height": 10, "N": range(10, 500, 10)}

# empty_model = SimpleModel(8, 2, 3, "random")
# empty_model.step()
# empty_model.step()

if __name__ == "__main__":
    freeze_support()
    results = mesa.batch_run(
        SimpleModel,
        parameters={"network_agents": 8, "total_networks": 2, "treatment_id": [2, 3, 4], "game_type": "reputation"},
        iterations=100,
        max_steps=100,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    results_df = pd.DataFrame(results)

    # print(results_df[results_df["Step"] <= 2])
    # print(results_df)

    results_df.to_csv("results.csv")


# available_groups = list(range(1, 5))
# print(available_groups)
# while len(available_groups) > 0:
#     random_group = random.choice(available_groups)
#     print(random_group)
#     available_groups.remove(random_group)
#     print(available_groups)

# agent_id = 3
# if agent_id == (3 | 4 | 5):
#     print("Yes")
# else:
#     print("No")


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
