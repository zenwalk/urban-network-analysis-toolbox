# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

from Constants import weight_attribute

"""
Representation for a node in a graph
A graph is represented by a dictionary mapping node id's to Node objects
"""
class Node:
  def __init__(self):
    # The node's neighboring nodes
    self.neighbor_ids = set()
    self.neighbors = []
    # The weight of the node, defaults to 1.0 but can be changed
    setattr(self, weight_attribute, 1.0)

    """
    Add a neighbor to this node
    |neighbor_id|: id of the neighboring node
    |edge_weight|: weight of the edge connecting the two nodes
    |accumulation_weights|: the weight of the edge based on other metrics
    """
    def add_neighbor(self, neighbor_id, edge_weight=1.0, accumulation_weights={}):
      if not neighbor_id in self.neighbor_ids:
        self.neighbor_ids.add(neighbor_id)
        self.neighbors.append((neighbor_id,
                               edge_weight,
                               tuple(accumulation_weights.items())))
