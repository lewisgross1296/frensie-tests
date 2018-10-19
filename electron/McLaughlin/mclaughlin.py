#! /usr/bin/env python
import os
import sys
import numpy
import datetime
import socket
import PyFrensie.Data as Data
import PyFrensie.Data.Native as Native
import PyFrensie.Geometry.DagMC as DagMC
import PyFrensie.Geometry as Geometry
import PyFrensie.Utility as Utility
import PyFrensie.Utility.MPI as MPI
import PyFrensie.Utility.Prng as Prng
import PyFrensie.Utility.Coordinate as Coordinate
import PyFrensie.Utility.Distribution as Distribution
import PyFrensie.MonteCarlo as MonteCarlo
import PyFrensie.MonteCarlo.Collision as Collision
import PyFrensie.MonteCarlo.ActiveRegion as ActiveRegion
import PyFrensie.MonteCarlo.Event as Event
import PyFrensie.MonteCarlo.Manager as Manager

# Add the parent directory to the path
sys.path.insert(1,'../')
import simulation_setup as setup

##---------------------------------------------------------------------------##
## ---------------------- GLOBAL SIMULATION VARIABLES ---------------------- ##
##---------------------------------------------------------------------------##

# Set the material ( Al, polystyrene, polyethylene )
material="Al"
# Set the source energy
energy=3.0
# Set the material density (g/cm3)
density=2.7

# Set the bivariate interpolation (LOGLOGLOG, LINLINLIN, LINLINLOG)
interpolation=MonteCarlo.LOGLOGLOG_INTERPOLATION

# Set the bivariate Grid Policy (UNIT_BASE_CORRELATED, CORRELATED, UNIT_BASE)
grid_policy=MonteCarlo.UNIT_BASE_CORRELATED_GRID

# Set the elastic distribution mode ( DECOUPLED, COUPLED, HYBRID )
mode=MonteCarlo.COUPLED_DISTRIBUTION

# Set the elastic coupled sampling method
# ( TWO_D_UNION, ONE_D_UNION, MODIFIED_TWO_D_UNION )
method=MonteCarlo.MODIFIED_TWO_D_UNION

# Set the data file type (ACE_EPR_FILE, Native_EPR_FILE)
file_type=Data.ElectroatomicDataProperties.Native_EPR_FILE

# Set the width of the subzones (cm)
subzone_width=0.0148

# Set database directory path (for Denali)
if socket.gethostname() == "Denali":
  database_path = "/home/software/mcnpdata/database.xml"
  geometry_path = "/home/lkersting/frensie/tests/electron/McLaughlin/"
elif socket.gethostname() == "Elbrus": # Set database directory path (for Elbrus)
  database_path = "/home/software/mcnpdata/database.xml"
  geometry_path = "/home/ligross/frensie/tests/McLaughlin/"
else: # Set database directory path (for Cluster)
  database_path = "/home/lkersting/software/mcnp6.2/MCNP_DATA/database.xml"
  geometry_path = "/home/lkersting/dag_frensie/tests/electron/McLaughlin/"

geometry_path += material + "/geom.h5m"

