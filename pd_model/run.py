# import matplotlib.pyplot as plt
from multiprocessing import freeze_support

import mesa
import pandas as pd
from model import SimpleModel

if __name__ == "__main__":
    freeze_support()
    parameter_config = {
        "network_groups": {2},
        "total_networks": {4},
        "treatment_ref": {"B"},
        "game_type": {"gossip"},
        "gossip_logic": {"complex"},
    }
    n_iterations = 2
    n_steps = 100
    # combinations = 0
    # for i in parameter_config:
    #     if combinations == 0:
    #         combinations = len(parameter_config[i])
    #     else:
    #         combinations *= len(parameter_config[i])
    # combinations *= n_iterations

    # print("Running " + str(combinations) + " simulations.")

    results = mesa.batch_run(
        SimpleModel,
        parameters=parameter_config,
        iterations=n_iterations,
        max_steps=n_steps,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    print("Creating pandas DataFrame.")

    results_df = pd.DataFrame(results)

    print("Writing results to csv file.")

    results_df.to_csv("results.csv")

    print("Completed.")
