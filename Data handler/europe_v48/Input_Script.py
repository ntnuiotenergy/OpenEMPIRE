import xlrd
import pandas as pd
from openpyxl import load_workbook

# Reading the whole workbook


# Function description: read column value from excel sheet and save as .tab file "sheet.tab"
# Input: excel name, sheet name, the number of columns to be read
# Output:  .tab file
def read_file(excel, sheet, columns):
    input_excel = pd.ExcelFile(excel)
    input_sheet = pd.read_excel(input_excel, sheet, skiprows=2)

    data_table = input_sheet.iloc[:, columns]
    data_table.columns = pd.Series(data_table.columns).str.replace(' ', '_')
    data_nonempty = data_table.dropna()

    save_csv_frame = pd.DataFrame(data_nonempty)

    save_csv_frame.replace('\s', '', regex=True, inplace=True)

    save_csv_frame.to_csv('Tab_Files/'+ excel.replace(".xlsx", "_") + sheet + '.tab', header=True, index=None, sep='\t', mode='w')
    #print(excel.replace(".xlsx", "_") + sheet + '.tab')
    input_excel.close()


def read_sets(excel, sheet):
    input_excel = pd.ExcelFile(excel)
    input_sheet = pd.read_excel(input_excel, sheet)

    for ind, column in enumerate(input_sheet.columns):
        data_table = input_sheet.iloc[:, ind]
        data_nonempty = data_table.dropna()
        data_nonempty.replace(" ", "")
        save_csv_frame = pd.DataFrame(data_nonempty)
        save_csv_frame.replace('\s', '', regex=True, inplace=True)
        save_csv_frame.to_csv('Tab_Files/' + excel.replace(".xlsx", "_") + column + '.tab', header=[column], index=None, sep='\t', mode='w')

    input_excel.close()



