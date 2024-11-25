#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 12})

def translate_algname(algname):
  if algname == 'PACE':
    return 'CIMAT'
  if algname == '2APX':
    return 'Mehlhorn'
  return algname.replace('alpha', 'α').replace('inf', '∞')

PATH_results = '../results.csv'
data = pd.read_csv(PATH_results, names=['instance', 'experiment', 'alg', 'val', 'prob', 'iter'])

PATH_bestKnown = '../SteinerTree-PACE-2018-instances/track3.csv'
best_known = pd.read_csv(PATH_bestKnown).rename(columns={'paceName':'instance'})
best_known['instance'] = best_known['instance'].str.replace(" ", "")  # removes trailing whitespace


# filter relevant rows
data = data[data['experiment']=='SP']

# filter relevant columns
data = data[['instance', 'alg', 'val', 'prob', 'iter']]

paceVal = data[(data['alg']=='PACE')]
MSTVal = data[(data['alg']=='2APX')]

stddev = data.groupby(['instance', 'alg', 'prob']).agg({'val':'std'}).reset_index()
data = data.groupby(['instance', 'alg', 'prob']).agg({'val':'mean'}).reset_index()
print((stddev['val'] / data['val']).max())
print((stddev['val'] / data['val']).quantile(0.99))

data = pd.merge(data, best_known.rename(columns={'lower':'opt'}), on=['instance'])

data['ratio'] = data['val']/data['opt']   

data = data.groupby(['alg', 'prob']).agg({'ratio':'mean'}).reset_index()

alg_names = sorted(data['alg'].unique())

averages_columns = pd.DataFrame(index=[0.1*_ for _ in range(11)])

for alg_name in alg_names:
  if alg_name.startswith('ALPS'):
    averages_columns[translate_algname(alg_name)]=data[data['alg'] == str(alg_name)]['ratio'].values
  else:
    averages_columns[translate_algname(alg_name)]=data[data['alg'] == str(alg_name)]['ratio'].values[0]

plot = averages_columns.plot()
plot.set_ylim(1, 1.25)

plt.xlabel('Fraction of mispredicted edges')
plt.ylabel('Mean approximation ratio')
plt.gcf().set_size_inches(5, 4)
plt.tight_layout()
plt.savefig('synthetic', dpi=300)
plt.close()




