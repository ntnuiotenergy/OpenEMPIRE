import pandas as pd
import os

def read_file(filepath, excel, sheet, columns, tab_file_path):
    input_sheet = pd.read_excel(filepath + "/" +excel, sheet, skiprows=2)

    data_table = input_sheet.iloc[:, columns]
    data_table.columns = pd.Series(data_table.columns).str.replace(' ', '_')
    data_nonempty = data_table.dropna()

    save_csv_frame = pd.DataFrame(data_nonempty)

    save_csv_frame.replace('\s', '', regex=True, inplace=True)

    if not os.path.exists(tab_file_path):
        os.makedirs(tab_file_path)
    #excel = excel.replace(".xlsx", "_")
    #excel = excel.replace("Excel/", "")
    save_csv_frame.to_csv(tab_file_path + "/" + excel.replace(".xlsx", '_') + sheet + '.tab', header=True, index=None, sep='\t', mode='w')
    #save_csv_frame.to_csv(excel.replace(".xlsx", '_') + sheet + '.tab', header=True, index=None, sep='\t', mode='w')

def read_sets(filepath, excel, sheet, tab_file_path):
    input_sheet = pd.read_excel(filepath + "/" + excel, sheet)

    for ind, column in enumerate(input_sheet.columns):
        data_table = input_sheet.iloc[:, ind]
        data_nonempty = data_table.dropna()
        data_nonempty.replace(" ", "")
        save_csv_frame = pd.DataFrame(data_nonempty)
        save_csv_frame.replace('\s', '', regex=True, inplace=True)
        if not os.path.exists(tab_file_path):
            os.makedirs(tab_file_path)
        #excel = excel.replace(".xlsx", "_")
        #excel = excel.replace("Excel/", "")
        save_csv_frame.to_csv(tab_file_path + "/" + excel.replace(".xlsx", '_') + column + '.tab', header=True, index=None, sep='\t', mode='w')
        #save_csv_frame.to_csv(excel.replace(".xlsx", '_') + column + '.tab', header=True, index=None, sep='\t', mode='w')

def generate_tab_files(filepath, tab_file_path, scenariogeneration=True):
    # Function description: read column value from excel sheet and save as .tab file "sheet.tab"
    # Input: excel name, sheet name, the number of columns to be read
    # Output:  .tab file
    
    print("Generating .tab-files...")

    # Reading Excel workbooks using our function read_file

    if not os.path.exists(tab_file_path):
        os.makedirs(tab_file_path)

    read_sets(filepath, 'Sets.xlsx', 'Nodes', tab_file_path = tab_file_path)
    #read_sets(filepath, 'Sets.xlsx', 'Times', tab_file_path = tab_file_path)
    read_sets(filepath, 'Sets.xlsx', 'LineType', tab_file_path = tab_file_path)
    read_sets(filepath, 'Sets.xlsx', 'Technology', tab_file_path = tab_file_path)
    read_sets(filepath, 'Sets.xlsx', 'Storage', tab_file_path = tab_file_path)
    read_sets(filepath, 'Sets.xlsx', 'Generators', tab_file_path = tab_file_path)
    read_file(filepath, 'Sets.xlsx', 'StorageOfNodes', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Sets.xlsx', 'GeneratorsOfNode', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Sets.xlsx', 'GeneratorsOfTechnology', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Sets.xlsx', 'DirectionalLines', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Sets.xlsx', 'LineTypeOfDirectionalLines', [0, 1, 2], tab_file_path = tab_file_path)

    # Reading GeneratorPeriod
    read_file(filepath, 'Generator.xlsx', 'FixedOMCosts', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'CapitalCosts', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'VariableOMCosts', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'FuelCosts', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'CCSCostTSVariable', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'Efficiency', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'RefInitialCap', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'ScaleFactorInitialCap', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'InitialCapacity', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'MaxBuiltCapacity', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'MaxInstalledCapacity', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'RampRate', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'GeneratorTypeAvailability', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'CO2Content', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Generator.xlsx', 'Lifetime', [0, 1], tab_file_path = tab_file_path)

    #Reading InterConnector
    read_file(filepath, 'Transmission.xlsx', 'lineEfficiency', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Transmission.xlsx', 'MaxInstallCapacityRaw', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Transmission.xlsx', 'MaxBuiltCapacity', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Transmission.xlsx', 'Length', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Transmission.xlsx', 'TypeCapitalCost', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Transmission.xlsx', 'TypeFixedOMCost', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Transmission.xlsx', 'InitialCapacity', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Transmission.xlsx', 'Lifetime', [0, 1, 2], tab_file_path = tab_file_path)

    #Reading Node
    read_file(filepath, 'Node.xlsx', 'ElectricAnnualDemand', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Node.xlsx', 'NodeLostLoadCost', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Node.xlsx', 'HydroGenMaxAnnualProduction', [0, 1], tab_file_path = tab_file_path)

    #Reading Season
    read_file(filepath, 'General.xlsx', 'seasonScale', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'General.xlsx', 'CO2Cap', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'General.xlsx', 'CO2Price', [0, 1], tab_file_path = tab_file_path)
    
    #Reading Storage
    read_file(filepath, 'Storage.xlsx', 'StorageBleedEfficiency', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'StorageChargeEff', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'StorageDischargeEff', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'StoragePowToEnergy', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'StorageInitialEnergyLevel', [0, 1], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'InitialPowerCapacity', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'PowerCapitalCost', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'PowerFixedOMCost', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'PowerMaxBuiltCapacity', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'EnergyCapitalCost', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'EnergyFixedOMCost', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'EnergyInitialCapacity', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'EnergyMaxBuiltCapacity', [0, 1, 2, 3], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'EnergyMaxInstalledCapacity', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'PowerMaxInstalledCapacity', [0, 1, 2], tab_file_path = tab_file_path)
    read_file(filepath, 'Storage.xlsx', 'Lifetime', [0, 1], tab_file_path = tab_file_path)