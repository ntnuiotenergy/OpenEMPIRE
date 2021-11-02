from dataclasses import dataclass
from abc import ABC, abstractmethod
import pandas as pd
import json
from typing import List
from pathlib import Path

@dataclass
class Data:
    reader: str = None
    reader_config: dict = None
    path: str = None
    exist: bool = True
    
    def check_exist(self) -> None:
        file = Path(self.path)
        if file.is_file():
            self.exist = True
        raise Exception("Does not exist.")
    
    def fetch_data(self):
        #if self.check_exist():
        if self.reader == 'excel':
            return pd.read_excel(io=self.path, **self.reader_config)
        return pd.read_csv(self.path)
            
        
class AggregationStrategy(ABC):
    
    @abstractmethod
    def sum(self, data: pd.DataFrame):
        pass
    
    @abstractmethod
    def average(self, data: pd.DataFrame):
        pass
    
@dataclass
class VerticalAggregationStrategy(AggregationStrategy):
    group_by_cols: list[str] = None
    agg_col: str = None
    transmission: bool = False
    
    def sum(self, data: pd.DataFrame, supernodes: dict[str]):
        return self.aggregate(data, supernodes).sum(self.agg_col)
    
    def average(self, data: pd.DataFrame, supernodes: dict[str]):
        return self.aggregate(data, supernodes).mean(self.agg_col)
    
    def aggregate(self, data: pd.DataFrame, supernodes: dict[str]):
        data[self.group_by_cols[0]] = data[self.group_by_cols[0]].apply(lambda x: self.map_supernode(x, supernodes))
        if self.transmission:
            data[self.group_by_cols[1]] = data[self.group_by_cols[1]].apply(lambda x: self.map_supernode(x, supernodes))
        return data.groupby(self.group_by_cols, as_index=False)
    
    def map_supernode(self, node, supernodes: dict):
        for supernode, child_nodes in supernodes.items():
            if node in child_nodes:
                return supernode
        return node
    
@dataclass
class HorizontalAggregationStrategy(AggregationStrategy):
    
    def sum(self, data: pd.DataFrame, supernodes: dict[str]):
        supernodes = self.alpha2(supernodes)
        for supernode, nodes in supernodes.items():
            data[supernode] = data[nodes].sum(axis=1)
            data.drop(nodes, axis=1, inplace=True)
        return data
    
    def average(self, data: pd.DataFrame, supernodes: dict[str]):
        supernodes = self.alpha2(supernodes)
        for supernode, nodes in supernodes.items():
            data[supernode] = data[nodes].mean(axis=1)
            data.drop(nodes, axis=1, inplace=True)
        return data
    
    def alpha2(self, supernodes: dict):
        with open('config/alpha2.json') as f:
            alpha2_dict = json.load(f)
        return {supernode : [alpha2_dict.get(node, node) 
                             for node in child_nodes] for supernode, child_nodes in supernodes.items()}
        
    
class Aggregator:
    def __init__(self, data: Data, aggregation_strategy: AggregationStrategy, supernodes: dict):
        self.data = data
        self.aggregation_strategy = aggregation_strategy
        self.supernodes = supernodes
    
    def sum(self):
        return self.aggregation_strategy.sum(self.data, self.supernodes)
    
    def average(self):
        return self.aggregation_strategy.average(self.data, self.supernodes)
        

def main() -> None:
    supernodes = {
        'Nordics': ['NO1', 'Sweden', 'Denmark'],
        'Europe': ['France', 'Germany'],
        'Baltics': ['Romania', 'Poland'],
    }
    with open('config/reader_config.json') as f:
        reader_config = json.load(f)
        
    for config in reader_config:
        if config['reader'] == 'excel':
            data = Data(config['reader'], config['reader_config'], config['path']).fetch_data()
            aggregator = Aggregator(data, VerticalAggregationStrategy(config['group_by_cols'], config['agg_col']), supernodes)
            print(aggregator.sum())
        elif config['reader'] == 'csv':
            data = Data(reader=config['reader'], path=config['path']).fetch_data()
            aggregator = Aggregator(data, HorizontalAggregationStrategy(), supernodes)
            print(aggregator.sum())

if __name__ == '__main__':
    main()