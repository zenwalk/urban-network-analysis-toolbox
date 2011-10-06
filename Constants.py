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
Inputs to the tool
"""
INPUT_POINTS = "Input Points"
INPUT_NETWORK = "Input Network"
COMPUTE_REACH = "Compute Reach"
COMPUTE_GRAVITY = "Compute Gravity Type Index"
COMPUTE_BETWEENNESS = "Compute Betweenness"
COMPUTE_CLOSENESS = "Compute Closeness"
COMPUTE_STRAIGHTNESS = "Compute Straightness"
ID_ATTRIBUTE = "ID Attribute Name"
NODE_WEIGHT_ATTRIBUTE = "Node Weight Attribute Name"
IMPEDANCE_ATTRIBUTE = "Impedance Attribute Name"
SEARCH_RADIUS = "Search Radius"
MAX_NEIGHBOR_SEPARATION = "Maximum Neighbor Separation"
BETA = "beta"
NORMALIZE_RESULTS = "Normalize Results"
OUTPUT_LOCATION = "Output Location"
OUTPUT_FILE_NAME = "Output File Name"
ACCUMULATOR_ATTRIBUTES = "Accumulators"

"""
Console messages
"""
PROGRESS_NORMALIZATION = "Normalizing Results"
WARNING_NO_EDGE_FEATURE = lambda input_network: input_network + " does not have edge feature"
WARNING_NO_JUNCTION_FEATURE = lambda input_network: input_network + " does not have junction feature"
START_CALCULATE_LOCATIONS = "... [started] Calculating locations on the network"
FINISH_CALCULATE_LOCATIONS = "... [finished]"
BARRIER_COST_PRE_PROCESSING = "Barrier cost computation pre-processing"
BARRIER_COST_COMPUTATION = "Barrier cost computation"

"""
Node attribute names
"""
LOCATION = "location"
WEIGHT = "weight"
REACH = "reach"
NORM_REACH = "norm_reach"
GRAVITY = "gravity_type_index"
NORM_GRAVITY = "norm_gravity_type_index"
BETWEENNESS = "betweenness"
NORM_BETWEENNESS = "norm_betweenness"
CLOSENESS = "closeness"
NORM_CLOSENESS = "norm_closeness"
STRAIGHTNESS = "straightness"
NORM_STRAIGHTNESS = "norm_straightness"

"""
Constants for adjacency list computation
"""
# Network feature type identifiers
EDGE_FEATURE = "EdgeFeature"
JUNCTION_FEATURE = ("JunctionFeature", "SystemJunction")
# Network location field names
NETWORK_LOCATION_FIELDS = ("SourceID", "SourceOID", "PosAlong", "SideOfEdge", "SnapX", "SnapY", "Distance")
# Number of input points per raster cell
POINTS_PER_RASTER_CELL = 500
# High cost assigned to buildings to stop neighbor search when a building is encountered
BARRIER_COST_FIELD = "Barrier_Cost"
BARRIER_COST = maxint * float(2) / 5
# Maximum extent of search on the network
SEARCH_TOLERANCE = "5000 Meters"
# Distance offset when buildings are snapped to the network
SNAP_OFFSET = "5 Meters"
# File names
AUXILIARY_DIR_NAME = "Auxiliary_Files"
OD_COST_MATRIX_LAYER_NAME = "OD_Cost_Matrix_Layer"
POLYGONS_SHAPEFILE = "Polygons.shp"
PARTIAL_ADJACENCY_LIST_NAME = "Partial_Adjacency_List"
PARTIAL_ADJACENCY_LIST_NAME = "Partial_Adjacency_List"
POLYGONS_LAYER_NAME = "Polygons_Layer"
RASTER_NAME = "Raster"
INPUT_POINTS_LAYER_NAME = "Input_Points_Layer"
OD_COST_MATRIX_LINES = "Lines"

"""
Representation for an infinite radius (or infinite extent on the network)
"""
INFINITE_RADIUS = maxint

"""
Tolerance on inequality (if ||a - b|| < |TOLERANCE|, we consider a and b equal)
"""
TOLERANCE = 0.000001
