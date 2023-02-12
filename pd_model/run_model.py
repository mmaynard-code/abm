# import matplotlib.pyplot as plt
# mypy: ignore-errors
from multiprocessing import freeze_support

import mesa
import pandas as pd
from model import SimpleModel

if "aggregate" in "baseline, pd_game, aggregate":
    pass

if __name__ == "__main__":
    freeze_support()
    all_parameter_config = {
        "network_groups": {2},
        "total_networks": {2},
        "treatment_ref": {"C"},
        "game_type": {"gossip"},
    }
    n_iterations = 10
    n_steps = 1000

    # noqa
    combinations = n_iterations
    for key, values in all_parameter_config.items():
        combinations = combinations * len(values)

    print(
        f"Running {str(combinations)} simulations of {str(n_steps)} steps. {str(combinations * n_steps)} steps in total."
    )

    for values in all_parameter_config.get("network_groups"):
        network_groups = values
        for values in all_parameter_config.get("total_networks"):
            total_networks = values
            for values in all_parameter_config.get("treatment_ref"):
                treatment_ref = values
                for values in all_parameter_config.get("game_type"):
                    game_type = values
                    parameter_config = {
                        "network_groups": {network_groups},
                        "total_networks": {total_networks},
                        "treatment_ref": {treatment_ref},
                        "game_type": {game_type},
                        "consensus_type": {"grouped"},
                        "reporter_config": {"baseline, pd_game, aggregate"},
                    }
                    print(parameter_config)
                    parameter_filename = f"result_{network_groups}_{total_networks}_{treatment_ref}_{game_type}"
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
                    print(results_df.columns)
                    print("Writing results to csv file.")

                    # results_df.to_csv(f"{parameter_filename}.csv")

                    print("Completed.")
