# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

"""
Unittest for the centrality metric computation.
"""

from Centrality_Computation import compute_centrality
from Constants import INFINITE_RADIUS
from Constants import BETWEENNESS
from Constants import CLOSENESS
from Constants import GRAVITY
from Constants import LOCATION
from Constants import REACH
from Constants import STRAIGHTNESS
from math import log
from math import sqrt
from Node import Node
import unittest
from Utils import eq_tol

def construct_graph(node_ids, edges):
  """
  Constructs a weighted, undirected graph.
  """
  graph = {}
  # Nodes
  for id in node_ids:
    graph[id] = Node()
  # Edges
  for (u, v, weight) in edges:
    graph[u].add_neighbor(v, weight)
    graph[v].add_neighbor(u, weight)
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
A
|\
| C--D
|/
B
"""
class TestCloseness(unittest.TestCase):
  def setUp(self):
    self.graph = construct_graph(["A", "B", "C", "D"],
                                 [("A", "B", 2),
                                  ("A", "C", 1),
                                  ("B", "C", 1),
                                  ("C", "D", 3)])
  def test_Closeness(self):
    compute_centrality(self.graph, False, False, False, True, False,
                       INFINITE_RADIUS, 1, [], [])
    assert eq_tol(getattr(self.graph["A"], CLOSENESS), 1.0/7)
    assert eq_tol(getattr(self.graph["B"], CLOSENESS), 1.0/7)
    assert eq_tol(getattr(self.graph["C"], CLOSENESS), 1.0/5)
    assert eq_tol(getattr(self.graph["D"], CLOSENESS), 1.0/11)

"""
Straightness
  |
 1| A
  | |\
 0| | C--D
  | |/
-1| B
   --------
   -1 0  1
"""
class TestStraightness(unittest.TestCase):
  def setUp(self):
    self.graph = construct_graph(["A", "B", "C", "D"],
                                 [("A", "B", 2),
                                  ("A", "C", sqrt(2)),
                                  ("B", "C", sqrt(2)),
                                  ("C", "D", 1)])
    setattr(self.graph["A"], LOCATION, (-1, 1))
    setattr(self.graph["B"], LOCATION, (-1, -1))
    setattr(self.graph["C"], LOCATION, (0, 0))
    setattr(self.graph["D"], LOCATION, (1, 0))
  def test_Straightness(self):
    compute_centrality(self.graph, False, False, False, False, True,
                       INFINITE_RADIUS, 1, [], [])
    assert eq_tol(getattr(self.graph["A"], STRAIGHTNESS), 2+sqrt(5)/(1+sqrt(2)))
    assert eq_tol(getattr(self.graph["B"], STRAIGHTNESS), 2+sqrt(5)/(1+sqrt(2)))
    assert eq_tol(getattr(self.graph["C"], STRAIGHTNESS), 3)
    assert eq_tol(getattr(self.graph["D"], STRAIGHTNESS), 1+2*sqrt(5)/(1+sqrt(2)))

if __name__ == "__main__":
  unittest.main()