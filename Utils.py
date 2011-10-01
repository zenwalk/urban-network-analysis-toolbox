# -------------------------------------------------------------------------------------
# Urban Network Analysis Toolbox for ArcGIS10
# Credits: Michael Mekonnen, Andres Sevtsuk
# MIT City Form Research Group
# Usage: Creative Commons Attribution - NonCommercial - ShareAlike 3.0 Unported License
# License: http://creativecommons.org/licenses/by-nc-sa/3.0/
# -------------------------------------------------------------------------------------

import arcpy
from Constants import TOLERANCE
from math import sqrt

"""
Exception thrown when input is invalid
"""
class Invalid_Input_Exception(Exception):
  """
  |input_name|: the name of the invalid input
  """
  def __init__(self, input_name):
    self.input_name = input_name

  def __str__(self):
    return "Invalid Input: %s" % self.input_name

"""
Wrapper for the arcpy progress bar
"""
class Progress_Bar:
  """
  |n|: number of steps to count to
  |p|: display is updated every |p| steps, default is 1
  |caption|: message to display with the progress bar
  """
  def __init__(slef, n, p=1, caption=""):
    self.n = n
    self.p = p
    self.caption = caption
    # Create progress bar
    self.bar = self.progress_bar()
    # Start progress bar
    self.step()

  """
  Move the progress bar by 1 step
  """
  def step(self):
    self.bar.next()

  """
  A generator representation of the arcpy progressor
  """
  def progress_bar(self):
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

"""
Returns True if |a| and |b| are within |TOLERANCE|
"""
def eq_TOL(a, b):
  return abs(a, b) < TOLERANCE

"""
Returns the first 10 characters of |field_name|
(DBF files truncate field names to 10 characters)
"""
def trim(field_name):
  return field_name[:10]

"""
Computes the euclidean distance between |loc1| and |loc2|

|loc1|: (x1, y1)
|loc2|: (x2, y2)
"""
def dist(loc1, loc2):
  x1, y1 = loc1
  x2, y2 = loc2
  return sqrt((x1 - x2)**2 + (y1 - y2)**2)

"""
Returns comb_map, such that comb_map[key] = |f|(|map1|[key], |map2|[key])
|map1| and |map2| must have the same keys
"""
def merge_maps(map1, map2, f):
  comb_map = {}
  for key in map1:
    comb_map[key] = f(map1[key], map2[key])
  return comb_map

"""
Returns True if |row| has the field |field|
"""
def row_has_field(row, field):
  try:
    row.getValue(field)
    return True
  except:
    return False
