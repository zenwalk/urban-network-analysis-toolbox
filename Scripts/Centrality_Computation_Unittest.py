# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

#### REMOVE ME ######
import sys
arcpy_needs = ['C:\\Windows\\system32\\python26.zip', u'C:\\Program Files (x86)\\ArcGIS\\Desktop10.0\\arcpy', 'C:\\Python26\\Lib', 'C:\\Python26\\DLLs', 'C:\\Python26\\Lib\\lib-tk', 'C:\\Python26\\ArcGIS10.0\\Lib', 'C:\\Python26\\ArcGIS10.0\\DLLs', 'C:\\Python26\\ArcGIS10.0\\Lib\\lib-tk', 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.0\\Bin', 'C:\\Python26\\ArcGIS10.0', 'C:\\Python26\\ArcGIS10.0\\lib\\site-packages', 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.0\\arcpy', 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.0\\ArcToolbox\\Scripts']
for thing in arcpy_needs:
  sys.path.append(thing)
#### REMOVE ME ######

from Centrality_Computation import compute_centrality
from Constants import *
from math import log
from Node import Node
import unittest
from Utils import *

def construct_graph(node_ids, edges):
  """
  Constructs a weighted, undirected graph with the given nodes and edges.
  A graph is represented by a dictionary with the node ids as keys and Node objects
    as values.
  """
  graph = {}
  # Nodes
  for id in node_ids:
    graph[id] = Node()
  # Edges
  for (u, v, dist) in edges:
    graph[u].add_neighbor(v, dist)
    graph[v].add_neighbor(u, dist)
  return graph

"""
Reach
A
|\
| C--D
|/
B
"""
class TestReach(unittest.TestCase):
  def setUp(self):
    self.graph = construct_graph(["A", "B", "C", "D"],
                                 [("A", "B", 1),
                                  ("A", "C", 1),
                                  ("B", "C", 1),
                                  ("C", "D", 1)])
  def test_Infinite_Reach(self):
    compute_centrality(self.graph, True, False, False, False, False,
                       INFINITE_RADIUS, 1, [], [])
    assert eq_tol(getattr(self.graph["A"], REACH), 3)
    assert eq_tol(getattr(self.graph["B"], REACH), 3)
    assert eq_tol(getattr(self.graph["C"], REACH), 3)
    assert eq_tol(getattr(self.graph["D"], REACH), 3)
  def test_Degree_Reach(self):
    compute_centrality(self.graph, True, False, False, False, False,
                       1, 1, [], [])
    assert eq_tol(getattr(self.graph["A"], REACH), 2)
    assert eq_tol(getattr(self.graph["B"], REACH), 2)
    assert eq_tol(getattr(self.graph["C"], REACH), 3)
    assert eq_tol(getattr(self.graph["D"], REACH), 1)

"""
Gravity
A
|\
| C--D
|/
B
"""
class TestGravity(unittest.TestCase):
  def setUp(self):
    self.graph = construct_graph(["A", "B", "C", "D"],
                                 [("A", "B", log(3)),
                                  ("A", "C", log(2)),
                                  ("B", "C", log(2)),
                                  ("C", "D", log(3))])
  def test_Gravity(self):
    # Infinite radius, beta = 1
    compute_centrality(self.graph, False, True, False, False, False,
                       INFINITE_RADIUS, 1, [], [])
    assert eq_tol(getattr(self.graph["A"], GRAVITY), 1)
    assert eq_tol(getattr(self.graph["B"], GRAVITY), 1)
    assert eq_tol(getattr(self.graph["C"], GRAVITY), 4.0/3)
    assert eq_tol(getattr(self.graph["D"], GRAVITY), 2.0/3)

"""
Betweenness
A
 \
  C--D
 /
B
"""
class TestBetweenness(unittest.TestCase):
  def setUp(self):
    self.graph = construct_graph(["A", "B", "C", "D"],
                                 [("A", "C", 1),
                                  ("B", "C", 1),
                                  ("C", "D", 1)])
  def test_Betweenness(self):
    compute_centrality(self.graph, False, False, True, False, False,
                       INFINITE_RADIUS, 1, [], [])
    assert eq_tol(getattr(self.graph["A"], BETWEENNESS), 0)
    assert eq_tol(getattr(self.graph["B"], BETWEENNESS), 0)
    assert eq_tol(getattr(self.graph["C"], BETWEENNESS), 3)
    assert eq_tol(getattr(self.graph["D"], BETWEENNESS), 0)

"""
Closeness
"""

"""
Straightness
"""

if __name__ == "__main__":
  unittest.main()
