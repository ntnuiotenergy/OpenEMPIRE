# OpenEMPIRE
Open basic version of EMPIRE in Pyomo

# OpenEMPIRE
Open basic version of EMPIRE in Pyomo

# Required Software
The EMPIRE model is available in the Python-based, open-source optimization modelling language Pyomo. To run the model, make sure Python, Pyomo and a third-party solver like SCIP or CPLEX is installed and loaded to the respective computer or cluster. More information on how to install Python and Pyomo can be found here: http://www.pyomo.org/installation.

# Test Run
Note that building the instance in Pyomo for a base case of EMPIRE can take around 40 min. Therefore, it is good to run the ‘test_run.py’ first to confirm whether your computer or cluster connects to the preferred solver or not.

# Running
When all Pyomo and the preferred solver has been installed, the model is run by running the script ‘run.py’ in a Python interface. The code is run by using the following commands:
C:\Users\name> cd <path_to_folder>           
C:\Users\name\path_to_folder> python run.py   
