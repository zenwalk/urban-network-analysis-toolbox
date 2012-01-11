# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

from Adjacency_List_Computation import compute_adjacency_list
import arcpy
import arcgisscripting
from Centrality_Computation import compute_centrality
from Constants import ACCUMULATOR_ATTRIBUTES
from Constants import ADJACENCY_LIST_COMPUTED
from Constants import ADJACENCY_LIST_NAME
from Constants import AUXILIARY_DIR_NAME
from Constants import BETA
from Constants import COMPUTE_BETWEENNESS
from Constants import COMPUTE_CLOSENESS
from Constants import COMPUTE_GRAVITY
from Constants import COMPUTE_REACH
from Constants import COMPUTE_STRAIGHTNESS
from Constants import DESTINATION_ID_FIELD_NAME
from Constants import FAILURE
from Constants import FINAL_ATTRIBUTES
from Constants import ID_ATTRIBUTE
from Constants import IMPEDANCE_ATTRIBUTE
from Constants import INFINITE_RADIUS
from Constants import INPUT_BUILDINGS
from Constants import INPUT_COUNT
from Constants import INPUT_NETWORK
from Constants import INPUT_POINTS
from Constants import INPUT_POINTS_LAYER_NAME
from Constants import layer_name
from Constants import LOCATION
from Constants import MAX_NEIGHBOR_SEPARATION
from Constants import NODE_WEIGHT_ATTRIBUTE
from Constants import NORMALIZE_RESULTS
from Constants import OD_COST_MATRIX_LAYER_NAME
from Constants import OD_COST_MATRIX_LINES
from Constants import ORIGIN_ID_FIELD_NAME
from Constants import ORIGINAL_FID
from Constants import OUTPUT_FILE_NAME
from Constants import OUTPUT_LOCATION
from Constants import PARTIAL_ADJACENCY_LIST_NAME
from Constants import POINT_CONVERSION_FINISHED
from Constants import POINT_CONVERSION_STARTED
from Constants import POINT_FEATURE_CLASS_NAME
from Constants import POINT_LOCATION
from Constants import POLYGONS_LAYER_NAME
from Constants import POLYGONS_SHAPEFILE_NAME
from Constants import RASTER_NAME
from Constants import SEARCH_RADIUS
from Constants import STEP_1_FAILED
from Constants import STEP_1_FINISHED
from Constants import STEP_1_STARTED
from Constants import STEP_2
from Constants import STEP_2_FAILED
from Constants import STEP_2_FINISHED
from Constants import STEP_2_STARTED
from Constants import STEP_3
from Constants import STEP_3_FAILED
from Constants import STEP_3_FINISHED
from Constants import STEP_3_STARTED
from Constants import STEP_4_FAILED
from Constants import STEP_4_FINISHED
from Constants import STEP_4_STARTED
from Constants import STEP_5
from Constants import STEP_5_FAILED
from Constants import STEP_5_FINISHED
from Constants import STEP_5_STARTED
from Constants import STEP_6_FAILED
from Constants import STEP_6_FINISHED
from Constants import STEP_6_STARTED
from Constants import SUCCESS
from Constants import UNA_ID
from Constants import WARNING_FAIL_TO_DISPLAY
from Constants import WARNING_NO_NODES
from Constants import WARNING_OUTPUT_ALREADY_EXISTS
from Constants import WARNING_POINTS_NOT_IN_GRAPH
from Constants import WEIGHT
from Node import Node
from os.path import join
from sys import argv
from Utils import basename
from Utils import delete
from Utils import Invalid_Input_Exception
from Utils import is_accumulator_field
from Utils import Progress_Bar
from Utils import to_point_feature_class
from Utils import trim

arcpy.env.overwriteOutput = True # Enable overwritting
arcpy.CheckOutExtension("Network")

# Success of the program through the six steps
success = True

# Inputs to the tool
if len(argv) != INPUT_COUNT + 1:
  raise Exception("Invalid number of inputs")
def index():
  i = 1
  while True:
    yield i
    i += 1
