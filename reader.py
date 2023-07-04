import pandas as pd
import os
__author__ = "Stian Backe"
__license__ = "MIT"
__maintainer__ = "Stian Backe"
__email__ = "stian.backe@ntnu.no"


def read_file(excelfile, sheet, columns, tab_file_path, filename, skipheaders=0):
    #input_sheet = pd.read_excel(filepath + "/" +excel, sheet, skiprows=2)

    input_sheet = excelfile[sheet]
    data_table = input_sheet.iloc[skipheaders:, columns]
    data_table.columns = pd.Series(data_table.columns).str.replace(' ', '_')
    data_nonempty = data_table.dropna()

    save_csv_frame = pd.DataFrame(data_nonempty)

    save_csv_frame.replace('\s', '', regex=True, inplace=True)

    if not os.path.exists(tab_file_path):
        os.makedirs(tab_file_path)
    #excel = excel.replace(".xlsx", "_")
    #excel = excel.replace("Excel/", "")
    save_csv_frame.to_csv(tab_file_path + "/" + filename + "_" + sheet + '.tab', header=True, index=None, sep='\t', mode='w')
    #save_csv_frame.to_csv(excel.replace(".xlsx", '_') + sheet + '.tab', header=True, index=None, sep='\t', mode='w')

def read_sets(excelfile, sheet, tab_file_path, filename, skipheaders=0):
    
    input_sheet = excelfile[sheet]

    for ind, column in enumerate(input_sheet.columns):
        data_table = input_sheet.iloc[0:, ind]
        data_nonempty = data_table.dropna()
        data_nonempty.replace(" ", "")
        save_csv_frame = pd.DataFrame(data_nonempty)
        save_csv_frame.replace('\s', '', regex=True, inplace=True)
        if not os.path.exists(tab_file_path):
            os.makedirs(tab_file_path)
        #excel = excel.replace(".xlsx", "_")
        #excel = excel.replace("Excel/", "")
        save_csv_frame.to_csv(tab_file_path + "/" + filename + "_" + column + '.tab', header=True, index=None, sep='\t', mode='w')
        #save_csv_frame.to_csv(excel.replace(".xlsx", '_') + column + '.tab', header=True, index=None, sep='\t', mode='w')

