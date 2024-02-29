import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

def read_file(excelfile: pd.ExcelFile, sheet: str, columns: list, 
              tab_file_path: Path, filename: str, skipheaders: int = 0) -> None:
    """
    Reads data from an Excel file and saves it as a .tab file.
    
    :param excelfile: The Excel file object.
    :param sheet: The name of the sheet to read from.
    :param columns: List of columns to be read.
    :param tab_file_path: Path to save the .tab file.
    :param filename: Base name for the .tab file.
    :param skipheaders: Number of header rows to skip. Defaults to 0.
    """
    logger.info("Reading %s sheet from %s.xlsx", sheet, filename)

    input_sheet = excelfile[sheet]

    # Modify the columns' header
    input_sheet.columns = pd.Series(input_sheet.iloc[skipheaders-1]).str.replace(' ', '_')

    # Remove the extra rows and columns
    data_table = input_sheet.iloc[skipheaders:, columns]

    # Filter the dataframe to remove unwanted investment periods and nodes.
    data_table = filter_input(data_table)

    # Remove the rows that contains NULL values
    data_nonempty = data_table.dropna()

    save_csv_frame = pd.DataFrame(data_nonempty)
    save_csv_frame.replace('\s', '', regex=True, inplace=True)

    tab_file_path.mkdir(parents=True, exist_ok=True)
    save_csv_frame.to_csv(tab_file_path / f"{filename}_{sheet}.tab", header=True, index=None, sep='\t', mode='w')

def read_sets(excelfile: pd.ExcelFile, sheet: str, tab_file_path: Path, 
              filename: str) -> None:
    """
    Reads sets data from an Excel file and saves each column as a separate .tab file.
    
    :param excelfile: The Excel file object.
    :param sheet: The name of the sheet to read from.
    :param tab_file_path: Path to save the .tab files.
    :param filename: Base name for the .tab files.
    """
    logger.info("Reading %s sheet from %s.xlsx", sheet, filename)

    # Read the Excel sheet passed to this function from the input files
    input_sheet = excelfile[sheet]

    # Filter the input to remove unwanted investment periods and nodes.
    input_sheet = filter_input(input_sheet)

    for ind, column in enumerate(input_sheet.columns):
        data_table = input_sheet.iloc[0:, ind]
        data_nonempty = data_table.dropna()
        data_nonempty.replace(" ", "")
        save_csv_frame = pd.DataFrame(data_nonempty)
        save_csv_frame.replace('\s', '', regex=True, inplace=True)
        tab_file_path.mkdir(parents=True, exist_ok=True)
        save_csv_frame.to_csv(tab_file_path / f"{filename}_{column}.tab", header=True, index=None, sep='\t', mode='w')        

def filter_input(df):
    """
    Arg: DataFrame with parameter/set information + selection/slicing criteria
    Returns: filtered DataFrame
    """
    
    remove_periods = filter_input_glo["remove_periods"]
    if remove_periods:
        if 'Period' in df.columns:
            df = df[~df.Period.isin(remove_periods)]
        elif 'Periods' in df.columns:
            df = df[~df.Periods.isin(remove_periods)]
        elif 'Horizon' in df.columns:
            df = df[~df.Horizon.isin(remove_periods)]
    return df

