#! /usr/bin/env python
import xml.etree.ElementTree as ET
import sys; sys.path.append("../")
from ElementTree_pretty import prettify

# Set up the argument parser
description = "This script allows one to write the est.xml file for FACEMC."\
              "The input parameter is the geometry type."

root = ET.Element("ParameterList", name="Estimators")

# Transmission Tally
parameter_1 = ET.SubElement(root, "ParameterList", name="Transmission Current")

ET.SubElement(parameter_1, "Parameter", name="Id", type="unsigned int", value="1")
ET.SubElement(parameter_1, "Parameter", name="Type", type="string", value="Surface Current")
ET.SubElement(parameter_1, "Parameter", name="Particle Type", type="string", value="Electron")
ET.SubElement(parameter_1, "Parameter", name="Surfaces", type="Array", value="{48}")

sub_list_1 = ET.SubElement(parameter_1, "ParameterList", name="Bins")
ET.SubElement(sub_list_1, "Parameter", name="Cosine Bins", type="Array", value="{\
-1.0,\
0.0,\
0.848048096156426,\
0.882126866017668,\
0.913332365617192,\
0.938191335922484,\
0.951433341895538,\
0.960585317886711,\
0.968669911264357,\
0.974526872786577,\
0.978652704312051,\
0.982024659632372,\
0.985229115235059,\
0.988520271746353,\
0.991146155097021,\
0.992986158373646,\
0.995072889372028,\
0.996419457128586,\
0.997012445565730,\
0.997743253476273,\
0.998187693254492,\
0.998555486558339,\
0.998823128276774,\
0.999166134342540,\
0.999378583910478,\
0.999701489781183,\
0.999853726281158,\
0.999958816007535,\
1.0}")

# ET.SubElement(sub_list_1, "Parameter", name="Cosine Bins", type="Array", value="{\
# -1.0,\
#  0.0,\
#  0.939692620785908,\
#  0.965925826289068,\
#  0.984807753012208,\
#  0.990268068741570,\
#  0.994521895368273,\
#  0.995396198367179,\
#  0.996194698091746,\
#  0.996917333733128,\
#  0.997564050259824,\
#  0.998134798421867,\
#  0.998629534754574,\
#  0.999048221581858,\
#  0.999390827019096,\
#  0.999657324975557,\
#  0.999847695156391,\
#  0.999961923064171,\
#  1.0}")

# Reflection Tally
parameter_2 = ET.SubElement(root, "ParameterList", name="Reflection Current")

ET.SubElement(parameter_2, "Parameter", name="Id", type="unsigned int", value="2")
ET.SubElement(parameter_2, "Parameter", name="Type", type="string", value="Surface Current")
ET.SubElement(parameter_2, "Parameter", name="Particle Type", type="string", value="Electron")
ET.SubElement(parameter_2, "Parameter", name="Surfaces", type="Array", value="{46}")

sub_list_2 = ET.SubElement(parameter_2, "ParameterList", name="Bins")
ET.SubElement(sub_list_2, "Parameter", name="Cosine Bins", type="Array", value="{-1.0, -0.999999, 1.0}")


# Reflection Tally
parameter_3 = ET.SubElement(root, "ParameterList", name="Cell Track Length Flux Estimator")

ET.SubElement(parameter_3, "Parameter", name="Id", type="unsigned int", value="3")
ET.SubElement(parameter_3, "Parameter", name="Type", type="string", value="Cell Track-Length Flux")
ET.SubElement(parameter_3, "Parameter", name="Particle Type", type="string", value="Electron")
ET.SubElement(parameter_3, "Parameter", name="Cells", type="Array", value="{7}")

sub_list_3 = ET.SubElement(parameter_3, "ParameterList", name="Bins")
ET.SubElement(sub_list_3, "Parameter", name="Energy Bins", type="Array", value="{1.5e-5, 99l, 15.7")


prettify(root,"est.xml")

