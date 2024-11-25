import os.path
import random
import re
import subprocess
import sys
import time

# ---------- utils ----------

def read_input(fname):  # returns (edges, terminals), each edge is (u, v, cost)
  edges, terminals = [], []
  with open(fname) as f:
    for line in f:
      if re.match(r'E \d+ \d+ \d+', line):
        edges.append(tuple(map(int, line.split()[1:])))
      elif re.match(r'T \d+', line):
        terminals.append(int(line[2:]))
  return edges, terminals

# ---------- algorithms ----------

def _run_external(execfname, edges, terminals, timeout=None):
  # prepare input
  num_nodes = max(max(max(u, v) for u, v, _ in edges), max(terminals))
  inputlines = []
  inputlines.append("SECTION Graph")
  inputlines.append("Nodes %d" % num_nodes)
  inputlines.append("Edges %d" % len(edges))
  for u, v, w in edges:
    inputlines.append("E %d %d %d" % (u, v, w))
  inputlines.append("END")
  inputlines.append("SECTION Terminals")
  inputlines.append("Terminals %d" % len(terminals))
  for t in terminals:
    inputlines.append("T %d" % t)
  inputlines.append("END")
  inputlines.append("EOF")
  inputdata = '\n'.join(inputlines)
  # run program
  process = subprocess.Popen(
    args=[execfname],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    universal_newlines=True)
  try:
    outputdata, _ = process.communicate(inputdata, timeout)
  except subprocess.TimeoutExpired:
    process.terminate()
    outputdata, _ = process.communicate()
  outputlines = outputdata.split('\n')
  # parse solution
  e2i = dict(((min(u,v), max(u,v)), i) for i, (u, v, _) in enumerate(edges))
  solution = [False] * len(edges)
  selfreported_solution_value = None
  for line in outputlines:
    if re.match(r'VALUE \d+', line):
      assert selfreported_solution_value is None
      selfreported_solution_value = int(line.split()[1])
    elif re.match(r'\d+ \d+', line):
      u, v  = map(int, line.split())
      u, v = min(u, v), max(u, v)
      assert (u, v) in e2i
      solution[e2i[(u, v)]] = True
  solution_value = sum(w for (u, v, w), x in zip(edges, solution) if x == True)
  assert solution_value == selfreported_solution_value
  return solution_value, solution

def apx2(edges, terminals):
  return _run_external('./MehlhornSteinerTree2Apx', edges, terminals)
  
def alps(edges, terminals, predictions, alpha=None):
  modified_edges = [(u, v, w * (0 if alpha is None else int(1000 / alpha)) if p else w * 1000)
                    for (u, v, w), p in zip(edges, predictions)]
  _, solution = apx2(modified_edges, terminals)
  solution_value = sum(w for (u, v, w), in_sol in zip(edges, solution) if in_sol)
  return solution_value, solution

def cimat(edges, terminals, timeout=60.0):  # winner of PACE 2018 Track C
  return _run_external('SteinerTreeProblem/V4/main', edges, terminals, timeout)
  
# ---------- experiments ----------

def synthetic_predictions(predictions, prob_false_neg):
  dist1 = lambda: random.choices((False, True), (prob_false_neg, 1.0 - prob_false_neg))[0]
  num0 = predictions.count(False)
  num1 = predictions.count(True)
  dist0 = lambda: random.choices((True, False), (prob_false_neg * num1, max(0, num0 - prob_false_neg * num1)))[0]
  return [dist1() if p else dist0() for p in predictions]

def connected_component(edges, source):
  max_node_id = max(max(u, v) for u, v, _ in edges)
  p = list(range(max_node_id + 1))
  def find(a):
    if p[a] == a:
      return a
    p[a] = find(p[a])
    return p[a]
  for u, v, _ in edges:
    p[find(u)] = find(v)
  return [u for u in range(max_node_id + 1) if find(u) == find(source)]

def main():
  random.seed('Steiner')

  edges, terminals = read_input(sys.argv[1])
  instance_name = os.path.basename(sys.argv[1])

  # Synthetic predictions experiment

  before = time.time()
  pace_solution_value, pace_solution = cimat(edges, terminals, timeout=60.0)  # run for 1 minute
  after =  time.time()
  print(instance_name, 'SP', 'PACE', pace_solution_value, 0, 0, sep=',')
  print(instance_name, 'PACE time', after - before, 'seconds', file=sys.stderr)

  before = time.time()
  apx2_solution_value, apx2_solution = apx2(edges, terminals)
  after =  time.time()
  print(instance_name, 'SP', '2APX', apx2_solution_value, 0, 0, sep=',')
  print(instance_name, '2APX time', after - before, 'seconds', file=sys.stderr)

  NUM_ITERS = 10
  for iter in range(NUM_ITERS):
    for p in range(0, 10 + 1):
      predictions = synthetic_predictions(pace_solution, 0.1 * p)
      for alpha in [1.1, 1.2, 1.4, 2, 4, None]:
        solution_value, _ = alps(edges, terminals, predictions, alpha)
        print(instance_name, 'SP', 'ALPS(alpha=%s)' % ('inf' if alpha is None else str(alpha)), solution_value, 10*p, iter, sep=',')

  # Terminals resampling experiment

  NUM_SAMPLES = 10
  connected_component_to_sample_from = connected_component(edges, terminals[0])
  for resampling_p in range(0, 10 + 1):
    for keep_fixed in (True, False):
      # terminals = random.sample(connected_component_to_sample_from, len(terminals))  # removes a possible structure of the original instance from the distribution
      NUM_RESAMPLES = int(resampling_p / 10 * len(terminals))
      experiment_name = "TRfix" if keep_fixed else "TR"
      if keep_fixed:
        fixed_terminals = random.sample(terminals, len(terminals) - NUM_RESAMPLES)
        sampled_terminals = [sorted(random.sample(connected_component_to_sample_from, NUM_RESAMPLES) + fixed_terminals) for _ in range(NUM_SAMPLES)]
      else:
        sampled_terminals = [sorted(random.sample(connected_component_to_sample_from, NUM_RESAMPLES) + random.sample(terminals, len(terminals) - NUM_RESAMPLES)) for _ in range(NUM_SAMPLES)]

      optimal_solutions = [cimat(edges, T, timeout=60.0) for T in sampled_terminals]
      for idx in range(NUM_SAMPLES):
        print(instance_name, experiment_name, 'PACE', optimal_solutions[idx][0], 10*resampling_p, idx, sep=',')
        apx2_solution_value, apx2_solution = apx2(edges, sampled_terminals[idx])
        print(instance_name, experiment_name, '2APX', apx2_solution_value, 10*resampling_p, idx, sep=',')
        predictions = []
        for i in range(len(edges)):
          num1 = sum([optimal_solutions[jdx][1][i] for jdx in range(NUM_SAMPLES) if jdx != idx])
          predictions.append(num1 * 2 > NUM_SAMPLES - 1)
        for alpha in [1.1, 1.2, 1.4, 2, 4, None]:
          solution_value, _ = alps(edges, sampled_terminals[idx], predictions, alpha)
          print(instance_name, experiment_name, 'ALPS(alpha=%s)' % ('inf' if alpha is None else str(alpha)), solution_value, 10*resampling_p, idx, sep=',')

if __name__ == '__main__':
  main()
