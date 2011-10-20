"""
Validator for the tool's parameters, controls the behavior of the tool's dialog
"""
import arcpy

class ToolValidator:
  def __init__(self):
    params = arcpy.GetParameterInfo()

    self.inputs = {}
    self.inputs["input_points"] = params[0];
    self.inputs["input_network"] = params[1];
    self.inputs["compute_reach"] = params[2];
    self.inputs["compute_gravity"] = params[3];
    self.inputs["compute_betweenness"] = params[4];
    self.inputs["compute_closeness"] = params[5];
    self.inputs["compute_straightness"] = params[6];
    self.inputs["id_attribute"] = params[7];
    self.inputs["node_weight_attribute"] = params[8];
    self.inputs["impedance_attribute"] = params[9];
    self.inputs["search_radius"] = params[10];
    self.inputs["max_neighbor_separation"] = params[11];
    self.inputs["beta"] = params[12];
    self.inputs["normalize_results"] = params[13];
    self.inputs["output_location"] = params[14];
    self.inputs["output_file_name"] = params[15];
    self.inputs["accumulator_attributes"] = params[16];

  """
  Called when the tool is opened
  """
  def initializeParameters(self):
    self.inputs["accumulator_attributes"].category = "Accumulators"
    self.inputs["normalize_results"].category = "Normalization"

  """
  Called whenever a parameter has been changed
  """
  def updateParameters(self):
    # impedance_attribute
    network = self.inputs["input_network"]
    if network.altered:
      if network.value and not network.hasBeenValidated:
        try:
          self.get_network_properties(network)
        except:
          self.reset_network_properties()
    else:
      self.reset_network_properties()

    # beta
    self.inputs["beta"].enabled = self.inputs["compute_gravity"].value

    # normalize_results
    metrics_to_compute = []
    norm_results = self.inputs["normalize_results"]
    if self.inputs["compute_reach"].value: metrics_to_compute.append("Reach")
    if self.inputs["compute_gravity"].value: metrics_to_compute.append("Gravity_Type_Index")
    if self.inputs["compute_betweenness"].value: metrics_to_compute.append("Betweenness")
    if self.inputs["compute_closeness"].value: metrics_to_compute.append("Closeness")
    if self.inputs["compute_straightness"].value: metrics_to_compute.append("Straightness")
    norm_results.filter.list = metrics_to_compute
    norm_results.enabled = bool(metrics_to_compute)

  """
  Called after internal validation
  """
  def updateMessages(self):
    network = self.inputs["input_network"]
    impedance = self.inputs["impedance_attribute"]
    search_radius = self.inputs["search_radius"]
    if network.altered or impedance.altered:
      try:
        for attribute in arcpy.Describe(network.value).attributes:
          if attribute.name == impedance.value:
            search_radius.setWarningMessage("Units: %s" % attribute.units)
            return
        search_radius.setWarningMessage("No units")
      except:
        search_radius.setWarningMessage("No units")

  """
  Updates list of cost attributes based on the input network
  """
  def get_network_properties(self, network):
    impedance = self.inputs["impedance_attribute"]
    accumulators = self.inputs["accumulator_attributes"]

    description = arcpy.Describe(network.value)
    defalut_cost_attribute = ""
    cost_attributes = []
    for attribute in description.attributes:
      if attribute.usageType == "Cost":
        if attribute.useByDefault:
          default_cost_attribute = attribute.name
        cost_attributes.append(attribute.name)

    impedance.filter.list = cost_attributes
    accumulators.filter.list = cost_attributes

    if not impedance.altered:
      if default_cost_attribute == "" and cost_attributes:
        default_cost_attribute = cost_attributes[0]
      impedance.value = default_cost_attribute

  """
  Reset the list of cost attributes
  """
  def reset_network_properties(self):
    impedance = self.inputs["impedance_attribute"]
    impedance.filter.list = []
    impedance.value = ""
    self.inputs["accumulator_attributes"].filter.list = []
