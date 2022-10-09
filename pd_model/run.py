# import matplotlib.pyplot as plt
from multiprocessing import freeze_support

import mesa
import pandas as pd
from model import SimpleModel

# empty_model = SimpleModel(8, 2, 4, "gossip")
# empty_model.step()
# empty_model.step()

if __name__ == "__main__":
    freeze_support()
    results = mesa.batch_run(
        SimpleModel,
        parameters={
            "network_groups": 2,
            "total_networks": 2,
            "treatment_id": 4,
            "game_type": "gossip",
            "gossip_logic": "simple",
        },
        iterations=1,
        max_steps=11,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    results_df = pd.DataFrame(results)

    print(results_df[(results_df["Step"] == 10) & (results_df["AgentID"] == 0)])
    # print(results_df)

    results_df.to_csv("results.csv")
