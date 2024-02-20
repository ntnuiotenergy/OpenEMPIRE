from pathlib import Path

import openpyxl

from .sheets_structure import sheets


def create_empty_empire_dataset(path: Path):
    path.mkdir(parents=True)
    for wb_name in sheets:
        wb = openpyxl.Workbook()
        # Remove the default sheet
        default_sheet = wb.active
        wb.remove(default_sheet)

        for sheet_name in sheets[wb_name]:
            wb.create_sheet(title=sheet_name)
        wb.save(path / f"{wb_name}.xlsx")
