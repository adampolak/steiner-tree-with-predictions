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


for fixed in (True, False):

  PATH_results = '../results.csv'
  data = pd.read_csv(PATH_results, names=['instance', 'experiment', 'alg', 'val', 'prob', 'iter'])

  # filter relevant rows
  data = data[data['experiment']==('TRfix' if fixed else 'TR')]

  # filter relevant columns
  data = data[['instance', 'alg', 'val', 'prob', 'iter']]

  paceVal = data[(data['alg']=='PACE')]
  MSTVal = data[(data['alg']=='2APX')]

  # data = data[(data['alg']!='PACE') & (data['alg'] !='2APX')]

  data = pd.merge(data, paceVal, on=['instance', 'prob', 'iter'], suffixes = ['', '_pace'])
  data = pd.merge(data, MSTVal,  on=['instance', 'prob', 'iter'], suffixes = ['', '_mst'])
  data = data[['instance', 'alg', 'prob', 'iter', 'val', 'val_pace', 'val_mst']]

  data['val_robust'] = data[['val', 'val_mst']].min(axis=1)

  data['ratio'] = data['val'] / data['val_pace']
  data['ratio_robust'] = data['val_robust'] / data['val_pace']

  data['quality'] = (data['val']-data['val_pace'])/((data['val_mst']-data['val_pace'])+0.01)
  data['quality_robust'] = (data['val_robust']-data['val_pace'])/((data['val_mst']-data['val_pace'])+0.01)
  
  data['instance_gap'] = data['val_mst'] / data['val_pace']
  instance_gap = data.groupby(['instance']).agg({'instance_gap': 'min'}).reset_index()
  data = pd.merge(data, instance_gap, on=['instance'], suffixes=['', '_min'])
  data = data[data['instance_gap_min'] >= 1.01]

  KEYS = ('val', 'val_robust', 'ratio', 'ratio_robust', 'quality', 'quality_robust')
  stddev = data.groupby(['instance', 'alg', 'prob']).agg(dict((key, 'std') for key in KEYS)).reset_index()
  data = data.groupby(['instance', 'alg', 'prob']).agg(dict((key, 'mean') for key in KEYS)).reset_index()
  # print(stddev)
  # print(data)
  print((stddev['val'] / data['val']).quantile(0.95))
  print((stddev['val'] / data['val']).max())

  alg_names = sorted(data['alg'].unique())
  instance_names = sorted(data['instance'].unique())

  print(len(instance_names))

  # for instance_name in instance_names:
  for instance_name in (['instance011.gr', 'instance178.gr'] if fixed else ['instance082.gr',]):
    idata = data[data['instance'] == instance_name]
    for key in ('val',):  # KEYS[::2]:
      averages_columns = pd.DataFrame(index=[0.1 * p for p in range(11)])
      for alg_name in alg_names:
        averages_columns[translate_algname(alg_name)]=idata[idata['alg'] == str(alg_name)][key].values
      # plot = averages_columns.plot(title='%s Terminals resampled (%s)' % (instance_name, 'fixed' if fixed else 'not fixed'))
      plot = averages_columns.plot()
      # if key.startswith('quality'):
      #   plot.set_ylim(-0.05, 1.25)
      # elif key.startswith('ratio'):
      #   plot.set_ylim(0.95, 1.3)
      plt.xlabel('Fraction of resampled terminals')
      plt.ylabel('Cost of the solution')
      plt.gcf().set_size_inches(5, 4)
      plt.tight_layout()
      plt.savefig('%s_learned_%s_%s' % (instance_name[:-3], 'FixedCore' if fixed else 'NoCore', key), dpi=300)
      plt.close()
  
  data = data.groupby(['alg', 'prob']).agg(dict((key, 'mean') for key in KEYS)).reset_index()
  for key in ('quality',):
    averages_columns = pd.DataFrame(index=[0.1 * p for p in range(11)])
    for alg_name in alg_names:
      if alg_name.startswith('ALPS'):
        averages_columns[translate_algname(alg_name)]=data[data['alg'] == str(alg_name)][key].values
    # plot = averages_columns.plot(title='Terminals resampled (%s) %s' % ('fixed' if fixed else 'not fixed'))
    plot = averages_columns.plot()
    # if key.startswith('quality'):
    #   plot.set_ylim(-0.05, 1.25)
    # else:
    #   plot.set_ylim(0.95, 1.1)
    plot.set_ylim(-0.05, 1.25)
    plt.yticks([0,1], ['CIMAT', 'Mehlhorn'])
    # plt.yticks([0.2,0.4,0.6,0.8], minor=True)
    plt.xlabel('Fraction of resampled terminals')
    plt.ylabel('Cost of the solution')
    plt.grid(True, which='major', axis='y')
    plt.gcf().set_size_inches(5, 4)
    plt.tight_layout()
    plt.savefig('learned_%s_%s' % ('FixedCore' if fixed else 'NoCore', key), dpi=300)
    plt.close()
