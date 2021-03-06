#! /usr/bin/env python
import argparse as ap
import xml.etree.ElementTree as ET
import sys; sys.path.append("../")
from ElementTree_pretty import prettify
import os.path

# Set up the argument parser
description = "This script allows one to write the geom.xml file for FACEMC. "\
              "The input parameter is the geometry type."

parser = ap.ArgumentParser(description=description)

geom_type_msg = "the geometry type (DagMC, ROOT)"
parser.add_argument('-t', help=geom_type_msg, required=False)

# Parse the user's arguments
user_args = parser.parse_args()
name_base ="geom"

geom_type = "DagMC"
if user_args.t:
    geom_type = user_args.t

root = ET.Element("ParameterList", name="Geometry")

if geom_type == "DagMC" or geom_type == "DAGMC" or geom_type == "dagmc":
    sat_file = "h_sphere.sat"
    ET.SubElement(root, "Parameter", name="Handler", type="string", value="DagMC")
    ET.SubElement(root, "Parameter", name="CAD File", type="string", value=sat_file)
    ET.SubElement(root, "Parameter", name="Facet Tolerance", type="double", value="1e-3")
    ET.SubElement(root, "Parameter", name="Use Fast Id Lookup", type="bool", value="True")
    ET.SubElement(root, "Parameter", name="Termination Cell Property", type="string", value="termination.cell")
    ET.SubElement(root, "Parameter", name="Estimator Property", type="string", value="estimator")
    ET.SubElement(root, "Parameter", name="Material Property", type="string", value="mat")
    ET.SubElement(root, "Parameter", name="Density Property", type="string", value="rho")

elif geom_type == "ROOT" or geom_type == "root" or geom_type == "Root":
    root_file = "h_sphere.root"
    name_base=name_base+"_root"
    ET.SubElement(root, "Parameter", name="Handler", type="string", value="ROOT")
    ET.SubElement(root, "Parameter", name="Root File", type="string", value=root_file)
    ET.SubElement(root, "Parameter", name="Terminal Material Name", type="string", value="graveyard")
    ET.SubElement(root, "Parameter", name="Void Material Name", type="string", value="void")
    ET.SubElement(root, "Parameter", name="Material Property Name", type="string", value="mat")

else:
    # Just assume DagMC
    sat_file = "h_sphere.sat"
    ET.SubElement(root, "Parameter", name="Handler", type="string", value="DagMC")
    ET.SubElement(root, "Parameter", name="CAD File", type="string", value=sat_file)
    ET.SubElement(root, "Parameter", name="Facet Tolerance", type="double", value="1e-3")
    ET.SubElement(root, "Parameter", name="Use Fast Id Lookup", type="bool", value="True")
    ET.SubElement(root, "Parameter", name="Termination Cell Property", type="string", value="termination.cell")
    ET.SubElement(root, "Parameter", name="Estimator Property", type="string", value="estimator")
    ET.SubElement(root, "Parameter", name="Material Property", type="string", value="mat")
    ET.SubElement(root, "Parameter", name="Density Property", type="string", value="rho")

name =name_base+".xml"
i=1
while os.path.isfile(name):
  name = name_base+"_"+str(i)+".xml"
  i=i+1

prettify(root,name)
print name