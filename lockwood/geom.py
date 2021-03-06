#! /usr/bin/env python
import argparse as ap
import xml.etree.ElementTree as ET
import sys; sys.path.append("../")
from ElementTree_pretty import prettify

# Set up the argument parser
description = "This script allows one to write the source.xml file for FACEMC. "\
              "The input parameter is the geometry type."

parser = ap.ArgumentParser(description=description)

geom_type_msg = "the geometry type (DagMC, ROOT)"
parser.add_argument('-t', help=geom_type_msg, required=False)

geom_file_msg = "the geometry file path"
parser.add_argument('-f', help=geom_file_msg, required=False)

# Parse the user's arguments
user_args = parser.parse_args()
geom_type = user_args.t
geom_file = user_args.f

# Extract energy and element from the file path
energy = geom_file.rsplit('/')[-3]

# Extract test number from file name
test_number = geom_file.rsplit('_', 1)[-1][:-4]

name = "geom_"+str(geom_type)+"_"+str(energy)+"_"+str(test_number)+".xml"
root = ET.Element("ParameterList", name="Geometry")

if str(geom_type) == "DagMC":
    ET.SubElement(root, "Parameter", name="Handler", type="string", value="DagMC")
    ET.SubElement(root, "Parameter", name="CAD File", type="string", value=str(geom_file))
    ET.SubElement(root, "Parameter", name="Facet Tolerance", type="double", value="1e-3")
    ET.SubElement(root, "Parameter", name="Use Fast Id Lookup", type="bool", value="True")

elif str(geom_type) == "ROOT":
    ET.SubElement(root, "Parameter", name="Handler", type="string", value="ROOT")
    ET.SubElement(root, "Parameter", name="Root File", type="string", value=str(geom_file))
    ET.SubElement(root, "Parameter", name="Terminal Material Name", type="string", value="graveyard")
    ET.SubElement(root, "Parameter", name="Void Material Name", type="string", value="void")
    # ET.SubElement(root, "Parameter", name="Estimator Property", type="string", value="estimator")

else:
    # Just assume DagMC
    ET.SubElement(root, "Parameter", name="Handler", type="string", value="DagMC")
    ET.SubElement(root, "Parameter", name="CAD File", type="string", value=str(geom_file))
    ET.SubElement(root, "Parameter", name="Facet Tolerance", type="double", value="1e-3")
    ET.SubElement(root, "Parameter", name="Use Fast Id Lookup", type="bool", value="True")


# ET.SubElement(root, "Parameter", name="Material Property Name", type="string", value="mat")
# ET.SubElement(root, "Parameter", name="Density Property", type="string", value="rho")

prettify(root,name)
print name
