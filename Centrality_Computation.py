# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

import arcpy
from Constants import *
from Utils import *
from operator import add
import heapq
from math import exp

"""
Computes reach, gravity_type_index, betweenness, closeness, and straightness on a graph.
|nodes|: representation of graph, a dictionary mapping node id's to Node objects
|compute_r|: compute reach?
|compute_g|: compute gravity_type_index?
|compute_b|: compute betweenness?
|compute_c|: compute closeness?
|compute_s|: compute straightness?
|radius|: buffer radius, only consider nodes that can be reached within this distance
|beta|: parameter for gravity_type_index
|measures_to_normalize|: a list of the measures to normalize
|accumulator_fields|: a list of cost attributes to accumulate
"""
def compute_centrality(nodes,
                       compute_r, compute_g, compute_b, compute_c, compute_s,
                       radius,
                       beta,
                       measures_to_normalize,
                       accumulator_fields):

  # Number of nodes in the graph
  N = len(nodes)
  if N == 0:
    return

  # Preprocessing
  have_accumulations = len(accumulator_fields) > 0
  have_locations = hasattr(nodes.values()[0], location)
  if compute_s and not have_locations:
    # We cannot compute straightness without node locations
    compute_s = False
  if compute_b:
    # Initialize betweenness values
    for id in nodes:
      setattr(nodes[id], betweenness, 0.0)
  
  # Initialize the sum of all node weights (normalization)
  sum_weights = 0.0

  # Computation
  progress = Progress_Bar(N, 1, STEP_4)
  for s in nodes:
    weight_s = getattr(nodes[s], weight)
    if have_locations: location_s = getattr(nodes[s], location)

    sum_weights += weight_s

    # Initialize reach (weighted and unweighted) computation for |s| (normalization)
    reach_s = -1
    weighted_reach_s = -weight_s

    # Initialize measures
    if compute_g: gravity_s = 0.0
    if compute_b: 
      P = {s: []} # Predecessors
      S = [] # Stack containing nodes in the order they are extended
      sigma = {s: 1.0} # Number of shortest paths from |s| to other nodes
      delta = {} # Dependency of |s| on other nodes
    if compute_c: d_sum_s = 0.0
    if compute_s: straightness_s = 0.0
    if have_accumulations:
      empty_accumulations = lambda: dict((field, 0.0) for field in accumulator_fields)
      accumulations_s = {s: empty_accumulations()}

    d = {s: 0.0} # Shortest distance from |s| to other nodes
    Q = [(0.0, s)] # Queue for Dijkstra

    # Dijkstra
    while Q:
      # Pop the closest node to |s| from |Q|
      d_sv, v = heapq.heappop(Q)
      weight_v = getattr(nodes[v], weight)
      if have_locations: location_v = getattr(nodes[v], location)

      reach_s += 1
      weighted_reach_s += weight_v

      if d_sv > 0:
        if compute_g: gravity_s += weight_v / exp(d_sv * beta)
        if compute_c: d_sum_s += weight_v * d_sv
        if compute_s: straightness_s += weight_v * dist(location_s, location_v) / d_sv
      if compute_b: S.append(v)

      for w, d_vw, accumulations_vw in nodes[v].neighbors:
        # s ~ ... ~ v ~ w
        d_sw = d_sv + d_vw

        if compute_b: b_refresh = False

        if not w in d: # Found a path from |s| to |w| for the first time
          if d_sw <= radius:
            heapq.heappush(Q, (d_sw, w)) # Add w to |Q|
            if have_accumulations:
              accumulations_s[w] = merge_maps(accumulations_s[v], dict(accumulations_vw), add)
          d[w] = d_sw
          if compute_b: b_refresh = True

        elif lt_TOL(d_sw, d[w]): # Found a better path from |s| to |w|
          if d_sw <= radius:
            if d[w] <= radius:
              Q.remove((d[w], w))
              heapq.heapify(Q)
            heapq.heappush(Q, (d_sw, w)) # Add w to |Q|
            if have_accumulations:
              accumulations_s[w] = merge_maps(accumulations_s[v], dict(accumulations_vw), add)
          d[w] = d_sw
          if compute_b: b_refresh = True

        if compute_b:
          if b_refresh:
            sigma[w] = 0.0
            P[w] = []
          if eq_TOL(d_sw, d[w]): # Count all shortest paths from |s| to |w|
            sigma[w] += sigma[v] # Update the number of shortest paths
            P[w].append(v) # |v| is a predecessor of |w|
            delta[v] = 0.0 # Recognize |v| as a predecessor

    if compute_r: setattr(nodes[s], reach, weighted_reach_s)
    if compute_g: setattr(nodes[s], gravity, gravity_s)
    if compute_b:
      while S: # Revisit nodes in reverse order of distance from |s|
        w = S.pop()
        delta_w = delta[w] if w in delta else 0.0 # Dependency of |s| on |w|
        for v in P[w]:
          delta[v] += sigma[v] / sigma[w] * (1 + delta_w)
        if w != s:
          between_w = getattr(w, betweenness)
          setattr(nodes[w], betweenness, between_w + delta_w * weight_s)
    if compute_c: setattr(nodes[s], closeness, 1 / d_sum_s if d_sum_s > 0 else 0.0)
    if compute_s: setattr(nodes[s], straightness, straightness_s)

    nodes[s].reach = reach_s
    nodes[s].weighted_reach = weighted_reach_s

    if have_accumulations:
      total_accumulations_s = empty_accumulations()
      for v in accumulations_s:
        total_accumulations_s = merge_maps(total_accumulations_s, accumulations_s[v], add)
      for field in accumulator_fields:
        setattr(nodes[s], field, total_accumulations_s[field])

    progress.step() # |s| is completed, move to next node

  # Normalization
  if measures_to_normalize:
    norm_progress = Progress_Bar(N, 1, "Normalizing results")
    for s in nodes:
      reach_s = getattr(nodes[s], "reach")
      weighted_reach_s = getattr(nodes[s], "weighted_reach")

      # Normalize reach
      if compute_r and reach in measures_to_normalize:
        weight_s = getattr(nodes[s], weight)
        try: setattr(nodes[s], norm_reach, (reach_s + weight_s) / sum_weights
        except: setattr(nodes[s], reach_norm, 0.0)

      # Normalize gravity
      if compute_g and gravity in measures_to_normalize:
        gravity_s = getattr(nodes[s], gravity)
        try: setattr(nodes[s], norm_gravity, gravity_s / weighted_reach_s)
        except: setattr(nodes[s], norm_gravity, 0.0)

      # Normalize betweenness
      if compute_b and betweenness in measures_to_normalize:
        betweenness_s = getattr(nodes[s], betweenness)
        try: setattr(nodes[s], norm_betweenness, betweenness_s / (weighted_reach_s * (reach_s - 1)))
        except: setattr(nodes[s], norm_betweenness, 0.0)

      # Normalize closeness
      if compute_c and closeness in measures_to_normalize:
        closeness_s = getattr(nodes[s], closeness)
        try: setattr(nodes[s], norm_closeness, closeness_s * weighted_reach_s)
        except: setattr(nodes[s], norm_closeness, 0.0)

      # Normalize straightness
      if compute_s and straightness in measures_to_normalize:
        straightness_s = getattr(nodes[s], straightness)
        try: setattr(nodes[s], norm_straightness, straightness_s / weighted_reach_s)
        except: setattr(nodes[s], norm_straightness, 0.0)

      norm_progress.step()
