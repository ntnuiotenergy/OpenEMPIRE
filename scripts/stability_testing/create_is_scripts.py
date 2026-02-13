### CHANGE THIS ###
# You can use the 'In-sample'-tab in the file 'Stability_tests_setup.xlsx to define the methods you want to test
# and the Solstorm-nodes if you want to do several runs in parallell

SOLSTORM_USER = "" # Your username on Solstorm

run_table = """
#run	Node	Metode	Scenarier	Instanser	Tidsbruk (dager)		Instans fra	Instans til
1	6-1	basic	100	5	0.8		1	5
2	6-2	basic	100	5	0.8		6	10
3	6-3	basic	100	5	0.8		11	15
4	6-4	basic	100	5	0.8		16	20
5	6-5	basic	100	5	0.8		21	25
6	6-6	basic	100	5	0.8		26	30
7	6-7	moment	100	5	0.8		1	5
8	6-8	moment	100	5	0.8		6	10
9	6-9	moment	100	5	0.8		11	15
10	6-10	moment	100	5	0.8		16	20
11	6-11	moment	100	5	0.8		21	25
12	6-12	moment	100	5	0.8		26	30
13	6-13	filter	100	5	0.8		1	5
14	6-14	filter	100	5	0.8		6	10
15	6-15	filter	100	5	0.8		11	15
16	6-16	filter	100	5	0.8		16	20
17	6-17	filter	100	5	0.8		21	25
18	6-18	filter	100	5	0.8		26	30
19	6-19	copula	100	5	0.8		1	5
20	6-20	copula	100	5	0.8		6	10
21	6-21	copula	100	5	0.8		11	15
22	6-22	copula	100	5	0.8		16	20
23	6-23	copula	100	5	0.8		21	25
24	6-24	copula	100	5	0.8		26	30
"""

# Generate shell script files for each run
for line in run_table.split('\n')[1:]:
    if line.strip() == '':
        continue
    parts = line.split()
    try:
        run_id = int(parts[0])
        copula_type = parts[2]
    except ValueError:
        continue  # Skip header and other non-integer lines
    node = parts[1]  # Extract node number
    # Create a shell script content for each run
    script_content = f"""\
#!/bin/bash

screen -S run-{copula_type}-{run_id}
ssh compute-{node}

module load Python/3.11.5-GCCcore-13.2.0
module load gurobi
cd ../../storage/users/{SOLSTORM_USER}/OpenEMPIRE
python -m scripts.stability_testing.run_in_sample_{run_id}
"""
    # Write the content to a file
    with open(f"run_script_{run_id}.sh", "w") as f:
        f.write(script_content)

print("Script files generated successfully.")
