from Input_Script import read_file
from Input_Script import read_sets

# Reading Excel workbooks using our function read_file

read_sets('Sets.xlsx', 'Nodes')
read_sets('Sets.xlsx', 'Times')
read_sets('Sets.xlsx', 'LineType')
read_sets('Sets.xlsx', 'Technology')
read_sets('Sets.xlsx', 'Storage')
read_sets('Sets.xlsx', 'Generators')
read_file('Sets.xlsx', 'HourOfSeason', [0, 1])
read_file('Sets.xlsx', 'StorageOfNodes', [0, 1])
read_file('Sets.xlsx', 'GeneratorsOfNode', [0, 1])
read_file('Sets.xlsx', 'GeneratorsOfTechnology', [0, 1])
read_file('Sets.xlsx', 'DirectionalLines', [0, 1])
read_file('Sets.xlsx', 'LineTypeOfDirectionalLines', [0, 1, 2])

# Reading GeneratorPeriod
read_file('Generator.xlsx', 'FixedOMCosts', [0, 1, 2])
read_file('Generator.xlsx', 'CapitalCosts', [0, 1, 2])
read_file('Generator.xlsx', 'VariableOMCosts', [0, 1])
read_file('Generator.xlsx', 'FuelCosts', [0, 1, 2])
read_file('Generator.xlsx', 'CCSCostTSVariable', [0, 1])
read_file('Generator.xlsx', 'Efficiency', [0, 1, 2])
read_file('Generator.xlsx', 'RefInitialCap', [0, 1, 2])
read_file('Generator.xlsx', 'ScaleFactorInitialCap', [0, 1, 2])
read_file('Generator.xlsx', 'InitialCapacity', [0, 1, 2, 3])
read_file('Generator.xlsx', 'MaxBuiltCapacity', [0, 1, 2, 3])
read_file('Generator.xlsx', 'MaxInstalledCapacity', [0, 1, 2])
read_file('Generator.xlsx', 'RampRate', [0, 1])
read_file('Generator.xlsx', 'GeneratorTypeAvailability', [0, 1])
read_file('Generator.xlsx', 'CO2Content', [0, 1])
read_file('Generator.xlsx', 'Lifetime', [0, 1])

#Reading InterConnector
read_file('Transmission.xlsx', 'lineEfficiency', [0, 1, 2])
read_file('Transmission.xlsx', 'MaxInstallCapacityRaw', [0, 1, 2, 3])
read_file('Transmission.xlsx', 'MaxBuiltCapacity', [0, 1, 2, 3])
read_file('Transmission.xlsx', 'Length', [0, 1, 2])
read_file('Transmission.xlsx', 'TypeCapitalCost', [0, 1, 2])
read_file('Transmission.xlsx', 'TypeFixedOMCost', [0, 1, 2])
read_file('Transmission.xlsx', 'InitialCapacity', [0, 1, 2, 3])
read_file('Transmission.xlsx', 'Lifetime', [0, 1, 2])

#Reading Node
read_file('Node.xlsx', 'ElectricAnnualDemand', [0, 1, 2])
read_file('Node.xlsx', 'NodeLostLoadCost', [0, 1, 2])

#Reading Season
read_file('General.xlsx', 'seasonScale', [0, 1])
read_file('General.xlsx', 'CO2Cap', [0, 1])
read_file('General.xlsx', 'CO2Price', [0, 1])

#Reading Stochastic
read_file('Stochastic.xlsx', 'StochasticAvailability', [0, 1, 2, 3, 4])
read_file('Stochastic.xlsx', 'ElectricLoadRaw', [0, 1, 2, 3])
read_file('Stochastic.xlsx', 'HydroGenMaxSeasonalProduction', [0, 1, 2, 3, 4])
read_file('Stochastic.xlsx', 'HydroGenMaxAnnualProduction', [0, 1])

#Reading Storage
read_file('Storage.xlsx', 'StorageBleedEfficiency', [0, 1])
read_file('Storage.xlsx', 'StorageChargeEff', [0, 1])
read_file('Storage.xlsx', 'StorageDischargeEff', [0, 1])
read_file('Storage.xlsx', 'StoragePowToEnergy', [0, 1])
read_file('Storage.xlsx', 'StorageInitialEnergyLevel', [0, 1])
read_file('Storage.xlsx', 'InitialPowerCapacity', [0, 1, 2, 3])
read_file('Storage.xlsx', 'PowerCapitalCost', [0, 1, 2])
read_file('Storage.xlsx', 'PowerFixedOMCost', [0, 1, 2])
read_file('Storage.xlsx', 'PowerMaxBuiltCapacity', [0, 1, 2, 3])
read_file('Storage.xlsx', 'EnergyCapitalCost', [0, 1, 2])
read_file('Storage.xlsx', 'EnergyFixedOMCost', [0, 1, 2])
read_file('Storage.xlsx', 'EnergyInitialCapacity', [0, 1, 2, 3])
read_file('Storage.xlsx', 'EnergyMaxBuiltCapacity', [0, 1, 2, 3])
read_file('Storage.xlsx', 'EnergyMaxInstalledCapacity', [0, 1, 2])
read_file('Storage.xlsx', 'PowerMaxInstalledCapacity', [0, 1, 2])
read_file('Storage.xlsx', 'Lifetime', [0, 1])