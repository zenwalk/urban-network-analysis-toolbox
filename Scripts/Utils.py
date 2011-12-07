# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

import arcpy
from Constants import *
from math import sqrt
from os.path import join

class Invalid_Input_Exception(Exception):
  """
  Exception thrown when input is invalid
  """

  def __init__(self, input_name):
    """
    |input_name|: the name of the invalid input
    """
    self.input_name = input_name

  def __str__(self):
    return "Invalid Input: %s" % self.input_name

class Progress_Bar:
  """
  Wrapper for the arcpy progress bar
  """

  def __init__(self, n, p, caption):
    """
    |n|: number of steps to count to
    |p|: display is updated every |p| steps
    |caption|: message to display with the progress bar
    """
    self.n = n
    self.p = p
    self.caption = caption
    # Create progress bar
    self.bar = self.progress_bar()
    # Start progress bar
    self.step()

  def step(self):
    """
    Move the progress bar by 1 step
    """
    self.bar.next()

  def progress_bar(self):
    """
    A generator representation of the arcpy progressor
    """
    # Setup progressor with min, max, interval, and label
    arcpy.SetProgressor("step", "", 0, self.n, self.p)
    arcpy.SetProgressorLabel(self.caption)
    # Counter
    count = 0
    while True:
      # Update display
      if count % self.p == 0:
        arcpy.SetProgressorPosition(count)
      # Finished?
      if count == self.n:
        arcpy.SetProgressorLabel("")
        arcpy.ResetProgressor()
      count += 1
      yield

def to_point_feature_class(feature_class, location):
  """
  Converts |feature_class| to point feature class
  Returns the name of the newly created point feature class
  Saves the new file at |location|
  """
  feature_class_name = str(arcpy.Describe(feature_class).baseName)
  arcpy.AddMessage(feature_class_name)
  point_feature_class_name = POINT_FEATURE_CLASS_NAME(feature_class_name)
  arcpy.AddMessage(point_feature_class_name)
  point_feature_class = "%s.shp" % (join(location, point_feature_class_name))
  arcpy.AddMessage(point_feature_class)
  arcpy.FeatureToPoint_management(in_features=feature_class,
                                  out_feature_class=point_feature_class,
				  point_location="CENTROID")
  return point_feature_class

def eq_tol(a, b):
  """
  Returns True if |a| and |b| are within |TOLERANCE|, False otherwise
  """
  return abs(a - b) <= TOLERANCE

def lt_tol(a, b):
  """
  Returns True if |a| is less than |b| by more than |TOLERANCE|, False otherwise
  """
  return b - a > TOLERANCE

def trim(field_name):
  """
  Returns the first 10 characters of |field_name|
  (DBF files truncate field names to 10 characters)
  """
  return field_name[:10]

def dist(loc1, loc2):
  """
  Computes the euclidean distance between |loc1| and |loc2|
  |loc1|: (x1, y1)
  |loc2|: (x2, y2)
  """
  x1, y1 = loc1
  x2, y2 = loc2
  return sqrt((x1 - x2)**2 + (y1 - y2)**2)

def merge_maps(map1, map2, f):
  """
  Returns comb_map, such that comb_map[key] = |f|(|map1|[key], |map2|[key])
  |map1| and |map2| must have the same keys
  """
  if set(map1.keys()) != set(map2.keys()):
    raise Exception("Invalid input to |merge_maps|")
  comb_map = {}
  for key in map1:
    comb_map[key] = f(map1[key], map2[key])
  return comb_map

def row_has_field(row, field):
  """
  Returns True if |row| has the field |field|, False otherwise
  """
  try:
    row.getValue(field)
    return True
  except:
    return False

def is_accumulator_field(field):
  """
  Returns True if |field| is an accumulator field, False otherwise
  """
  return field.startswith("Total_")
