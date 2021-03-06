#! /usr/bin/env python
import datetime
import os
import shutil
import sys, getopt
from subprocess import call

def main(argv):
    base = 'mcnp'
    try:
        opts, args = getopt.getopt(argv,"he:f:",["filename=","energy="])
    except getopt.GetoptError:
        print 'data_processor.py -f <filename> -e <energy>'
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print 'data_processor.py -f <filename> -e <energy in MeV>'
            sys.exit(1)
        elif opt in ("-f", "--filename"):
            base = arg
        elif opt in ("-e", "--energy"):
            energy = arg

    if energy:
      cell_list = ['10']
      surface_list = ['100', '101']
      angle_list = ['', 'full' ]

      # Get mcnp output file name
      mcnp_output = base+".o"

      # Check if file exists
      if os.path.isfile(mcnp_output):

          today = datetime.date.today()
          # Read the mcnp data file for surface tallies
          with open(mcnp_output) as data:
              # go through all surface tallies
              for i in cell_list:
                  start=" cell  "+i
                  name = base+"_cell_flux.txt"
                  file = open(name, 'w')
                  header = "# Energy   flux \t   Sigma\t"+str(today)+"\n"
                  file.write(header)
                  # Skips text before the beginning of the interesting block:
                  for line in data:
                      if line.startswith(start):
                          data.next()
                          break
                  # Reads text until the end of the block:
                  for line in data:  # This keeps reading the file
                      if line.startswith('      total'):
                          file.close()
                          break
                      line = line.lstrip()
                      line = line.replace('   ',' ')
                      file.write(line)

          with open(mcnp_output) as data:
              # go through all surface tallies
              for i in surface_list:
                  start=" surface  "+i

                  # go through the current estimators first angle
                  if i == '100':
                      print "\n Energy (MeV)\tAlbedo\tError"
                      name = base+"_albedo.txt"
                      file = open(name, 'w')
                      header = "# Energy (MeV)\tAlbedo\tError\t"+str(today)+"\n"
                      file.write(header)
                      # Skips text before the beginning of the interesting block:
                      for line in data:
                          if line.startswith(start):
                              line = data.next().strip()
                              line = line.replace('angle  bin:  -1.          to  ','')
                              line = line.replace('0.00000E+00',energy)
                              line = line.replace(' mu',' ')
                              line+=data.next().strip()+'\n'
                              file.write(line)
                              print line
                              break
                      file.close()
                  else:
                      name = base+"_transmission.txt"
                      file = open(name, 'w')
                      header = "# Energy (keV)\tTransmission\tError\t"+str(today)+"\n"
                      total_number_of_angles = 3
                      number_of_angles = 0
                      file.write(header)
                      # Skips text before the beginning of the interesting block:
                      print " Transmission:"
                      for line in data:
                          if line.startswith(start):
                              line = data.next().strip()
                              if number_of_angles == 0:
                                  print number_of_angles, ": ",line
                                  line = line.replace('angle  bin:  -1.          to  ','')
                              elif number_of_angles == 1:
                                  print number_of_angles, ": ",line
                                  line = line.replace('angle  bin:   0.00000E+00 to  ','')
                              elif number_of_angles == 2:
                                  print number_of_angles, ": ",line
                                  line = line.replace('angle  bin:   9.90000E-01 to  ','')
                              line = line.replace(' mu',' ')
                              line+=data.next().strip()+'\n'
                              file.write(line)
                              print line
                              number_of_angles+=1
                              if number_of_angles == total_number_of_angles:
                                  break
                      file.close()

      else:
          print "File ",mcnp_output," does not exist!"
    else:
      print "No input energy given!"

if __name__ == "__main__":
   main(sys.argv[1:])
