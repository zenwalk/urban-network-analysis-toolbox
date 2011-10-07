# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

import arcpy
from Centrality_Computation import compute_centrality
from Adjacency_List_Computation import compute_adjacency_list
from Constants import *
from Utils import *
from math import ceil
from Node import Node
from sys import argv
from os.path import join

arcpy.env.overwriteOutput = True # Enable overwritting
arcpy.CheckOutExtension("Network")

# Success of the program through the 6 steps
success = True

# Inputs
if len(argv) != 17:
  raise Exception("Invalid number of inputs")
inputs = {}
inputs[INPUT_POINTS] = argv[1]
inputs[INPUT_NETWORK] = argv[2]
inputs[COMPUTE_REACH] = argv[3] == "true"
inputs[COMPUTE_GRAVITY] = argv[4] == "true"
inputs[COMPUTE_BETWEENNESS] = argv[5] == "true"
inputs[COMPUTE_CLOSENESS] = argv[6] == "true"
inputs[COMPUTE_STRAIGHTNESS] = argv[7] == "true"
inputs[ID_ATTRIBUTE] = argv[8]
inputs[NODE_WEIGHT_ATTRIBUTE] = argv[9]
inputs[IMPEDANCE_ATTRIBUTE] = argv[10]
try: inputs[SEARCH_RADIUS] = float(argv[11])
except: inputs[SEARCH_RADIUS] = INFINITE_RADIUS
inputs[MAX_NEIGHBOR_SEPARATION] = argv[12]
try: inputs[BETA] = float(argv[13])
except: raise Invalid_Input_Exception(BETA)
inputs[NORMALIZE_RESULTS] = [measure for measure in argv[14].split(";") if measure != "#"]
inputs[OUTPUT_LOCATION] = argv[15]
inputs[OUTPUT_FILE_NAME] = argv[16]
inputs[ACCUMULATOR_ATTRIBUTES] = argv[17]

