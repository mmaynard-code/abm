# import matplotlib.pyplot as plt
from multiprocessing import freeze_support

import mesa
import pandas as pd
from model import SimpleModel

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

    results_df.to_csv("results.csv")
