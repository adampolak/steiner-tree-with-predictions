#include <assert.h>
#include <stdint.h>

#include <algorithm>
#include <functional>
#include <iostream>
#include <istream>
#include <numeric>
#include <queue>
#include <string>
#include <utility>
#include <vector>
using namespace std;

struct expect { string expected_token; };

istream& operator>>(istream& is, const expect& et) {
  string actual_token;
  cin >> actual_token;
  assert(et.expected_token == actual_token);
  return is;
}

int main() {
  // Read input
  ios_base::sync_with_stdio(false);
  int num_nodes, num_edges;
  cin >> expect{"SECTION"} >> expect{"Graph"};
  cin >> expect{"Nodes"} >> num_nodes;
  cin >> expect{"Edges"} >> num_edges;
  typedef pair<int64_t, pair<int, int>> Edge;
  vector<Edge> edges;
  edges.reserve(num_edges);
  vector<vector<pair<int, int64_t>>> adj(num_nodes + 1);
  while (num_edges--) {
    int u, v;
    int64_t w;
    cin >> expect{"E"} >> u >> v >> w;
    edges.emplace_back(w, pair<int,int>(u, v));
    adj[u].emplace_back(v, w);
    adj[v].emplace_back(u, w);
  }
  cin >> expect{"END"};
  cin >> expect{"SECTION"} >> expect{"Terminals"};
  vector<bool> is_terminal(num_nodes + 1, false);
  int num_terminals;
  cin >> expect{"Terminals"} >> num_terminals;
  while (num_terminals--) {
      int t;
      cin >> expect{"T"} >> t;
      is_terminal[t] = true;
  }
  cin >> expect{"END"};
  cin >> expect{"EOF"};
  // Dijkstra from terminals
  vector<int64_t> distance(num_nodes + 1, 1e18);
  vector<int> parent(num_nodes + 1, -1), source(num_nodes + 1, -1);
  priority_queue<pair<int64_t, int>, vector<pair<int64_t, int>>, greater<pair<int64_t, int>>> Q;
  for (int t = 1; t <= num_nodes; ++t) {
    if (is_terminal[t]) {
      distance[t] = 0;
      source[t] = t;
      Q.emplace(0, t);
    }
  }
  while (!Q.empty()) {
    int64_t d = Q.top().first;
    int u = Q.top().second;
    Q.pop();
    if (distance[u] < d)
      continue;
    for (auto edge : adj[u]) {
      int v = edge.first;
      int64_t w = edge.second;
      if (distance[v] > distance[u] + w) {
        distance[v] = distance[u] + w;
        parent[v] = u;
        source[v] = source[u];
        Q.emplace(distance[v], v);
      }
    }
  }
  // Sorting edges of G1', constructing G2=MST(G1'), and finding nodes of G3
  auto key = [&](Edge e) { return e.first + distance[e.second.first] + distance[e.second.second]; };
  sort(edges.begin(), edges.end(), [&](Edge a, Edge b) { return key(a) < key(b); });
  vector<int> fu_parent(num_nodes + 1);
  function<int(int)> fu_find = [&](int a) { return fu_parent[a] == a ? a : fu_parent[a] = fu_find(fu_parent[a]); };
  function<bool(int, int)> fu_union = [&](int a, int b) { a = fu_find(a); b = fu_find(b); fu_parent[a] = b; return a != b; };
  iota(fu_parent.begin(), fu_parent.end(), 0);
  vector<bool> G3_nodes = is_terminal;
  // int64_t debug_mst_val = 0;
  for (Edge edge : edges) {
    int u = edge.second.first;
    int v = edge.second.second;
    if (source[u] == -1)
      continue;  // unreachable from terminals
    assert(source[v] != -1);
    if (fu_union(source[u], source[v])) {  // adding edge to G2 and nodes to G3
      while (u != source[u]) {
        G3_nodes[u] = true;
        u = parent[u];
      }
      while (v != source[v]) {
        G3_nodes[v] = true;
        v = parent[v];
      }
      // debug_mst_val += key(edge);
    }
  }
  // cerr << "First MST value " << debug_mst_val << endl;
  // Computing G4=MST(G3)
  sort(edges.begin(), edges.end());
  iota(fu_parent.begin(), fu_parent.end(), 0);
  vector<vector<pair<int, int64_t>>> G4_adj(num_nodes + 1);
  int64_t mst_value = 0;
  for (Edge edge : edges) {
    int u = edge.second.first;
    int v = edge.second.second;
    int64_t w = edge.first;
    if (!(G3_nodes[u] && G3_nodes[v]))
      continue;
    if (fu_union(u, v)) {  // adding edge to G4
      G4_adj[u].emplace_back(v, w);
      G4_adj[v].emplace_back(u, w);
      mst_value += w;
    }
  }
  // Removing non-terminal leaves of G4 to obtain G5
  vector<bool> G5_nodes = G3_nodes;
  vector<int> G5_degree(num_nodes + 1);
  queue<int> nonterminal_leaves;
  for (int u = 1; u <= num_nodes; ++u) {
    G5_degree[u] = G4_adj[u].size();
    if (G5_degree[u] == 1 && !is_terminal[u])
      nonterminal_leaves.push(u);
  }
  while (!nonterminal_leaves.empty()) {
    int u = nonterminal_leaves.front();
    nonterminal_leaves.pop();
    G5_nodes[u] = false;
    for (auto edge : G4_adj[u]) {
      int v = edge.first;
      int64_t w = edge.second;
      if (G5_nodes[v]) {
        --G5_degree[v];
        if (G5_degree[v] == 1 && !is_terminal[v]){
          nonterminal_leaves.push(v);
        }
        mst_value -= w;
      }
    }
  }
  // Output
  cout << "VALUE " << mst_value << endl;
  for (int u = 1; u <= num_nodes; ++u) {
    if (G5_nodes[u]) {
      for (auto edge : G4_adj[u]) {
        int v = edge.first;
        if (G5_nodes[v] && u < v)
          cout << u << " " << v << endl;
      }
    }
  }
}