def generate_tab_files(file_path, tab_file_path, DLCMODULE, DataFilters):
    """
    Read column value from excel sheet and save as .tab file "sheet.tab"

    :param file_path: Path to the dataset.
    :param tab_file_path: Path to save the .tab files.
    """
    
    logger.info("Generating .tab-files...")

    # Creating global variable for filtering the inputs
    global filter_input_glo
    filter_input_glo = DataFilters

    # Reading Excel workbooks using our function read_file

    if not os.path.exists(tab_file_path):
        os.makedirs(tab_file_path)

    logger.info("Reading Sets.xlsx")
    SetsExcelData = pd.read_excel(file_path / "Sets.xlsx", sheet_name=None)
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
    logger.info("Reading Generator.xlsx")
    GeneratorExcelData = pd.read_excel(file_path / "Generator.xlsx", sheet_name=None)
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
    logger.info("Reading Transmission.xlsx")
    TransmissionExcelData = pd.read_excel(file_path / "Transmission.xlsx", sheet_name=None)
    read_file(TransmissionExcelData, 'lineEfficiency', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'MaxInstallCapacityRaw', [0, 1, 2, 3], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'MaxBuiltCapacity', [0, 1, 2, 3], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'Length', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'TypeCapitalCost', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'TypeFixedOMCost', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'InitialCapacity', [0, 1, 2, 3], tab_file_path,  "Transmission", skipheaders=2)
    read_file(TransmissionExcelData, 'Lifetime', [0, 1, 2], tab_file_path,  "Transmission", skipheaders=2)

    #Reading Node
    logger.info("Reading Node.xlsx")
    NodeExcelData = pd.read_excel(file_path / "Node.xlsx", sheet_name=None)
    read_file(NodeExcelData , 'ElectricAnnualDemand', [0, 1, 2],tab_file_path,  "Node", skipheaders=2)
    read_file(NodeExcelData , 'NodeLostLoadCost', [0, 1, 2],tab_file_path,  "Node", skipheaders=2)
    read_file(NodeExcelData , 'HydroGenMaxAnnualProduction', [0, 1],tab_file_path,  "Node", skipheaders=2)

    #Reading Season
    logger.info("Reading General.xlsx")
    GeneralExcelData = pd.read_excel(file_path / "General.xlsx", sheet_name=None)
    # read_file(GeneralExcelData, 'seasonScale', [0, 1], tab_file_path, "General", skipheaders=2)
    read_file(GeneralExcelData, 'CO2Cap', [0, 1], tab_file_path, "General", skipheaders=2)
    read_file(GeneralExcelData, 'CO2Price', [0, 1], tab_file_path, "General", skipheaders=2)
    
    #Reading Storage
    logger.info("Reading Storage.xlsx")
    StorageExcelData = pd.read_excel(file_path / "Storage.xlsx", sheet_name=None)
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

    if DLCMODULE:
        logger.info("Reading DLCSets.xlsx")
        # Reading DLC sets
        DLCSetExcelData = pd.read_excel(file_path / "DLCModule/DLCSets.xlsx", sheet_name=None)
        read_sets(DLCSetExcelData, 'Storage', tab_file_path / "DLCModule", "DLCSets")
        read_file(DLCSetExcelData, 'StorageOfNodes', [0, 1], tab_file_path / "DLCModule", "DLCSets", skipheaders=2)
        # Reading DR storage specifications
        logger.info("Reading DLCStorage.xlsx")
        DLCSetExcelData = pd.read_excel(file_path / "DLCModule/DLCStorage.xlsx", sheet_name=None)
        read_file(DLCSetExcelData, 'StorageBleedEfficiency', [0, 1], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'StorageChargeEff', [0, 1], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'StorageDischargeEff', [0, 1], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'StoragePowToEnergy', [0, 1], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'StorageInitialEnergyLevel', [0, 1], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'InitialPowerCapacity', [0, 1, 2, 3], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'PowerCapitalCost', [0, 1, 2], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'PowerFixedOMCost', [0, 1, 2], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'PowerMaxBuiltCapacity', [0, 1, 2, 3], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'EnergyCapitalCost', [0, 1, 2], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'EnergyFixedOMCost', [0, 1, 2], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'EnergyInitialCapacity', [0, 1, 2, 3], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'EnergyMaxBuiltCapacity', [0, 1, 2, 3], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'EnergyMaxInstalledCapacity', [0, 1, 2], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'PowerMaxInstalledCapacity', [0, 1, 2], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'Lifetime', [0, 1], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)
        read_file(DLCSetExcelData, 'ActivationCost', [0, 1, 2, 3], tab_file_path / "DLCModule", "DLCStorage", skipheaders=2)