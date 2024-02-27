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
EMPIRE consists of a programming script used to run the model: 

<b>	scripts/run.py:</b> The main script used to run EMPIRE. This is the only script a user of EMPIRE needs to use and potentially modify.  

**Note:** The main run-script (scipts/run.py), can run a small test instance of EMPIRE that usually finishes in 1-2 min. A normal test instance requires around 140 GB RAM and thus needs to be run on a high performance cluster (HPC). 

The run script uses the empire package that consists of these core modules:

<b>(1)	empire.py:</b> Contains the abstract formulation of EMPIRE in Pyomo. This script also contains code related to printing the results.

<b>(2)	scenario_random.py:</b> Generates random operational scenarios as .tab-files through sampling.

<b>(3)	reader.py:</b> Generates .tab-files input based on data provided in Excel workbooks. 

<b>(4)	config.py:</b> Defines two configuration objects used by Empire.

<b>(5)	model_runner.py:</b> Methods used for setting up an Empire run.

In addition there are modules containing input and output clients, that can be used to read and alter input data, and read ouput/results data. 

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
    <td>use_temporary_directory</td>
    <td>True/False</td> 
    <td>False</td> 
    <td>If true, all instance-files related to solving EMPIRE is stored in the directory defined by temporary_directory (see below). This is useful when running a large instance of EMPIRE to avoid memory problems. </td> 
  </tr>
  <tr>
    <td>temporary_directory</td>
    <td>String</td>
    <td>'./'</td>
    <td>The path to which temporary files will be stored if use_temporary_directory = True; .lp-file is stored if write_in_lp_format = True; and .plk-file is stored if serialize_instance = True. </td>
  </tr>
  <tr>
    <td>forecast_horizon_year</td>
    <td>Integer</td>
    <td>2060</td>
    <td>The last strategic (investment) period used in the optimization run. </td>
  </tr>
  <tr>
    <td>number_of_scenarios</td>
    <td>Integer</td>
    <td>3</td>
    <td>The number of scenarios in every investment period.  </td>
  </tr>
  <tr>
    <td>length_of_regular_season</td>
    <td>Integer</td>
    <td>168</td>
    <td>The number of hours to use in a regular season for optimization of system operation in every investment period. </td>
  </tr>
  <tr>
    <td>discount_rate</td>
    <td>Float</td>
    <td>0.05</td>
    <td>The discount rate. </td>
  </tr>
  <tr>
    <td>wacc</td>
    <td>Float</td>
    <td>0.05</td>
    <td>The weighted average cost of capital (WACC). </td>
  </tr>
  <tr>
    <td>optimization_solver</td>
    <td>String</td>
    <td>"Xpress"</td>
    <td>Specifies the solver. Options: “Xpress”, “Gurobi”, “CPLEX”. </td>
  </tr>
  <tr>
    <td>use_scenario_generation</td>
    <td>True/False</td>
    <td>True</td>
    <td>If true, new operational scenarios will be generated. NB! If false, .tab-files or sampling key must be manually added to the ‘ScenarioData’-folder in the version. </td>
  </tr>
  <tr>
    <td>use_fixed_sample</td>
    <td>True/False</td>
    <td>False</td>
    <td>If true, operational scenarios will be generated according to a fixed sampling key located in the ‘ScenarioData’-folder to ensure the same operational scenarios are generated. </td>
  </tr>
    <tr>
    <td>load_change_module</td>
    <td>True/False</td>
    <td>False</td>
    <td> </td>
  </tr>
    <tr>
    <td>filter_make</td>
    <td>True/False</td>
    <td>False</td>
    <td> </td>
  </tr>
    <tr>
    <td>filter_use</td>
    <td>True/False</td>
    <td>False</td>
    <td> </td>
  </tr>
    <tr>
    <td>n_cluster</td>
    <td>Integer</td>
    <td>10</td>
    <td> </td>
  </tr>
    <tr>
    <td>moment_matching</td>
    <td>True/False</td>
    <td><False/td>
    <td> </td>
  </tr>
  <tr>
    <td>n_tree_compare</td>
    <td>Integer</td>
    <td>20</td>
    <td> </td>
  </tr>
  <tr>
    <td>use_emission_cap</td>
    <td>True/False</td>
    <td>True</td>
    <td>If true, emissions in every scenario are capped according to the specified cap in ‘General.xlsx’. If false, the CO2-price specified in ‘General.xlsx’ applies. </td>
  </tr>
  <tr>
    <td>print_in_iamc_format</td>
    <td>True/False</td>
    <td>True</td>
    <td>If true, selected results are printed on the standard IAMC-format in addition to the normal EMPIRE print. </td>
  </tr>
  <tr>
    <td>write_in_lp_format</td>
    <td>True/False</td>
    <td>False</td>
    <td>If true, the solver-file will be saved. Useful for debugging.  </td>
  </tr>
  <tr>
    <td>serialize_instance</td>
    <td>True/False</td>
    <td>False</td>
    <td>If true, instance will be saved/pickled. Useful for printing alternative results. </td>
  </tr>
  <tr>
    <td>north_sea</td>
    <td>True/False</td>
    <td>False</td>
    <td>Whether the north sea is modelled or not. </td>
  </tr>
</table>


# Test Run

**System Requirements:** Running the base case of EMPIRE in Pyomo typically takes about 40 minutes and requires approximately 140 GB of RAM. 

**Initial Test:** To ensure your setup is correctly configured, start with a test run using a smaller dataset. This test checks if your computer or cluster can successfully connect to the preferred solver.

Run the test using the following command:

```shell
C:\Users\name\path_to_folder> python scripts/run.py -d test
```

**No-Optimization Test**: To execute a test run without performing optimization, use:

```python
C:\Users\name\path_to_folder> python scripts/run.py --test-run -d test
```

This can be useful for verifying basic setup and data handling without engaging the full optimization process.

# Running

**Setup Requirements:** Ensure that Pyomo and the preferred solver are installed.

**Execution:** Run the model using the `run.py` script. Specify the dataset located in the Data Handler folder. For example, to run the model with the `europe_v51` dataset, use:

```python
C:\Users\name\path_to_folder> python scripts/run.py -d europe_v51
```

# Running on a High-Performance Cluster (HPC)
**Example Script**: For running multiple cases on an HPC, refer to the script `scripts/copy_and_run_empire_on_hpc.sh`. This script uses configurations from config/cluster.json and is designed for NTNU's HPC clusters: Solstorm and Idun.

**Usage Linux or macOS**: From the project directory, execute the following to run on the Solstorm cluster:

```shell
sh scripts/copy_and_run_empire_on_hpc.sh Solstorm
```

**Usage Windows**: Install "jq" on Windows: 
```shell
curl -L -o /usr/bin/jq.exe https://github.com/stedolan/jq/releases/latest/download/jq-win64.exe
```
From the project directory, execute the following command in Git Bash to run on the Solstorm cluster: 
```shell
sh scripts/copy_and_run_empire_on_hpc.sh Solstorm
```  
  
This command copies the EMPIRE code to the Solstorm cluster and performs several runs managed by the SGE task manager. Ensure the "empire_env" conda environment is set up on the cluster with dependencies as listed in `environment.yml`.

The `scripts/run_analysis.py` script demonstrates how to modify input data at execution time using data managers.

# Contributing

We welcome any contribution the OpenEMPIRE, whether it is fixing a bug, adding a new feature, or improving documentation, your help is appreciated. For more information, see [CONTRIBUTING](.github/CONTRIBUTING.md).