if any(inputs[COMPUTE_REACH],
       inputs[COMPUTE_GRAVITY],
       inputs[COMPUTE_BETWEENNESS],
       inputs[COMPUTE_CLOSENESS],
       inputs[COMPUTE_STRAIGHTNESS]): # Computing any measure?

  # Step 1
  if success:
    arcpy.AddMessage(STEP_1_STARTED)
    adj_file_name = ADJACENCY_LIST_NAME + "_" + \
                    arcpy.Describe(inputs[INPUT_POINTS]).baseName + "_" + \
                    arcpy.Describe(inputs[INPUT_NETWORK]).baseName + "_" + \
                    inputs[ID_ATTRIBUTE] + "_" + \
                    inputs[IMPEDANCE_ATTRIBUTE] + "_" + \
                    inputs[ACCUMULATOR_ATTRIBUTES] + "_" + \
                    inputs[MAX_NEIGHBOR_SEPARATION] + \
                    ".dbf"
    adj_file = join(output_location, adj_file_name)

    if arcpy.Exists(adj_file):
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
                               adj_file_name)
        arcpy.AddMessage(STEP_1_FINISHED)
      except:
        arcpy.AddWarning(arcpy.GetMessages(2))
        arcpy.AddMessage(STEP_1_FAILED)
        success = False

  # Step 2
  if success:
    arcpy.AddMessage(STEP_2_STARTED)
    try:
      distance_field = trim("Total_" + inputs[IMPEDANCE_ATTRIBUTE])
      accumulator_fields = set([trim("Total_" + accumulator_attribute) \
                                for accumulator_attribute in inputs[ACCUMULATOR_ATTRIBUTES] \
                                if accumulator_attribute != "#"])
      
      # Create graph representation: a dictionary mapping node id's to Node objects
      nodes = {}

      directed_edge_count = arcpy.GetCount_management(adj_file) # The number of rows in |adj_file|
      graph_progress = Progress_Bar(directed_edge_count, 1, STEP_2)
      rows = arcpy.UpdateCursor(adj_file)
      for row in rows:
        # Get neighboring nodes, and the distance between them
        origin_id = row.getValue(ORIGIN_ID_FIELD_NAME)
        destination_id = row.getValue(DESTINATION_ID_FIELD_NAME)
        distance = float(row.getValue(distance_field)) - 2 * BARRIER_COST

        # Make sure the nodes are recorded in the graph
        for id in [origin_id, destination_id]:
          if not id in nodes:
            nodes[id] = Node()

        # Make sure that the nodes are neighbors in the graph
        if origin_id != destination_id and distance >= 0:
          accumulations = {}
          for accumulation_attribute in inputs[ACCUMULATOR_ATTRIBUTES]:
            accumulations[accumulation_attribute] = float(row.getValue(trim(accumulation_attribute)))
          nodes[origin_id].add_neighbor(destination, distance, accumulations)
          nodes[destination_id].add_neighbor(origin, distance, accumulations)

        graph_progress.step()

      N = len(nodes) # The number of nodes in the graph
      if N === 0:
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

      input_point_count = arcpy.GetCount_management(inputs[INPUT_POINTS])
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
                         inputs[ACCUMULATOR_ATTRIBUTES])
      arcpy.AddMessage(STEP_4_FINISHED)
    except:
      arcpy.AddWarning(arcpy.GetMessages(2))
      arcpy.AddMessage(STEP_4_FAILED)
      success = False

  # Step 5
  if success:
    arcpy.AddMessage(STEP_5_STARTED)
    try:
      output_dbf_name = inputs[OUTPUT_FILE_NAME] + ".dbf"
      output_dbf = join(inputs[OUTPUT_LOCATION], output_dbf_name)
      if arcpy.Exists(output_dbf):
        arcpy.Delete_management(output_dbf)
      arcpy.CreateTabele_management(out_path=inputs[OUTPUT_LOCATION],
                                    out_name=output_dbf_name)

      if inputs[ID_ATTRIBUTE] != "FID":
        arcpy.AddField_management(in_table=output_dbf,
                                  field_name=trim(inputs[ID_ATTRIBUTE]),
                                  field_type="TEXT",
                                  field_is_nullable="NON_NULLABLE")

      test_node = nodes.values()[0]
      measures = set([measure for measure in dir(test_node) \
                      if not measure.startswith("__") and not measure.endswith("__")])
      for measure in measures:
        arcpy.AddField_management(in_table=output_dbf,
                                  field_name=trim(measure),
                                  field_type="DOUBLE",
                                  field_is_nullable="NON_NULLABLE")

      write_progress = Progress_Bar(N, 1, STEP_5)
      rows = arcpy.InsertCursor(output_dbf)
      for id in nodes:
        row = rows.newRow()
        if inputs[ID_ATTRIBUTE] != "FID":
          row.setValue(trim(inputs[ID_ATTRIBUTE]), str(id))
        for measure in measures:
          row.setValue(measure, getattr(nodes[id], measure))
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
      output_layer = layer_name(output_file_name[-4])
      arcpy.MakeFeatureLayer_management(in_features=inputs[INPUT_POINTS],
                                        out_layer=output_layer)
      # Join |output_dbf| with |output_layer|
      in_field = inputs[ID_ATTRIBUTE]
      join_field = "OID" if in_field = "FID" else inputs[ID_ATTRIBUTE]
      arcpy.AddJoin_management(output_layer, in_field,
                               output_dbf, join_field)

      # Save
      layer = join(inputs[OUTPUT_LOCATION], output_layer) + ".lyr"
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
arcpy.AddMessage(CLEANUP_STARTED)
try:
  auxiliary_dir = join(inputs[OUTPUT_LOCATION], AUXILIARY_DIR_NAME)
  od_cost_matrix_layer = join(auxiliary_dir, OD_COST_MATRIX_LAYER_NAME)
  od_cost_matrix_lines = join(auxiliary_dir, OD_COST_MATRIX_LINES)
  temp_adj_dbf_name = adj_dbf_name[-4] + "%.dbf"
  temp_adj_dbf = join(inputs[OUTPUT_LOCATION], temp_adj_dbf_name)
  partial_adj_dbf = join(auxiliary_dir, PARTIAL_ADJACENCY_LIST_NAME)
  polygons = join(auxiliary_dir, POLYGONS_SHAPEFILE_NAME)
  raster = join(auxiliary_dir, RASTER_NAME)
  polygons_layer = join(auxiliary_dir, POLYGONS_LAYER_NAME)
  input_points_layer = join(auxiliary_dir, INPUT_POINTS_LAYER_NAME)

  for file in [input_points_layer,
               polygons_layer,
               raster,
               polygons,
               partial_adj_dbf,
               temp_adj_dbf,
               od_cost_matrix_lines,
               od_cost_matrix_layer,
               auxiliary_dir]:
    if arcpy.Exists(file):
      arcpy.Delete_management(file)
  arcpy.AddMessage(CLEANUP_FINISHED) 
except:
  arcpy.AddWarning(arcpy.GetMessages(2))
  arcpy.AddMessage(CLEAN_UP_FAILED)
  success = False

if success: arcpy.AddMessage(SUCCESS)
else: arcpy.AddMessage(FAILURE)