def generate_tab_files(filepath, tab_file_path):
    # Function description: read column value from excel sheet and save as .tab file "sheet.tab"
    # Input: excel name, sheet name, the number of columns to be read
    # Output:  .tab file
    
    print("Generating .tab-files...")

    # Reading Excel workbooks using our function read_file

    if not os.path.exists(tab_file_path):
        os.makedirs(tab_file_path)

    SetsExcelData = pd.read_excel(filepath + "/Sets.xlsx", sheet_name=None)
    read_sets(SetsExcelData, 'Nodes', tab_file_path, "Sets")
    read_sets(SetsExcelData, 'OffshoreNodes', tab_file_path, "Sets")
    read_sets(SetsExcelData, 'Horizon', tab_file_path, "Sets")
    read_sets(SetsExcelData, 'LineType', tab_file_path, "Sets")
    read_sets(SetsExcelData, 'Technology', tab_file_path, "Sets")
    read_sets(SetsExcelData, 'Storage', tab_file_path, "Sets")
    read_sets(SetsExcelData, 'Generators', tab_file_path, "Sets")
    read_file(SetsExcelData, 'StorageOfNodes', [0, 1], tab_file_path, "Sets", skipheaders=2)
    read_file(SetsExcelData, 'GeneratorsOfNode', [0, 1], tab_file_path, "Sets", skipheaders=2)
    read_file(SetsExcelData, 'GeneratorsOfTechnology', [0, 1], tab_file_path, "Sets", skipheaders=2)
    read_file(SetsExcelData, 'DirectionalLines', [0, 1], tab_file_path, "Sets", skipheaders=2)
    read_file(SetsExcelData, 'LineTypeOfDirectionalLines', [0, 1, 2], tab_file_path, "Sets", skipheaders=2)

    # Reading GeneratorPeriod
    GeneratorExcelData = pd.read_excel(filepath + "/Generator.xlsx", sheet_name=None)
    read_file(GeneratorExcelData, 'FixedOMCosts', [0, 1, 2], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'CapitalCosts', [0, 1, 2], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'VariableOMCosts', [0, 1], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'FuelCosts', [0, 1, 2], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'CCSCostTSVariable', [0, 1], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'Efficiency', [0, 1, 2], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'RefInitialCap', [0, 1, 2], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'ScaleFactorInitialCap', [0, 1, 2], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'InitialCapacity', [0, 1, 2, 3], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'MaxBuiltCapacity', [0, 1, 2, 3], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'MaxInstalledCapacity', [0, 1, 2], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'RampRate', [0, 1], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'GeneratorTypeAvailability', [0, 1], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'CO2Content', [0, 1], tab_file_path, "Generator", skipheaders=2)
    read_file(GeneratorExcelData, 'Lifetime', [0, 1], tab_file_path, "Generator", skipheaders=2)

    #Reading InterConnector
    TransmissionExcelData = pd.read_excel(filepath + "/Transmission.xlsx", sheet_name=None)
    read_file(TransmissionExcelData, 'lineEfficiency', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'MaxInstallCapacityRaw', [0, 1, 2, 3], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'MaxBuiltCapacity', [0, 1, 2, 3], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'Length', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'TypeCapitalCost', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'TypeFixedOMCost', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'InitialCapacity', [0, 1, 2, 3], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'Lifetime', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)

    #Reading Node
    NodeExcelData = pd.read_excel(filepath + "/Node.xlsx", sheet_name=None)
    read_file(NodeExcelData , 'ElectricAnnualDemand', [0, 1, 2],tab_file_path,  "Node", skipheaders=2)
    read_file(NodeExcelData , 'NodeLostLoadCost', [0, 1, 2],tab_file_path,  "Node", skipheaders=2)
    read_file(NodeExcelData , 'HydroGenMaxAnnualProduction', [0, 1],tab_file_path,  "Node", skipheaders=2)

    #Reading Season
    GeneralExcelData = pd.read_excel(filepath + "/General.xlsx", sheet_name=None)
    read_file(GeneralExcelData, 'seasonScale', [0, 1], tab_file_path, "General", skipheaders=2)
    read_file(GeneralExcelData, 'CO2Cap', [0, 1], tab_file_path, "General", skipheaders=2)
    read_file(GeneralExcelData, 'CO2Price', [0, 1], tab_file_path, "General", skipheaders=2)
    
    #Reading Storage
    StorageExcelData = pd.read_excel(filepath + "/Storage.xlsx", sheet_name=None)
    read_file(StorageExcelData, 'StorageBleedEfficiency', [0, 1], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'StorageChargeEff', [0, 1], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'StorageDischargeEff', [0, 1], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'StoragePowToEnergy', [0, 1], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'StorageInitialEnergyLevel', [0, 1], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'InitialPowerCapacity', [0, 1, 2, 3], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'PowerCapitalCost', [0, 1, 2], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'PowerFixedOMCost', [0, 1, 2], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'PowerMaxBuiltCapacity', [0, 1, 2, 3], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'EnergyCapitalCost', [0, 1, 2], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'EnergyFixedOMCost', [0, 1, 2], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'EnergyInitialCapacity', [0, 1, 2, 3], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'EnergyMaxBuiltCapacity', [0, 1, 2, 3], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'EnergyMaxInstalledCapacity', [0, 1, 2], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'PowerMaxInstalledCapacity', [0, 1, 2], tab_file_path, "Storage", skipheaders=2)
    read_file(StorageExcelData, 'Lifetime', [0, 1], tab_file_path, "Storage", skipheaders=2)
