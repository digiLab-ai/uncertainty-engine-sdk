# imports
from itertools import combinations
from typing import Optional, Union
import warnings

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from uncertainty_engine.client import Client
from uncertainty_engine.nodes.sensor_designer import (
    BuildSensorDesigner,
    ScoreSensorDesign,
    SuggestSensorDesign,
)


class Designer:
    def __init__(
        self,
        email: str,
        observables: pd.DataFrame,
        quantities_of_interest: Optional[pd.DataFrame] = None,
        sigma: Optional[Union[float, list[float]]] = None,
    ):
        self.client = Client(
            email=email,
            deployment="https://13qg20i4yc.execute-api.eu-west-2.amazonaws.com/dev/api",
        )
        observables = observables.to_dict(orient="list")

        if quantities_of_interest is not None:
            quantities_of_interest = quantities_of_interest.to_dict(orient="list")

        builder = BuildSensorDesigner(
            sensor_data=observables,
            quantities_of_interest_data=quantities_of_interest,
            sigma=sigma,
        )

        response = self.client.run_node(builder)

        self.designer = response["output"]["sensor_designer"]

    def suggest(self, num_sensors: int, num_eval: int):
        suggest_design = SuggestSensorDesign(
            sensor_designer=self.designer,
            num_sensors=num_sensors,
            num_eval=num_eval,
        )

        response = self.client.run_node(suggest_design)

        self.designer = response["output"]["sensor_designer"]

        if num_sensors >= 25:
            objective = "Exact"
        else:
            objective = "GP-Based"

        # Disable GP-based objective function if no quantities of interest are provided
        if (objective == "GP-Based") and (
            len(self.designer["bed"]["quantities_of_interest_df"]) == 0
        ):
            objective = "Exact"

        n_sensor_cache = {}
        for k, v in self.designer["bed"]["cache"]["Exact"].items():
            if len(eval(k)) != num_sensors:
                continue
            for sub_k, sub_v in v.items():
                if sub_k in ["mean_score", "score_var"]:
                    indices = eval(k)  # Ensure this is a list or tuple
                    if isinstance(indices, list):
                        indices = tuple(indices)  # Convert list to tuple

                    new_key = tuple(
                        [
                            list(self.designer["bed"]["sensor_df"][0].keys())[i]
                            for i in indices
                        ]
                    )
                    if new_key in n_sensor_cache:
                        n_sensor_cache[new_key].update({sub_k: sub_v})
                    else:
                        n_sensor_cache[new_key] = {sub_k: sub_v}

        top_5 = dict(
            sorted(
                n_sensor_cache.items(), key=lambda x: x[1]["mean_score"], reverse=True
            )[: min(5, len(n_sensor_cache))]
        )

        return top_5

    def score(self, design: list):
        score_design = ScoreSensorDesign(
            sensor_designer=self.designer,
            design=design,
        )

        response = self.client.run_node(score_design)

        self.designer = response["output"]["sensor_designer"]

        return response["output"]["score"]

    def redundancy_analysis(
        self, designs: list, num_dropout: list = [1], objective="Exact", num_iter=1
    ):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for design in designs:
                for length in len(design) - np.array(num_dropout):
                    for combo in combinations(design, length):
                        for _ in range(num_iter):
                            self.score(list(combo))

        redundancy_results = {}
        for design in designs:
            redundancy_results[str(design)] = {}
            for length in len(design) - np.array(num_dropout):
                length = int(length)
                overall_mean = 0
                means = []
                vars = []
                combs = list(combinations(design, length))
                for combo in combs:
                    sensor_ids = list(self.designer["bed"]["sensor_df"][0].keys())
                    combo_inds = [sensor_ids.index(sensor) for sensor in combo]
                    if (
                        str(list(combo_inds))
                        not in self.designer["bed"]["cache"][objective]
                    ):
                        continue
                    means.append(
                        self.designer["bed"]["cache"][objective][str(list(combo_inds))][
                            "mean_score"
                        ]
                    )
                    vars.append(
                        self.designer["bed"]["cache"][objective][str(list(combo_inds))][
                            "score_var"
                        ]
                    )
                overall_mean = np.mean(means)
                overall_var = np.var(means) + np.mean(vars)
                redundancy_results[str(design)][length] = {
                    "mean": overall_mean,
                    "var": overall_var,
                }

        for length in len(design) - np.array(num_dropout):
            x_labels = list(redundancy_results.keys())
            means = [value[length]["mean"] for value in redundancy_results.values()]
            std_devs = [
                np.sqrt(value[length]["var"]) for value in redundancy_results.values()
            ]
            x_indices = range((len(x_labels)))

            plt.figure(figsize=(10, 10))

            # Plot scatter points for the mean
            plt.scatter(x_indices, means, color="purple", label="Mean", zorder=3)

            # Plot error bars for 1st and 2nd standard deviations
            for x, mean, std in zip(x_indices, means, std_devs):
                # 1st standard deviation error bars
                plt.errorbar(
                    x,
                    mean,
                    yerr=std,
                    fmt="o",
                    color="purple",
                    label="1st Std Dev" if x == 0 else "",
                    zorder=2,
                    elinewidth=3,
                )
                # 2nd standard deviation error bars
                plt.errorbar(
                    x,
                    mean,
                    yerr=2 * std,
                    fmt="o",
                    color="darkorange",
                    label="2nd Std Dev" if x == 0 else "",
                    zorder=1,
                    capsize=5,
                    elinewidth=3,
                )

            # Customize the plot
            plt.xticks(x_indices, x_labels, rotation=90)
            plt.xlabel("Designs")
            plt.ylabel("GP-EIG")
            plt.title(f"GPEIG Distributions With {len(design) - length} Sensor Dropout")
            plt.legend()

            # Show the plot
            plt.tight_layout()
            plt.show()
            plt.close()

    def visualise_score_distribution(self):
        for objective in self.designer["bed"]["cache"].keys():
            if len(self.designer["bed"]["cache"][objective]) == 0:
                continue

            # Determine the length of design keys and plot separate histograms
            design_lengths = {}
            for design_key in self.designer["bed"]["cache"][objective].keys():
                length = len(eval(design_key))
                if length not in design_lengths:
                    design_lengths[length] = []
                design_lengths[length].append(
                    self.designer["bed"]["cache"][objective][design_key]["mean_score"]
                )

            for length, scores in design_lengths.items():
                plt.figure()
                plt.hist(scores, bins=50, color="#3ab09e", edgecolor="black")
                plt.xlabel(f"EIG")
                plt.ylabel("Frequency")
                plt.title(
                    f"EIG Distribution for {objective} Objective Function (Design Length: {length})"
                )
                plt.show()
                plt.close()

    visualize_score_distribution = visualise_score_distribution
