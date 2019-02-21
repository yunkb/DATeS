#!/usr/bin/env python

"""
Apply Ensemble Kalman Filter to Lorenz96 model.
"""

import sys
import numpy as np


# Define environment variables and update Python search path;
# this is a necessary call that must be inserted in the beginning of any driver.
import dates_setup
dates_setup.initialize_dates()
#
import dates_utility as utility  # import DATeS utility module(s)


# Create a model object
# ---------------------
from lorenz_models import Lorenz96  as Lorenz
model = Lorenz(model_configs={'create_background_errors_correlations':True,
                     'observation_noise_level':0.05,
                     'observation_vector_size':20,
                     'background_noise_level':0.08})
#
# create observations' and assimilation checkpoints:
obs_checkpoints = np.arange(0.1,0.301, 0.1)
da_checkpoints = np.arange(0, 0.01, 0.5)
analysis_trajectory_timespan = np.arange(0, .301, 0.01)
#

# Create DA pieces:
# ---------------------
# create initial ensemble...
ensemble_size = 25
initial_ensemble = model.create_initial_ensemble(ensemble_size=ensemble_size)

# create filter object
from EnKS import EnKS as EnKF_Smoother
enks_configs = dict(model=model,
                    analysis_ensemble=initial_ensemble,
                    forecast_ensemble=None,
                    ensemble_size=ensemble_size,
                    inflation_factor=1.0,
                   )
smoother_obj = EnKS_Smoother(filter_configs=enks_configs,
                             output_configs=dict(file_output_moment_only=False)
                            )

# Create sequential DA
# processing object:
# ---------------------
# Here this is a filtering_process object;
from smoothing_process import SmoothingProcess
experiment_configs = dict(smoother=smoother_obj,
                          experiment_timespan=[analysis_trajectory_timespan[0], analysis_trajectory_timespan[-1]],
                          obs_checkpoints=obs_checkpoints,
                          observations_list=None,
                          da_checkpoints=da_checkpoints,
                          initial_ensemble=initial_ensemble,
                          ref_initial_condition=ref_IC,
                          ref_initial_time=analysis_trajectory_timespan[0],
                          analysis_timespan=analysis_trajectory_timespan,
                          random_seed=_random_seed
                          )
experiment = SmoothingProcess(assimilation_configs=dict(smoother=smoother_obj,
                                                        obs_checkpoints=obs_checkpoints,
                                                        da_checkpoints=da_checkpoints,
                                                        forecast_first=True,
                                                        ref_initial_condition=model._reference_initial_condition.copy(),
                                                        ref_initial_time=0,
                                                        random_seed=2345
                                                        ),
                              output_configs = dict(scr_output=True,
                                                    scr_output_iter=1,
                                                    file_output=True,
                                                    file_output_iter=1)
                              )
# run the sequential filtering over the timespan created by da_checkpoints
experiment.recursive_assimilation_process()

#
# Clean executables and temporary modules
# ---------------------
# utility.clean_executable_files()
#