# Run the simulation
def runSimulation( threads, histories, time ):

  ##--------------------------------------------------------------------------##
  ## ------------------------------ MPI Session ----------------------------- ##
  ##--------------------------------------------------------------------------##
  session = MPI.GlobalMPISession( len(sys.argv), sys.argv )
  Utility.removeAllLogs()
  session.initializeLogs( 0, True )

  properties = setSimulationProperties( histories, time )
  name, title = setSimulationName( properties, file_type )
  path_to_database = database_path
  path_to_geometry = geometry_path

  ##--------------------------------------------------------------------------##
  ## ---------------------------- GEOMETRY SETUP ---------------------------- ##
  ##--------------------------------------------------------------------------##


  # Set geometry path and type
  geometry_type = "DagMC" #(ROOT or DAGMC)

  # Set geometry model properties
  if geometry_type == "DagMC":
    model_properties = DagMC.DagMCModelProperties( path_to_geometry )
    model_properties.useFastIdLookup()
    # model_properties.setMaterialPropertyName( "mat" )
    # model_properties.setDensityPropertyName( "rho" )
    # model_properties.setTerminationCellPropertyName( "graveyard" )
    # model_properties.setEstimatorPropertyName( "tally" )
  else:
    print "ERROR: geometry type ", geometry_type, " not supported!"

  # Construct model
  geom_model = DagMC.DagMCModel( model_properties )

  ##--------------------------------------------------------------------------##
  ## -------------------------- EVENT HANDLER SETUP -------------------------- ##
  ##--------------------------------------------------------------------------##

  # Set event handler
  event_handler = Event.EventHandler( properties )

  ## -------------------- Energy Deposition Calorimeter -------------------- ##

  number_of_subzones = 50

  # Setup a cell pulse height estimator
  estimator_id = 1
  cell_ids = range(1,number_of_subzones+1)
  energy_deposition_estimator = Event.WeightAndEnergyMultipliedCellPulseHeightEstimator( estimator_id, 1.0, cell_ids )

  # Set the particle type
  energy_deposition_estimator.setParticleTypes( [MonteCarlo.ELECTRON] )

  # Add the estimator to the event handler
  event_handler.addEstimator( energy_deposition_estimator )

  ##--------------------------------------------------------------------------##
  ## ----------------------- SIMULATION MANAGER SETUP ------------------------ ##
  ##--------------------------------------------------------------------------##

  # Initialized database
  database = Data.ScatteringCenterPropertiesDatabase(path_to_database)
  scattering_center_definition_database = Collision.ScatteringCenterDefinitionDatabase()

  # Set material properties
  version = 0
  if file_type == Data.ElectroatomicDataProperties.ACE_EPR_FILE:
    version = 14

  # Definition for Aluminum
  if material == "Al":
    al_properties = database.getAtomProperties( Data.Al_ATOM )

    al_definition = scattering_center_definition_database.createDefinition( material, Data.ZAID(13000) )

    al_definition.setElectroatomicDataProperties(
      al_properties.getSharedElectroatomicDataProperties( file_type, version ) )

    definition = ( ("Al", 1.0), )

  else:
    h_properties = database.getAtomProperties( Data.H_ATOM )

    h_definition = scattering_center_definition_database.createDefinition( "H", Data.ZAID(1000) )

    h_definition.setElectroatomicDataProperties(
      h_properties.getSharedElectroatomicDataProperties( file_type, version ) )

    c_properties = database.getAtomProperties( Data.C_ATOM )

    c_definition = scattering_center_definition_database.createDefinition( "C", Data.ZAID(6000) )

    c_definition.setElectroatomicDataProperties(
      c_properties.getSharedElectroatomicDataProperties( file_type, version ) )


    # Definition for polystyrene
    if material == "polystyrene":
      definition = ( ("H", -0.77418), ("C", -0.922582) )

    # Definition for polyethylene
    elif material == "polyethylene":
      definition = ( ("H", -0.14), ("C", -0.86) )

    else:
      print "ERROR: material ", material, " is currently not supported!"


  material_definition_database = Collision.MaterialDefinitionDatabase()
  material_definition_database.addDefinition( material, 1, definition )

  # Get the material ids
  material_ids = geom_model.getMaterialIds()

  # Fill model
  model = Collision.FilledGeometryModel( path_to_database, scattering_center_definition_database, material_definition_database, properties, geom_model, True )

  # Set particle distribution
  particle_distribution = ActiveRegion.StandardParticleDistribution( "source distribution" )

  # Set the energy dimension distribution
  delta_energy = Distribution.DeltaDistribution( energy )
  energy_dimension_dist = ActiveRegion.IndependentEnergyDimensionDistribution( delta_energy )
  particle_distribution.setDimensionDistribution( energy_dimension_dist )

  # Set the direction dimension distribution
  particle_distribution.setDirection( 0.0, 0.0, 1.0 )

  # Set the spatial dimension distribution
  particle_distribution.setPosition( 0.0, 0.0, -0.01 )

  particle_distribution.constructDimensionDistributionDependencyTree()

  # Set source components
  source_component = [ActiveRegion.StandardElectronSourceComponent( 0, 1.0, geom_model, particle_distribution )]

  # Set source
  source = ActiveRegion.StandardParticleSource( source_component )

  # Set the archive type
  archive_type = "xml"

  factory = Manager.ParticleSimulationManagerFactory( model,
                                                      source,
                                                      event_handler,
                                                      properties,
                                                      name,
                                                      archive_type,
                                                      threads )

  manager = factory.getManager()

  Utility.removeAllLogs()
  session.initializeLogs( 0, False )

  manager.runSimulation()

  if session.rank() == 0:

    print "Processing the results:"
    processData( energy_deposition_estimator, name, title, subzone_width*density )

    print "Results will be in ", os.path.dirname(name)

