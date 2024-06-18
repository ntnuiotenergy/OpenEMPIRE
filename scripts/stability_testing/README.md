# Stability testing: User guide

The scripts in this folder can be used for testing the stability of scenario generation routines (SGRs) with in-sample and out-of-sample tests.

### How to: 

1. Create the out-of-sample reference (scenario) tree using 'create_out_of_sample_tree.py'. Here you specify the number of subtrees in the reference tree and the number of scenarios per subtree. This is done to overcome potential memory restrictions and allow for parallellization. If you diverge from using 10 subtrees with 60 scenarios, you need to update the parameters in 'run_oos_1.py'.

2. Create the scripts for in-sample runs using the file 'create_is_runs.py'. You can use the Excel-file 'Stability_tests_setup.xlsx' to define the methods you want to test. Here you can also specifiy the number of instances to be used for assessing stability, and the nodes to be used in Solstorm if you want to do multiple runs in parallell to speed up the process. In addition, it gives an indication of the runtime given your parallellization configuration. Copy the Excel-table into 'run_table' in 'create_is_runs.py' and 'create_is_scripts.py'. This will create separate files for running the specified number of instances of the SGR (based on the rows in the Excel-table). Thereafter you can run the file 'create_is_scripts.py' (add your username in this file) to generate commands that can be pasted into the terminal for running the scripts on Solstorm. The output for each instance is found in 'Results/run_in_sample/...".

3. After the in-sample runs are finished, you can do out-of-sample-testing. Similarly, use 'Stability_tests_setup.xlsx' to define the (possibly same) methods you want to test. Note here that the integers for n_cluster (in strata and copula-methods) and n_tree_compare (in moment method) are added to the end of method names. Copy the Excel-table into 'run_table' in 'create_oos_runs.py' and 'create_oos_scripts.py'. This will create separate files for running out-of-sample tests on the specified number of instances of the SGR (based on the rows in the Excel-table). Thereafter you can run the file 'create_oos_scripts.py' (add your username in this file) to generate commands that can be pasted into the terminal for running the scripts on Solstorm. The out-of-sample output for each instance is found in a subfolder 'OutOfSample' at the original destination. Simplified output of only objective function values across all methods will be displayed in an outer parent folder named 'OutOfSample'. 

4. After all results are obtained from the tests, you can navigate to 'plots/stability_tests.ipynb' to generate plots and tables that can be used to access the stability performance. Before this, you should run 'get_relevant_output_files.py' to only consider the relevant in-sample output files (you can specify excl. e.g. large Operational-files). The relevant output files will be copied into an outer parent folder named 'NewResults/in-sample/...". This is done to reduce memory if you want to save or analyze the results locally.