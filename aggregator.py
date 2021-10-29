from reader import read_file
import pandas as pd
from typing import List, Callable
import numpy as np
import json
import itertools

def vert_sum_strat(filtered_data: pd.DataFrame, group_by_cols: List[str], agg_col: str):
    if len(group_by_cols) != 0:
        print(filtered_data.groupby(group_by_cols).sum(agg_col))
        return filtered_data.groupby(group_by_cols).sum(agg_col)
    return pd.DataFrame({agg_col: [filtered_data[agg_col].sum()]})

def vert_mean_strat(filtered_data: pd.DataFrame, group_by_cols: str, agg_col: str):
    return filtered_data.groupby(group_by_cols).mean(agg_col)


def vertical_process_strat(data: pd.DataFrame, s_node:str, child_nodes: List[str], group_by_cols: List[str], agg_col: str, agg_strat: Callable, node_col_name: str = 'Nodes', **kwargs):
    f_data = data[data[node_col_name].isin(child_nodes)]
    agg_data = agg_strat(f_data, group_by_cols, agg_col)
    agg_data[node_col_name] = s_node
    return agg_data

def vertical_comb_strat(data: pd.DataFrame, dfs: List[pd.DataFrame], processed_nodes: List[str], **kwargs):
    # do we need to provide the remaining nodes that are not aggregated?
    return pd.concat(dfs)
    #.append(data[~data['Node'].isin(processed_nodes)])


def horizontal_process_strat(data: pd.DataFrame, s_node, child_nodes: List[str], **kwargs):
    data[s_node] = data[child_nodes].mean(axis=1)
    return data[s_node]

def horizontal_comb_strat(data: pd.DataFrame, rest_cols: List[str], dfs: List[pd.DataFrame], processed_nodes: List[str], **kwargs):
    return_df =  pd.concat(dfs, axis=1)
    return_df[rest_cols] = data[rest_cols]
    return return_df


class SuperNodes:
    def __init__(self, s_nodes: dict, sheet_name: str=None, skiprows: int=None, usecols:List[str]=None):
        self.s_nodes: dict = s_nodes
        self.sheet_name: str = sheet_name
        self.skiprows: int = skiprows
        self.usecols: list = usecols
    
    def load_data(self, file_path):
        if self.sheet_name:
            self.data: pd.DataFrame = pd.read_excel(file_path, self.sheet_name, skiprows=self.skiprows, usecols=self.usecols)
        else:
            self.data = pd.read_csv(file_path)
            
    def construct_super(self, process_strat: Callable, comb_strat: Callable, **kwargs):
        dfs = [process_strat(self.data, s_node, child_nodes, **kwargs) for s_node, child_nodes in self.s_nodes.items()]
        self.processed_data = comb_strat(data=self.data, dfs=dfs, processed_nodes=self.processed_nodes(), **kwargs)
    
    def print_df(self, sheet_name: str=None):
        if self.sheet_name:
            self.processed_data.to_csv(f"nic_test/{self.sheet_name}.csv")
        else:
            self.processed_data.to_csv(f"nic_test/{sheet_name}.csv")
    
    def processed_nodes(self):
        nodes = [value for value in self.s_nodes.values()]
        return list(itertools.chain.from_iterable(nodes))

if __name__ == '__main__':
    def construct_tab_files(agg_config: str, scenario_config: str):
        with open(agg_config) as agg:
            config = json.load(agg)
            for file in config:
                file_path = file['file_path']
                node_name = file['node_name']
                for sheet in file['agg_sheets']:
                    super_node = SuperNodes(
                        {'Nordics': ['NO1', 'Sweden', 'Denmark'], 'Europe': ['France', 'Germany']}, 
                        sheet['sheet_name'], 
                        sheet['skiprows'], 
                        sheet['usecols']
                    )
                    super_node.load_data(file_path)
                    super_node.construct_super(
                        vertical_process_strat,
                        vertical_comb_strat,
                        group_by_cols=sheet['group_by_cols'],
                        agg_col=sheet['agg_col'],
                        agg_strat=vert_sum_strat,
                        node_col_name=node_name)
                    super_node.print_df()
                    
        with open(scenario_config) as scenario:
            scenario = json.load(scenario)
            for file in scenario:
                file_path = file['file_path']
                print(file['file_name'])
                super_node = SuperNodes({'Nordics': ['GB', 'SE'], 'Europe': ['FR', 'DE']})
                super_node.load_data(file_path)
                super_node.construct_super(horizontal_process_strat, horizontal_comb_strat, rest_cols=file['rest_cols'])
                super_node.print_df(file['file_name'])
            
    construct_tab_files("agg_config.json", "scenario_config.json")

# todos
# Write test for all aggregation functions.
# TDD
