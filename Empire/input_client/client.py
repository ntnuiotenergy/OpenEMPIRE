import openpyxl

from .excel_structure import sheets

class EmpireInputClient:
    def __init__(self, dataset_path: Path):
        """
        Client used to alter Empire dataset.

        :param filename: Path to the dataset
        """
        self.dataset_path = dataset_path
        self.wb_sets = openpyxl.load_workbook(dataset_path/"Sets.xlsx")
        self.wb_generators = openpyxl.load_workbook(dataset_path /"Generator.xlsx")
        self.wb_nodes = openpyxl.load_workbook(dataset_path / "Node.xlsx")
        self.wb_transmission = openpyxl.load_workbook(dataset_path / "Transmission.xlsx")
        self.wb_storages = openpyxl.load_workbook(dataset_path / "Storage.xlsx")

        self.validate()

        
    def get_nodes(self):
        

    def update_value(self, sheet_name, type_val, investment_period, new_value):
        """Update the 'Value' column based on 'Type' and 'InvestmentPeriod'"""
        ws = self.wb[sheet_name]
        
        for row in ws.iter_rows(min_row=2):  # Assuming 1st row contains headers
            if row[0].value == type_val and row[1].value == investment_period:
                row[2].value = new_value
    
    def validate(self):
        wbs = [
            ("Sets", self.wb_sets), ("Generators", self.wb_generators),
            ("Nodes", self.wb_nodes), ("Transmission", self.wb_transmission),
            ("Storages", self.wb_storages)
        ]
        for name, wb in wbs:
            if wb.sheetnames != sheets[name]:
                raise ValueError(f"Sheetnames of {name} does not match {sheets[name]}") 


# Example usage:
if __name__ == "__main__":
    client = EmpireInputClient('your_file_name.xlsx')
    client.update_value('Sheet1', 'SomeType', '2023', 1000)
    client.save()
