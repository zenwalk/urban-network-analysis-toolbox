# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

from sys import maxint

"""
The six steps of the tool
"""
STEP_1 = "Computing adjacency list"
STEP_2 = "Building graph from adjacency list"
STEP_3 = "Retrieving necessary node attributes"
STEP_4 = "Running centrality computation"
STEP_5 = "Writing out results"
STEP_6 = "Displaying results"

"""
Constants for adjacency list computation
"""
# High cost assigned to buildings to stop neighbor search when a building is encountered
BARRIER_COST = maxint * float(2) / 5
# Maximum extent of search on the network
SEARCH_TOLERANCE = "5000 Meters"
# Distance offset when buildings are snapped to the network
SNAP_OFFSET = "5 Meters"
# File names
Auxiliary_Dir_Name = "Auxiliary_Files"
OD_Cost_Matrix_Layer_Name = "OD_Cost_Matrix_Layer"
Partial_Adjacency_List_Name = "Partial_Adjacency_List"
Polygons_Shapefile = "Polygons.shp"
Polygons_Layer_Name = "Polygons_Layer"
Raster_Name = "Raster"
Input_Points_Layer_Name = "Input_Points_Layer"

"""
Representation for an infinite radius (or infinite extent on the network)
"""
INFINITE_RADIUS = maxint

"""
Tolerance on inequality (if ||a - b|| < |TOLERANCE|, we consider a and b equal)
"""
TOLERANCE = 0.000001