# Restart the simulation
def restartSimulation( threads, histories, time, rendezvous ):

  ##--------------------------------------------------------------------------##
  ## ------------------------------ MPI Session ----------------------------- ##
  ##--------------------------------------------------------------------------##
  session = MPI.GlobalMPISession( len(sys.argv), sys.argv )
  Utility.removeAllLogs()
  session.initializeLogs( 0, True )

  # Set the data path
  Collision.FilledGeometryModel.setDefaultDatabasePath( database_path )

  factory = Manager.ParticleSimulationManagerFactory( rendezvous, histories, time, threads )

  manager = factory.getManager()

  Utility.removeAllLogs()
  session.initializeLogs( 0, False )

  manager.runSimulation()

  if session.rank() == 0:

    rendezvous_number = manager.getNumberOfRendezvous()

    components = rendezvous.split("rendezvous_")
    archive_name = components[0] + "rendezvous_"
    archive_name += str( rendezvous_number - 1 )
    archive_name += "."
    archive_name += components[1].split(".")[1]

    # print "Processing the results:"
    # processData( archive_name, "native" )

    # print "Results will be in ", os.path.dirname(archive_name)

##---------------------------------------------------------------------------##
## ------------------------- SIMULATION PROPERTIES ------------------------- ##
##---------------------------------------------------------------------------##
def setSimulationProperties( histories, time ):

  properties = setup.setSimulationProperties( histories, time, interpolation, grid_policy, mode, method )


  ## -------------------------- ELECTRON PROPERTIES ------------------------- ##

  # Turn certain reactions off
  # properties.setElasticModeOff()
  # properties.setElectroionizationModeOff()
  # properties.setBremsstrahlungModeOff()
  # properties.setAtomicExcitationModeOff()

  return properties

##----------------------------------------------------------------------------##
## ------------------------ Create Results Directory ------------------------ ##
##----------------------------------------------------------------------------##
def createResultsDirectory():

  directory = setup.getResultsDirectory(file_type, interpolation)

  directory = material + "/" + directory

  if not os.path.exists(directory):
    os.makedirs(directory)

  print directory
  return directory

##---------------------------------------------------------------------------##
## -------------------------- setSimulationName -----------------------------##
##---------------------------------------------------------------------------##
# Define a function for naming an electron simulation
def setSimulationName( properties, file_type ):
  extension, title = setup.setSimulationNameExtention( properties, file_type )
  name = "mclaughlin" + extension
  output = material + "/" + setup.getResultsDirectory(file_type, interpolation) + "/" + name

  return (output, title)

##----------------------------------------------------------------------------##
##--------------------------- processDataFromFile ----------------------------##
##----------------------------------------------------------------------------##

# This function pulls data from the .xml results file
def processDataFromFile( rendezvous_file, raw_file_type, subzone_op ):

  Collision.FilledGeometryModel.setDefaultDatabasePath( database_path )

  # Load data from file
  manager = Manager.ParticleSimulationManagerFactory( rendezvous_file ).getManager()
  event_handler = manager.getEventHandler()

  # Get the estimator data
  estimator_1 = event_handler.getEstimator( 1 )

  # Get the simulation name and title
  properties = manager.getSimulationProperties()

  if raw_file_type == "ace":
    file_type = Data.ElectroatomicDataProperties.ACE_EPR_FILE
  elif raw_file_type == "native":
    file_type = Data.ElectroatomicDataProperties.Native_EPR_FILE
  else:
    ValueError
  filename, title = setSimulationName( properties, file_type )
  filename = rendezvous_file.split("_rendezvous_")[0]

  print "Processing the results:"
  processData( estimator_1, filename, title, subzone_op )

  print "Results will be in ", os.path.dirname(filename)

##----------------------------------------------------------------------------##
##------------------------------- processData --------------------------------##
##----------------------------------------------------------------------------##

# This function pulls pulse height estimator data outputs it to a separate file.
def processData( estimator, filename, title, subzone_op ):

  today = datetime.date.today()

  # Read the data file for surface tallies
  name = filename+"_energy_dep.txt"
  out_file = open(name, 'w')

  # Write title to file
  out_file.write( "# " + title +"\n")

  # Write the header to the file
  header = "# Range (g/cm2)\tEnergy Deposition (MeV cm2/g)\tError\t"+str(today)+"\n"
  out_file.write(header)

  ids = list(estimator.getEntityIds())

  for i in range(0,len(ids)):
    processed_data = estimator.getEntityBinProcessedData( ids[i] )
    energy_dep_mev = processed_data['mean']
    rel_error = processed_data['re']

    depth = subzone_op*(i+1)

    # Write the energy deposition to the file
    data = str(depth) + '\t' + str(energy_dep_mev[0]/subzone_op) + '\t' + str(rel_error[0]/subzone_op) + '\n'
    out_file.write(data)
  out_file.close()