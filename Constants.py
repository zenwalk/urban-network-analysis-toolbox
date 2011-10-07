# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

from sys import maxint
from Utils import trim

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
BETA = "Beta"
NORMALIZE_RESULTS = "Normalize Results"
OUTPUT_LOCATION = "Output Location"
OUTPUT_FILE_NAME = "Output File Name"
ACCUMULATOR_ATTRIBUTES = "Accumulator Attributes"

"""
Console messages
"""
PROGRESS_NORMALIZATION = "Normalizing Results"

WARNING_NO_EDGE_FEATURE = lambda input_network: input_network + " does not have edge feature"
WARNING_NO_JUNCTION_FEATURE = lambda input_network: input_network + " does not have junction feature"
WARNING_POINTS_NOT_IN_GRAPH = lambda in_graph, not_in_graph: str(not_in_graph) + " out of " + \
                              str(in_graph + not_in_graph) + " input points not recorded in graph"
WARNING_NO_NODES = "No nodes in graph"
WARNING_FAIL_TO_DISPLAY = "Layer produced but not displayed"

BARRIER_COST_PRE_PROCESSING = "Barrier cost computation pre-processing"
BARRIER_COST_COMPUTATION = "Barrier cost computation"

ADJACENCY_LIST_COMPUTED = "Adjacency list already computed on previous run"

CALCULATE_LOCATIONS_STARTED = "... [started] Calculating locations on the network"
CALCULATE_LOCATIONS_FINISHED = "... [finished]"
STEP_1_STARTED = "[1 started] " + STEP_1
STEP_1_FAILED = "[1 failed] "
STEP_1_FINISHED = "[1 finished]"
STEP_2_STARTED = "[2 started] " + STEP_2
STEP_2_FAILED = "[2 failed]"
STEP_2_FINISHED = "[2 finished]"
STEP_3_STARTED = "[3 started] " + STEP_3
STEP_3_FAILED = "[3 failed]"
STEP_3_FINISHED = "[3 finished]"
STEP_4_STARTED = "[4 started] " + STEP_4
STEP_4_FAILED = "[4 failed]"
STEP_4_FINISHED = "[4 finished]"
STEP_5_STARTED = "[5 started] " + STEP_5
STEP_5_FAILED = "[5 failed]"
STEP_5_FINISHED = "[5 finished]"
STEP_6_STARTED = "[6 started]" + STEP_6
STEP_6_FAILED = "[6 failed]"
STEP_6_FINISHED = "[6 finished]"
CLEANUP_STARTED = "... [started] Clean up"
CLEANUP_FAILED = "... [failed]"
CLEANUP_FINISHED = "... [finished]"
SUCCESS = "Successful!"
FAILURE = "Not successful"

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
layer_name = lambda base: base + "_Layer"
ADJACENCY_LIST_NAME = "Adjacency_List"
AUXILIARY_DIR_NAME = "Auxiliary_Files"
OD_COST_MATRIX_LAYER_NAME = layer_name("OD_Cost_Matrix")
POLYGONS_SHAPEFILE = "Polygons.shp"
PARTIAL_ADJACENCY_LIST_NAME = "Partial_Adjacency_List"
POLYGONS_LAYER_NAME = layer_name("Polygons")
RASTER_NAME = "Raster"
INPUT_POINTS_LAYER_NAME = layer_name("Input_Points")
OD_COST_MATRIX_LINES = "Lines"
# Origin and Destination ID names
ORIGIN_ID_FIELD_NAME = trim("OriginID")
DESTINATION_ID_FIELD_NAME = trim("DestinationID")

"""
Representation for an infinite radius (or infinite extent on the network)
"""
INFINITE_RADIUS = maxint

"""
Tolerance on inequality (if ||a - b|| < |TOLERANCE|, we consider a and b equal)
"""
TOLERANCE = 0.000001