input_number = index()
inputs = {}
inputs[INPUT_BUILDINGS] = argv[input_number.next()]
inputs[POINT_LOCATION] = "INSIDE" if argv[input_number.next()] == "true" else "CENTROID"
inputs[INPUT_NETWORK] = argv[input_number.next()]
inputs[COMPUTE_REACH] = argv[input_number.next()] == "true"
inputs[COMPUTE_GRAVITY] = argv[input_number.next()] == "true"
inputs[COMPUTE_BETWEENNESS] = argv[input_number.next()] == "true"
inputs[COMPUTE_CLOSENESS] = argv[input_number.next()] == "true"
inputs[COMPUTE_STRAIGHTNESS] = argv[input_number.next()] == "true"
inputs[ID_ATTRIBUTE] = argv[input_number.next()]
inputs[NODE_WEIGHT_ATTRIBUTE] = argv[input_number.next()]
inputs[IMPEDANCE_ATTRIBUTE] = argv[input_number.next()]
try: inputs[SEARCH_RADIUS] = float(argv[input_number.next()])
except: inputs[SEARCH_RADIUS] = INFINITE_RADIUS
inputs[MAX_NEIGHBOR_SEPARATION] = argv[input_number.next()]
try: inputs[BETA] = float(argv[input_number.next()])
except: raise Invalid_Input_Exception("Beta")
inputs[NORMALIZE_RESULTS] = [measure
                             for measure in argv[input_number.next()].split(";")
                             if measure != "#"]
inputs[OUTPUT_LOCATION] = argv[input_number.next()]
inputs[OUTPUT_FILE_NAME] = argv[input_number.next()]
inputs[ACCUMULATOR_ATTRIBUTES] = argv[input_number.next()]

# We will convert input buildings to point feature class
buildings_description = arcpy.Describe(inputs[INPUT_BUILDINGS])
if buildings_description.shapeType == "Point":
  # Input buildings are already a point shape file
  inputs[INPUT_POINTS] = inputs[INPUT_BUILDINGS]
elif buildings_description.shapeType == "Polygon":
  # Input buildings need to be converted to point feature class
  point_feature_class_name = POINT_FEATURE_CLASS_NAME(basename(inputs[INPUT_BUILDINGS]),
                                                      inputs[POINT_LOCATION])
  inputs[INPUT_POINTS] = "%s.shp" % join(inputs[OUTPUT_LOCATION],
                                         point_feature_class_name)
  # If FID is used as ID attribute, we need to change it since a new shapefile will be in use
  if inputs[ID_ATTRIBUTE] == "FID":
    inputs[ID_ATTRIBUTE] = ORIGINAL_FID
else:
  # Input buildings need to be either points or polygons
  raise Invalid_Input_Exception("Input Buildings")

# Output files
output_dbf_name = "%s.dbf" % inputs[OUTPUT_FILE_NAME]
output_dbf = join(inputs[OUTPUT_LOCATION], output_dbf_name)
output_layer = layer_name(inputs[OUTPUT_FILE_NAME])
# If output has already been created, don't carry on
if arcpy.Exists(output_dbf) or arcpy.Exists(output_layer):
  arcpy.AddWarning(WARNING_OUTPUT_ALREADY_EXISTS)
  success = False
# Adjacency List table
adj_dbf_name = ("%s_%s_%s_%s_%s_%s_%s.dbf" %
                (ADJACENCY_LIST_NAME,
                 basename(inputs[INPUT_POINTS]),
                 basename(inputs[INPUT_NETWORK]),
                 inputs[ID_ATTRIBUTE],
                 inputs[IMPEDANCE_ATTRIBUTE],
                 inputs[ACCUMULATOR_ATTRIBUTES],
                 inputs[MAX_NEIGHBOR_SEPARATION]))
adj_dbf = join(inputs[OUTPUT_LOCATION], adj_dbf_name)

def clean_up():
  """
  Removes all auxiliary files
  """
  auxiliary_dir = join(inputs[OUTPUT_LOCATION], AUXILIARY_DIR_NAME)
  od_cost_matrix_layer = join(auxiliary_dir, OD_COST_MATRIX_LAYER_NAME)
  od_cost_matrix_lines = join(auxiliary_dir, OD_COST_MATRIX_LINES)
  temp_adj_dbf_name = "%s~.dbf" % adj_dbf_name[-4]
  temp_adj_dbf = join(inputs[OUTPUT_LOCATION], temp_adj_dbf_name)
  partial_adj_dbf = join(auxiliary_dir, PARTIAL_ADJACENCY_LIST_NAME)
  polygons = join(auxiliary_dir, POLYGONS_SHAPEFILE_NAME)
  raster = join(auxiliary_dir, RASTER_NAME)
  polygons_layer = join(auxiliary_dir, POLYGONS_LAYER_NAME)
  input_points_layer = join(auxiliary_dir, INPUT_POINTS_LAYER_NAME)
  for path in [input_points_layer,
               polygons_layer,
               raster,
               polygons,
               partial_adj_dbf,
               temp_adj_dbf,
               od_cost_matrix_lines,
               od_cost_matrix_layer,
               auxiliary_dir]:
    delete(path)

