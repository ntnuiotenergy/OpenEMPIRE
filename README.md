# OpenEMPIRE
Open basic version of EMPIRE in Pyomo.

# Licencing
The EMPIRE model and all additional files in the git repository are licensed under the MIT license. In short, that means you can use and change the code of EMPIRE. Furthermore, you can change the license in your redistribution but must mention the original author. We appreciate if you inform us about changes and send a merge request via git.
For further information please read the LICENSE file, which contains the license text, or go to https://opensource.org/licenses/MIT

# Required Software
The EMPIRE model is available in the Python-based, open-source optimization modelling language Pyomo. Running the model thus requires some coding skills in Python. To run the model, make sure Python, Pyomo and a third-party solver (gurobi, FICO xpress, or CPLEX) is installed and loaded to the respective computer or cluster. More information on how to install Python and Pyomo can be found here: http://www.pyomo.org/installation. 
Other python package dependencies can be found in the file environment.yml.

To download, you need to install Git and clone the repository. Note that the repository makes use of Git Large File Storage (LFS) which also needs to be installed for input data-files to be downloaded when cloning the repository. Once both Git and Git LFS has been successfully installed, the model is downloaded to the desired directory.

# Software Structure
EMPIRE consists of five programming scripts: 

<b>(1)	run.py:</b> The main script used to run EMPIRE. It links to all other scripts. This is the only script a user of EMPIRE needs to use and potentially modify.  

<b>(2)	Empire.py:</b> Contains the abstract formulation of EMPIRE in Pyomo. This script also contains code related to printing the results.

<b>(3)	scenario_random.py:</b> Generates random operational scenarios as .tab-files through sampling.

<b>(4)	reader.py:</b> Generates .tab-files input based on data provided in Excel workbooks. 

<b>(5)	test_run.py:</b> Same as the main run-script (run.py), but it is linked to a small test instance of EMPIRE that usually finishes in 1-2 min. 

In the repository, the ‘Data handler’-folder contains the Excel workbooks that are used to store and modify input data. The workbooks are contained within folders representing instance-versions of EMPIRE, e.g. ‘europe_v50’. The ‘test’-folder contains input data for a small test-instance of EMPIRE. Within an instance-version in the ‘Data handler’-folder, there is a folder called ‘ScenarioData’ containing large data sets used to generate stochastic scenarios in EMPIRE. If EMPIRE is run with random scenario generation, representative time series are sampled once per scenario and season for each random input parameter.

The EMPIRE Model reads .tab-files, which provide all needed sets and input data. For editing and storing the data, excel-files are used. There are seven excel-files in total of which six contain indexed input data and one is to provide the indices/sets. The excel-files are sorted by the following categories: General data, generation data, country/node data, set/index data, transmission data, and storage data.  These files contain multiple tables regarding for example investment costs and initial capacity. 

For more details, please refer to the software documentation in the repository.

# User options
<table style="width:100%">
  <tr>
    <th>Input name</th>
    <th>Type</th> 
    <th>Default</th> 
    <th>Description</th> 
  </tr>
  <tr>
    <td>USE_TEMP_DIR</td>
    <td>True/False</td> 
    <td>False</td> 
    <td>If true, all instance-files related to solving EMPIRE is stored in the directory defined by temp_dir (see below). This is useful when running a large instance of EMPIRE to avoid memory problems. </td> 
  </tr>
  <tr>
    <td>temp_dir</td>
    <td>String</td>
    <td>'./'</td>
    <td>The path to which temporary files will be stored if USE_TEMP_DIR = True; .lp-file is stored if WRITE_LP = True; and .plk-file is stored if PICKLE_INSTANCE = True. </td>
  </tr>
  <tr>
    <td>version</td>
    <td>String</td>
    <td>'europe_v50'</td>
    <td>The name of the version to be run. Note that this is the folder-name containing input data in ‘Data handler’. </td>
  </tr>
  <tr>
    <td>Horizon</td>
    <td>Integer</td>
    <td>2060</td>
    <td>The last strategic (investment) period used in the optimization run. </td>
  </tr>
  <tr>
    <td>NoOfScenarios</td>
    <td>Integer</td>
    <td>3</td>
    <td>The number of scenarios in every investment period.  </td>
  </tr>
  <tr>
    <td>lengthRegSeason</td>
    <td>Integer</td>
    <td>168</td>
    <td>The number of hours to use in a regular season for optimization of system operation in every investment period. </td>
  </tr>
  <tr>
    <td>discountrate</td>
    <td>Float</td>
    <td>0.05</td>
    <td>The discount rate. </td>
  </tr>
  <tr>
    <td>WACC</td>
    <td>Float</td>
    <td>0.05</td>
    <td>The weighted average cost of capital (WACC). </td>
  </tr>
  <tr>
    <td>solver</td>
    <td>String</td>
    <td>"Xpress"</td>
    <td>Specifies the solver. Options: “Xpress”, “Gurobi”, “CPLEX”. </td>
  </tr>
  <tr>
    <td>scenariogeneration</td>
    <td>True/False</td>
    <td>True</td>
    <td>If true, new operational scenarios will be generated. NB! If false, .tab-files or sampling key must be manually added to the ‘ScenarioData’-folder in the version. </td>
  </tr>
  <tr>
    <td>fix_sample</td>
    <td>True/False</td>
    <td>False</td>
    <td>If true, new operational scenarios will be generated. NB! If false, .tab-files or sampling key must be manually added to the ‘ScenarioData’-folder in the version. </td>
  </tr>
  <tr>
    <td>EMISSION_CAP</td>
    <td>True/False</td>
    <td>True</td>
    <td>If true, emissions in every scenario are capped according to the specified cap in ‘General.xlsx’. If false, the CO2-price specified in ‘General.xlsx’ applies. </td>
  </tr>
  <tr>
    <td>IAMC_PRINT</td>
    <td>True/False</td>
    <td>True</td>
    <td>If true, selected results are printed on the standard IAMC-format in addition to the normal EMPIRE print. </td>
  </tr>
  <tr>
    <td>WRITE_LP</td>
    <td>True/False</td>
    <td>False</td>
    <td>If true, the solver-file will be saved. Useful for debugging.  </td>
  </tr>
  <tr>
    <td>PICKLE_INSTANCE</td>
    <td>True/False</td>
    <td>False</td>
    <td>If true, instance will be saved/pickled. Useful for printing alternative results. </td>
  </tr>
  
</table>

# Test Run
Note that building the instance in Pyomo for a base case of EMPIRE can take around 40 min. Therefore, it is good to run the ‘test_run.py’ first to confirm whether your computer or cluster connects to the preferred solver or not.

# Running
When all Pyomo and the preferred solver has been installed, the model is run by running the script ‘run.py’ in a Python interface. The code is run by using the following commands:

C:\Users\name> cd <path_to_folder>   

C:\Users\name\path_to_folder> python run.py 
