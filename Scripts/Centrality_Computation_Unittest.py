# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

##########
import sys
arcpy_needs = ['C:\\Windows\\system32\\python26.zip', u'C:\\Program Files (x86)\\ArcGIS\\Desktop10.0\\arcpy', 'C:\\Python26\\Lib', 'C:\\Python26\\DLLs', 'C:\\Python26\\Lib\\lib-tk', 'C:\\Python26\\ArcGIS10.0\\Lib', 'C:\\Python26\\ArcGIS10.0\\DLLs', 'C:\\Python26\\ArcGIS10.0\\Lib\\lib-tk', 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.0\\Bin', 'C:\\Python26\\ArcGIS10.0', 'C:\\Python26\\ArcGIS10.0\\lib\\site-packages', 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.0\\arcpy', 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.0\\ArcToolbox\\Scripts']
for thing in arcpy_needs:
  sys.path.append(thing)
##########

from Centrality_Computation import compute_centrality
from Constants import *
from Node import Node
import unittest

def construct_graph(node_ids, edges):
  graph = {}
  for id in node_ids:
    graph[id] = Node()
  for (u, v) in edges:
    graph[u].add_neighbor(v)
    graph[v].add_neighbor(u)
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
                            [("A", "B"), ("A", "C"), ("B", "C"), ("C", "D")])
  def test_Infinite_Reach(self):
    compute_centrality(self.graph, True, False, False, False, False,
                       INFINITE_RADIUS, 1, [], [])
    assert getattr(self.graph["A"], REACH) == 3
    assert getattr(self.graph["B"], REACH) == 3
    assert getattr(self.graph["C"], REACH) == 3
    assert getattr(self.graph["D"], REACH) == 3
  def test_Degree_Reach(self):
    compute_centrality(self.graph, True, False, False, False, False,
                       1, 1, [], [])
    assert getattr(self.graph["A"], REACH) == 2
    assert getattr(self.graph["B"], REACH) == 2
    assert getattr(self.graph["C"], REACH) == 3
    assert getattr(self.graph["D"], REACH) == 1


"""
Gravity
"""

"""
Betweenness
"""

"""
Closeness
"""

"""
Straightness
"""

if __name__ == "__main__":
  unittest.main()
