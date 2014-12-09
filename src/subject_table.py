#!/usr/bin/env python

import os
from collections import defaultdict

import yaml
import numpy as np
import pandas as pd

from utils import generate_meta_data_tables


with open('config.yml', 'r') as f:
    config = yaml.load(f)

root = config['root_data_directory']

tables = generate_meta_data_tables(root)

subject_df = tables['TOP|subject']

for trial in ['001', '002']:
    if trial in subject_df.index:
        subject_df = subject_df.drop(trial)

# Create columns for each speed that contain a list of the
for_group = subject_df.copy()
for_group['Speed'] = tables['TOP|trial']['nominal-speed']
grouped_by_id_speed = for_group.groupby(['id', 'Speed'])

index = defaultdict(list)
trials_per = defaultdict(list)
for (subject_id, speed), trial_ids in grouped_by_id_speed.groups.items():
    index[speed].append(subject_id)
    trials_per[speed].append(', '.join([t.lstrip("0") for t in trial_ids]))

unique_subjects = subject_df.drop_duplicates()
unique_subjects.index = unique_subjects['id']

for speed, trials in trials_per.items():
    speed_key = '{:1.1f} m/s'.format(speed)
    unique_subjects[speed_key] = pd.Series(trials, index[speed])

cols = ['id', 'gender', 'age', 'height', 'mass', '0.8 m/s', '1.2 m/s',
        '1.6 m/s']
units = ['', '', ' [yr]', ' [m]', ' [kg]', '', '', '']
new_cols = [s.capitalize() + u for s, u in zip(cols, units)]
unique_subjects.rename(columns=dict(zip(cols, new_cols)), inplace=True)

formatters = {'Height [m]': lambda x: 'NA' if np.isnan(x)
              else '{:0.2f}'.format(x),
              'Mass [kg]': lambda x: 'NA' if np.isnan(x)
              else '{:0.0f}'.format(x)}

unique_subjects = unique_subjects.drop_duplicates()
unique_subjects = unique_subjects.drop(0)  # remove null subject

table_dir = os.path.join('..', 'tables')
if not os.path.exists(table_dir):
    os.makedirs(table_dir)

with open(os.path.join(table_dir, 'subjects.tex'), 'w') as f:
    f.write(unique_subjects.sort().to_latex(na_rep='NA', index=False,
                                            columns=new_cols,
                                            formatters=formatters))