try:
  """
  Here we carry out the six steps of the tool
  """

  # Step 1
  if success:
    arcpy.AddMessage(STEP_1_STARTED)
    # If necessary, convert input buildings to point feature class
    if buildings_description.shapeType == "Polygon":
      arcpy.AddMessage(POINT_CONVERSION_STARTED)
      to_point_feature_class(inputs[INPUT_BUILDINGS],
                             inputs[INPUT_POINTS],
                             inputs[POINT_LOCATION])
      arcpy.AddMessage(POINT_CONVERSION_FINISHED)
    if arcpy.Exists(adj_dbf):
      arcpy.AddMessage(ADJACENCY_LIST_COMPUTED)
      arcpy.AddMessage(STEP_1_FINISHED)
    else:
      try:
        compute_adjacency_list(inputs[INPUT_POINTS],
                               inputs[INPUT_NETWORK],
                               inputs[ID_ATTRIBUTE],
                               inputs[IMPEDANCE_ATTRIBUTE],
                               inputs[ACCUMULATOR_ATTRIBUTES],
                               inputs[SEARCH_RADIUS],
                               inputs[MAX_NEIGHBOR_SEPARATION],
                               inputs[OUTPUT_LOCATION],
                               adj_dbf_name)
        arcpy.AddMessage(STEP_1_FINISHED)
      except:
        arcpy.AddWarning(arcpy.GetMessages(2))
        arcpy.AddMessage(STEP_1_FAILED)
        success = False

  # Step 2
  if success:
    arcpy.AddMessage(STEP_2_STARTED)
    try:
      distance_field = trim("Total_%s" % inputs[IMPEDANCE_ATTRIBUTE])
      accumulator_fields = set([trim("Total_%s" % accumulator_attribute)
                                for accumulator_attribute in inputs[ACCUMULATOR_ATTRIBUTES].split(";")
                                if accumulator_attribute != "#"])

      # Create graph representation: a dictionary mapping node id's to Node objects
      nodes = {}

      directed_edge_count = int(arcpy.GetCount_management(adj_dbf).getOutput(0)) # The number of rows in |adj_dbf|
      graph_progress = Progress_Bar(directed_edge_count, 1, STEP_2)
      rows = arcpy.UpdateCursor(adj_dbf)
      for row in rows:
        # Get neighboring nodes, and the distance between them
        origin_id = row.getValue(trim(ORIGIN_ID_FIELD_NAME))
        destination_id = row.getValue(trim(DESTINATION_ID_FIELD_NAME))
        distance = float(row.getValue(distance_field))

        # Make sure the nodes are recorded in the graph
        for id in [origin_id, destination_id]:
          if not id in nodes:
            nodes[id] = Node()

        # Make sure that the nodes are neighbors in the graph
        if origin_id != destination_id and distance >= 0:
          accumulations = {}
          for field in accumulator_fields:
            accumulations[field] = float(row.getValue(field))
          nodes[origin_id].add_neighbor(destination_id, distance, accumulations)
          nodes[destination_id].add_neighbor(origin_id, distance, accumulations)

        graph_progress.step()

      N = len(nodes) # The number of nodes in the graph
      if N == 0:
        arcpy.AddWarning(WARNING_NO_NODES)
        success = False
      arcpy.AddMessage(STEP_2_FINISHED)
    except:
      arcpy.AddWarning(arcpy.GetMessages(2))
      arcpy.AddMessage(STEP_2_FAILED)
      success = False

  # Step 3
  if success:
    arcpy.AddMessage(STEP_3_STARTED)
    try:
      get_weights = inputs[NODE_WEIGHT_ATTRIBUTE] != "#"
      get_locations = inputs[COMPUTE_STRAIGHTNESS]

      # Keep track of number nodes in |input_points| not present in the graph
      point_not_in_graph_count = 0

      input_point_count = int(arcpy.GetCount_management(inputs[INPUT_POINTS]).getOutput(0))
      node_attribute_progress = Progress_Bar(input_point_count, 1, STEP_3)
      rows = arcpy.UpdateCursor(inputs[INPUT_POINTS])
      for row in rows:
        id = row.getValue(inputs[ID_ATTRIBUTE])

        if not id in nodes:
          point_not_in_graph_count += 1
          continue

        if get_weights:
          setattr(nodes[id], WEIGHT, row.getValue(trim(inputs[NODE_WEIGHT_ATTRIBUTE])))

        if get_locations:
          snap_x = row.getValue(trim("SnapX"))
          snap_y = row.getValue(trim("SnapY"))
          setattr(nodes[id], LOCATION, (snap_x, snap_y))

        node_attribute_progress.step()

      if point_not_in_graph_count:
        arcpy.AddWarning(WARNING_POINTS_NOT_IN_GRAPH(N, point_not_in_graph_count))

      arcpy.AddMessage(STEP_3_FINISHED)
    except:
      arcpy.AddWarning(arcpy.GetMessages(2))
      arcpy.AddMessage(STEP_3_FAILED)
      success = False

  # Step 4
  if success:
    arcpy.AddMessage(STEP_4_STARTED)
    try:
      # Compute measures
      compute_centrality(nodes,
                         inputs[COMPUTE_REACH],
                         inputs[COMPUTE_GRAVITY],
                         inputs[COMPUTE_BETWEENNESS],
                         inputs[COMPUTE_CLOSENESS],
                         inputs[COMPUTE_STRAIGHTNESS],
                         inputs[SEARCH_RADIUS],
                         inputs[BETA],
                         inputs[NORMALIZE_RESULTS],
                         accumulator_fields)
      arcpy.AddMessage(STEP_4_FINISHED)
    except:
      arcpy.AddWarning(arcpy.GetMessages(2))
      arcpy.AddMessage(STEP_4_FAILED)
      success = False

  # Step 5
  if success:
    arcpy.AddMessage(STEP_5_STARTED)
    try:
      arcpy.CreateTable_management(out_path=inputs[OUTPUT_LOCATION],
                                   out_name=output_dbf_name)

      arcpy.AddField_management(in_table=output_dbf,
                                field_name=UNA_ID,
                                field_type="TEXT",
                                field_is_nullable="NON_NULLABLE")

      test_node = nodes.values()[0]
      measures = set([measure for measure in dir(test_node) \
                      if measure in FINAL_ATTRIBUTES or is_accumulator_field(measure)])

      for measure in measures:
        arcpy.AddField_management(in_table=output_dbf,
                                  field_name=trim(measure),
                                  field_type="DOUBLE",
                                  field_is_nullable="NON_NULLABLE")

      write_progress = Progress_Bar(N, 1, STEP_5)
      rows = arcpy.InsertCursor(output_dbf)
      for id in nodes:
        row = rows.newRow()
        row.setValue(UNA_ID, str(id))
        for measure in measures:
          row.setValue(trim(measure), getattr(nodes[id], measure))
        rows.insertRow(row)
        write_progress.step()

      arcpy.AddMessage(STEP_5_FINISHED)
    except:
      arcpy.AddWarning(arcpy.GetMessages(2))
      arcpy.AddMessage(STEP_5_FAILED)
      success = False

  # Step 6
  if success:
    arcpy.AddMessage(STEP_6_STARTED)
    try:
      arcpy.MakeFeatureLayer_management(in_features=inputs[INPUT_BUILDINGS],
                                        out_layer=output_layer)
      # Join |output_dbf| with |output_layer|
      if buildings_description.shapeType == "Polygon" and inputs[ID_ATTRIBUTE] == ORIGINAL_FID:
        in_field = "FID" 
      else:
        in_field = inputs[ID_ATTRIBUTE]
      join_field = UNA_ID
      arcpy.AddJoin_management(output_layer, in_field,
                               output_dbf, join_field)

      # Save
      layer = "%s.lyr" % join(inputs[OUTPUT_LOCATION], output_layer)
      arcpy.SaveToLayerFile_management(output_layer, layer, "ABSOLUTE")
    except:
      arcpy.AddWarning(arcpy.GetMessages(2))
      arcpy.AddMessage(STEP_6_FAILED)
      success = False

    # Display
    if success:
      try:
        current_map_document = arcpy.mapping.MapDocument("CURRENT")
        data_frame = arcpy.mapping.ListDataFrames(current_map_document, "Layers")[0]
        add_layer = arcpy.mapping.Layer(layer)
        arcpy.mapping.AddLayer(data_frame, add_layer, "AUTO_ARRANGE")
        arcpy.AddMessage(STEP_6_FINISHED)
      except:
        arcpy.AddWarning(WARNING_FAIL_TO_DISPLAY)
        arcpy.AddWarning(arcpy.GetMessages(2))
        arcpy.AddMessage(STEP_6_FAILED)

  # Clean up
  clean_up()

  if success: arcpy.AddMessage(SUCCESS)
  else: arcpy.AddMessage(FAILURE)

except arcgisscripting.ExecuteAbort:
  clean_up()
