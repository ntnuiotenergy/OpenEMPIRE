from reader import read_file
import pandas as pd
from typing import List, Callable
import numpy as np
import json
import itertools

# def construct_super(data: pd.DataFrame,
#                     s_name: str, 
#                     child_nodes: List[str], 
#                     group_by_cols: List[str], 
#                     agg_col: str, 
#                     agg_strat: Callable):
    
#     f_data = data[data.Nodes.isin(child_nodes)]
#     agg_data = agg_strat(f_data, group_by_cols, agg_col)
#     agg_data['Nodes'] = s_name
#     return agg_data

# def combine_nodes(data: pd.DataFrame, 
#                   s_nodes: dict, 
#                   group_by_cols: List[str], 
#                   agg_col:str, 
#                   agg_strat: Callable):
#     dfs = [construct_super(data=data, 
#                            s_name=s_node, 
#                            child_nodes=child_nodes, 
#                            group_by_cols=group_by_cols,
#                            agg_col=agg_col, 
#                            agg_strat=agg_strat) for s_node, child_nodes in s_nodes.items()]
#     return pd.concat(dfs)

# def construct_tab_files(config_path: str):
#     with open(config_path) as json_file:
#         config = json.load(json_file)
#         for file in config:
#             file_path = pd.ExcelFile(file['file_path'])
#             for sheet in file['agg_sheets']:
#                 sheet_df = pd.read_excel(file_path, sheet['sheet_name'], skiprows=sheet['skiprows'], usecols=sheet['usecols'])
#                 df = combine_nodes(data=sheet_df, 
#                               s_nodes={'Nordics': ['Norway', 'Sweden', 'Denmark'], 'Europe': ['France', 'Germany']},
#                               group_by_cols=sheet['group_by_cols'],
#                               agg_col=sheet['agg_col'],
#                               agg_strat=sum_strat)
#                 df.to_csv("nic_test/" + file['file_name'] + "_" + sheet['sheet_name'] + '.tab', sep='\t')

# def sum_countries(filtered_data: pd.DataFrame, group_by_cols: List[str]):
#     return filtered_data[group_by_cols].sum(axis=1)


def vert_sum_strat(filtered_data: pd.DataFrame, group_by_cols: List[str], agg_col: str):
    return filtered_data.groupby(group_by_cols).sum(agg_col)

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
    
    def print_df(self):
        print(self.processed_data)
    
    def processed_nodes(self):
        nodes = [value for value in self.s_nodes.values()]
        return list(itertools.chain.from_iterable(nodes))

if __name__ == '__main__':
    # def construct_tab_files(config_path: str):
    #     with open(config_path) as json_file:
    #         config = json.load(json_file)
    #         for file in config:
    #             file_path = pd.ExcelFile(file['file_path'])
    #             for sheet in file['agg_sheets']:
    #                 sheet_df = pd.read_excel(file_path, sheet['sheet_name'], skiprows=sheet['skiprows'], usecols=sheet['usecols'])
    #                 df = combine_nodes(data=sheet_df, 
    #                             s_nodes={'Nordics': ['Norway', 'Sweden', 'Denmark'], 'Europe': ['France', 'Germany']},
    #                             group_by_cols=sheet['group_by_cols'],
    #                             agg_col=sheet['agg_col'],
    #                             agg_strat=sum_strat)
    #                 df.to_csv("nic_test/" + file['file_name'] + "_" + sheet['sheet_name'] + '.tab', sep='\t')
                
    file_path = pd.ExcelFile('/Users/nwong/Workspace/School/OpenEMPIRE/Data handler/europe_v50/Generator.xlsx')
    generators = SuperNodes({'Nordics': ['NO1', 'Sweden', 'Denmark'], 'Europe': ['France', 'Germany']}, 'MaxInstalledCapacity', 2, 'A:C')
    generators.load_data(file_path)
    generators.construct_super(vertical_process_strat, 
                               vertical_comb_strat, 
                               group_by_cols=['GeneratorTechnology'], 
                               agg_col='generatorMaxInstallCapacity  in MW', 
                               agg_strat=vert_sum_strat,
                               node_col_name='Node')
    generators.print_df()
    
    # electric load
    file_path2 = '/Users/nwong/Workspace/School/OpenEMPIRE/Data handler/europe_v50/ScenarioData/electricload.csv'
    load = SuperNodes({'Nordics': ['NO1', 'SE', 'DK'], 'Europe': ['FR', 'DE']})
    load.load_data(file_path2)
    load.construct_super(horizontal_process_strat, horizontal_comb_strat, rest_cols=['time'])
    load.print_df()