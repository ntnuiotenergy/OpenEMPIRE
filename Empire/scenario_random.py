import os
from pathlib import Path

import numpy as np
import pandas as pd


def season_month(season):
    if season=="winter":
        return [1, 2, 3]
    elif season=="spring":
        return [4, 5, 6]
    elif season=="summer":
        return [7, 8, 9]
    elif season=="fall":
        return [10, 11, 12]

def year_season_filter(data, sample_year, season):
    data = data.loc[data.year.isin([sample_year]), :]
    data = data.loc[data.month.isin(season_month(season)), :]
    return data

def remove_time_index(data):
    data = data.reset_index(drop=True)
    data = data.drop(['time', 'year', 'month', 'dayofweek', 'hour'], axis=1)
    return data

def make_datetime(data, time_format):
    data["time"] = pd.to_datetime(data["time"],
                                  format=time_format,
                                  exact=False)
    data['year'] = data['time'].dt.year
    data['month'] = data['time'].dt.month
    data['hour'] = data['time'].dt.hour
    data['dayofweek'] = data['time'].dt.dayofweek
    return data

def gather_regular_sample(data, season, seasons, regularSeasonHours,
                          sample_hour):
    data = data.reset_index(drop=True)
    sample_data = data.iloc[sample_hour:sample_hour + regularSeasonHours,:]
    
    # Sort sample_data to start on midnight monday (INACTIVE)
    # sample_data = sample_data.sort_values(by=['dayofweek','hour'])
    
    # Drop non-country columns
    sample_data = remove_time_index(sample_data)
    
    hours = list(range(1 + regularSeasonHours * seasons.index(season),
                       regularSeasonHours * (seasons.index(season) + 1) + 1))
    return [sample_data, hours]

def sample_generator(data, regularSeasonHours, scenario, season, seasons,
                     period, generator, sample_hour):
    [sample_data, hours] = gather_regular_sample(data, season, seasons,
                                                 regularSeasonHours,
                                                 sample_hour)
    generator_data = pd.DataFrame()
    if generator=='Windoffshore' or generator=='Windoffshoregrounded' or generator=='Windoffshorefloating':
        startNOnode = 2
    else:
        startNOnode = 1
    for c in sample_data.columns:
        if c == "NO":
            for i in range(startNOnode, 6):
                c_no = c + str(i)
                df = pd.DataFrame(
                    data={'Node': c_no, "IntermitentGenerators": generator,
                          "Operationalhour": hours,
                          "Scenario": "scenario" + str(scenario),
                          "Period": period,
                          "GeneratorStochasticAvailabilityRaw": 
                              sample_data[c].values})
                generator_data = pd.concat([generator_data, df], ignore_index=True)
        else:
            df = pd.DataFrame(
                data={'Node': c, "IntermitentGenerators": generator,
                      "Operationalhour": hours,
                      "Scenario": "scenario" + str(scenario),
                      "Period": period,
                      "GeneratorStochasticAvailabilityRaw": 
                          sample_data[c].values})
            generator_data = pd.concat([generator_data, df], ignore_index=True)
    return generator_data

def sample_hydro(data, regularSeasonHours, scenario, season,
                 seasons, period, sample_hour):
    [sample_data, hours] = gather_regular_sample(data, season, seasons,
                                                 regularSeasonHours,
                                                 sample_hour)
    hydro_data = pd.DataFrame()
    for c in sample_data.columns:
        if c != 'time':
            df = pd.DataFrame(
                data={'Node': c, "Period": period, "Season": season,
                      "Operationalhour": hours, 
                      "Scenario": "scenario" + str(scenario),
                      "HydroGeneratorMaxSeasonalProduction": 
                          sample_data[c].values})
            hydro_data = pd.concat([hydro_data, df], ignore_index=True)
    return hydro_data

def sample_load(data, regularSeasonHours, scenario, season, seasons,
                period, sample_hour):
    [sample_data, hours] = gather_regular_sample(data, season, seasons,
                                                 regularSeasonHours,
                                                 sample_hour)
    load = pd.DataFrame()
    for c in sample_data.columns:
        if c != 'time':
            df = pd.DataFrame(
                data={'Node': c, "Period": period, "Operationalhour": hours,
                      "Scenario": "scenario" + str(scenario),
                      "ElectricLoadRaw_in_MW": sample_data[c].values})
            load = pd.concat([load, df], ignore_index=True)
    return load

def gather_peak_sample(data, seasons, regularSeasonHours, peakSeasonHours,
                       country_sample, overall_sample):
    data = data.reset_index(drop=True)
    country_peak = data.iloc[
        int(country_sample - (peakSeasonHours/2)):int(
            country_sample + (peakSeasonHours/2)),
        :]
    overall_peak = data.iloc[
        int(overall_sample - (peakSeasonHours/2)):int(
            overall_sample + (peakSeasonHours/2)),
        :]
    
    # Sort data to start on midnight (INACTIVE)
    # country_peak = country_peak.sort_values(by=['hour'])
    # overall_peak = overall_peak.sort_values(by=['hour'])
    
    # Drop non-country columns
    country_peak = remove_time_index(country_peak)
    overall_peak = remove_time_index(overall_peak)
    
    country_hours = list(
        range(1 + regularSeasonHours * len(seasons),
              regularSeasonHours * len(seasons) + peakSeasonHours + 1)
        )
    overall_hours = list(
        range(1 + regularSeasonHours * len(seasons) + peakSeasonHours,
              regularSeasonHours * len(seasons) + 2 * peakSeasonHours + 1)
        )
    return [country_peak, overall_peak, country_hours, overall_hours]

def sample_hydro_peak(data, seasons, scenario, period, regularSeasonHours,
                      peakSeasonHours, overall_sample, country_sample):
    peak_data = pd.DataFrame()
    [country_peak, overall_peak,
     country_hours, overall_hours] = gather_peak_sample(data, seasons,
                                                        regularSeasonHours,
                                                        peakSeasonHours,
                                                        country_sample,
                                                        overall_sample)
    for c in country_peak.columns:
        df = pd.DataFrame(
            data={'Node': c, "Period": period, "Season": "peak1",
                  "Operationalhour": country_hours,
                  "Scenario": "scenario" + str(scenario),
                  "HydroGeneratorMaxSeasonalProduction": 
                      country_peak[c].values})
        peak_data = pd.concat([peak_data, df], ignore_index=True)
        df = pd.DataFrame(
            data={'Node': c, "Period": period, "Season": "peak2",
                  "Operationalhour": overall_hours,
                  "Scenario": "scenario" + str(scenario),
                  "HydroGeneratorMaxSeasonalProduction": 
                      overall_peak[c].values})
        peak_data = pd.concat([peak_data, df], ignore_index=True)
    return peak_data

def sample_load_peak(data, seasons, scenario, period, regularSeasonHours,
                     peakSeasonHours, overall_sample, country_sample):
    peak_data = pd.DataFrame()
    [country_peak, overall_peak,
     country_hours, overall_hours] = gather_peak_sample(data, seasons,
                                                        regularSeasonHours, 
                                                        peakSeasonHours, 
                                                        country_sample,
                                                        overall_sample)
    for c in country_peak.columns:
        df = pd.DataFrame(
            data={'Node': c, "Period": period, 
                  "Operationalhour": country_hours,
                  "Scenario": "scenario" + str(scenario),
                  "ElectricLoadRaw_in_MW": country_peak[c].values})
        peak_data = pd.concat([peak_data, df], ignore_index=True)
        df = pd.DataFrame(
            data={'Node': c, "Period": period, 
                  "Operationalhour": overall_hours,
                  "Scenario": "scenario" + str(scenario),
                  "ElectricLoadRaw_in_MW": overall_peak[c].values})
        peak_data = pd.concat([peak_data, df], ignore_index=True)
    return peak_data

def sample_generator_peak(data, seasons, g, scenario,
                          period, regularSeasonHours, peakSeasonHours,
                          overall_sample, country_sample):
    peak_data = pd.DataFrame()
    [country_peak, overall_peak,
     country_hours, overall_hours] = gather_peak_sample(data, seasons,
                                                        regularSeasonHours,
                                                        peakSeasonHours, 
                                                        country_sample, 
                                                        overall_sample)
    if g=='Windoffshore' or g=='Windoffshoregrounded' or g=='Windoffshorefloating':
        startNOnode = 2
    else:
        startNOnode = 1
    for c in country_peak.columns:
        if c == "NO":
            for i in range(startNOnode, 6):
                c_no = c + str(i)
                df = pd.DataFrame(
                data={'Node': c_no, "IntermitentGenerators": g,
                      "Operationalhour": country_hours,
                      "Scenario": "scenario" + str(scenario),
                      "Period": period, 
                      "GeneratorStochasticAvailabilityRaw": 
                          country_peak[c].values})
                peak_data = pd.concat([peak_data, df], ignore_index=True)
                df = pd.DataFrame(
                data={'Node': c_no, "IntermitentGenerators": g, 
                      "Operationalhour": overall_hours, 
                      "Scenario": "scenario" + str(scenario),
                      "Period": period, 
                      "GeneratorStochasticAvailabilityRaw": 
                          overall_peak[c].values})
                peak_data = pd.concat([peak_data, df], ignore_index=True)
        else:
            df = pd.DataFrame(
            data={'Node': c, "IntermitentGenerators": g, 
                  "Operationalhour": country_hours, 
                  "Scenario": "scenario" + str(scenario),
                  "Period": period,
                  "GeneratorStochasticAvailabilityRaw": 
                      country_peak[c].values})
            peak_data = pd.concat([peak_data, df], ignore_index=True)
            df = pd.DataFrame(
            data={'Node': c, "IntermitentGenerators": g, 
                  "Operationalhour": overall_hours,
                  "Scenario": "scenario" + str(scenario),
                  "Period": period,
                 "GeneratorStochasticAvailabilityRaw": 
                     overall_peak[c].values})
            peak_data = pd.concat([peak_data, df], ignore_index=True)
    return peak_data

def generate_random_scenario(file_path: Path, tab_file_path: Path, scenarios, seasons,
                             Periods, regularSeasonHours, peakSeasonHours, 
                             dict_countries, time_format, fix_sample,
                             north_sea):
    
    if fix_sample:
        print("Generating scenarios according to key...")
    else:
        print("Generating random scenarios...")

    # Generate dataframes to print as stochastic-files
    genAvail = pd.DataFrame()
    elecLoad = pd.DataFrame()
    hydroSeasonal = pd.DataFrame()
    
    # Load all the raw scenario data
    solar_data = pd.read_csv(file_path / "solar.csv")
    windonshore_data = pd.read_csv(file_path / "windonshore.csv")
    windoffshore_data = pd.read_csv(file_path / "windoffshore.csv")
    hydroror_data = pd.read_csv(file_path / "hydroror.csv")
    hydroseasonal_data = pd.read_csv(file_path / "hydroseasonal.csv")
    electricload_data = pd.read_csv(file_path / "electricload.csv")

    # Make datetime columns
    solar_data = make_datetime(solar_data, time_format)
    windonshore_data = make_datetime(windonshore_data, time_format)
    windoffshore_data = make_datetime(windoffshore_data, time_format)
    hydroror_data = make_datetime(hydroror_data, time_format)
    hydroseasonal_data = make_datetime(hydroseasonal_data, time_format)
    electricload_data = make_datetime(electricload_data, time_format)


    if fix_sample:
        sampling_key = pd.read_csv(file_path / "sampling_key.csv")
        sampling_key = sampling_key.set_index(['Period','Scenario','Season'])
    else:
        sampling_key = pd.DataFrame(columns=['Period','Scenario','Season','Year','Hour'])

    for i in range(1,Periods+1):
        for scenario in range(1,scenarios+1):
            for s in seasons:
                ###################
                ##REGULAR SEASONS##
                ###################

        		# Get sample year (2015-2019) for each season/scenario 
                        
                sample_year = np.random.choice(list(range(2015,2020)))
        
        		# Set sample year according to key
                    
                if fix_sample:
                    sample_year = sampling_key.loc[(i,scenario,s),'Year']

        		# Filter out the hours within the sample year
                    
                solar_season = year_season_filter(solar_data,
                                                sample_year,
                                                s)
                windonshore_season = year_season_filter(windonshore_data,
                                                      sample_year,
                                                      s)
                windoffshore_season = year_season_filter(windoffshore_data,
                                                       sample_year,
                                                       s)
                hydroror_season = year_season_filter(hydroror_data,
                                                   sample_year,
                                                   s)
                hydroseasonal_season = year_season_filter(hydroseasonal_data,
                                                        sample_year,
                                                        s)
                electricload_season = year_season_filter(electricload_data,
                                                       sample_year,
                                                       s)
                
                sample_hour = np.random.randint(
                    0, solar_season.shape[0] - regularSeasonHours - 1)
                

                # Choose sample_hour from key or save sampling key

                if fix_sample:
                    sample_hour = sampling_key.loc[(i,scenario,s),'Hour']
                else:
                    df = pd.DataFrame(data={'Period': i,
                                            'Scenario': scenario,
                                            'Season': s,
                                            'Year': sample_year,
                                            'Hour': sample_hour}, index=[0])
                    sampling_key = pd.concat([sampling_key, df], ignore_index=True)

                # Sample generator availability for regular seasons
                genAvail = pd.concat([genAvail,
                                      sample_generator(data=solar_season,
                                                       regularSeasonHours=regularSeasonHours,
                                                       scenario=scenario, season=s,
                                                       seasons=seasons, period=i,
                                                       generator="Solar",
                                                       sample_hour=sample_hour)],
                                     ignore_index=True)
                genAvail = pd.concat([genAvail,
                                      sample_generator(data=windonshore_season,
                                                       regularSeasonHours=regularSeasonHours,
                                                       scenario=scenario, season=s,
                                                       seasons=seasons, period=i,
                                                       generator="Windonshore",
                                                       sample_hour=sample_hour)],
                                     ignore_index=True)
                if north_sea:
                    genAvail = pd.concat([genAvail,
                                          sample_generator(data=windoffshore_season,
                                                           regularSeasonHours=regularSeasonHours,
                                                           scenario=scenario, season=s,
                                                           seasons=seasons, period=i,
                                                           generator="Windoffshoregrounded",
                                                           sample_hour=sample_hour)],
                                         ignore_index=True)
                    genAvail = pd.concat([genAvail,
                                          sample_generator(data=windoffshore_season,
                                                           regularSeasonHours=regularSeasonHours,
                                                           scenario=scenario, season=s,
                                                           seasons=seasons, period=i,
                                                           generator="Windoffshorefloating",
                                                           sample_hour=sample_hour)],
                                         ignore_index=True)
                else:
                    genAvail = pd.concat([genAvail,
                                          sample_generator(data=windoffshore_season,
                                                           regularSeasonHours=regularSeasonHours,
                                                           scenario=scenario, season=s,
                                                           seasons=seasons, period=i,
                                                           generator="Windoffshore",
                                                           sample_hour=sample_hour)],
                                         ignore_index=True)
                genAvail = pd.concat([genAvail,
                                      sample_generator(data=hydroror_season,
                                                       regularSeasonHours=regularSeasonHours,
                                                       scenario=scenario, season=s,
                                                       seasons=seasons, period=i,
                                                       generator="Hydrorun-of-the-river",
                                                       sample_hour=sample_hour)],
                                     ignore_index=True)

                # Sample electric load for regular seasons
                elecLoad = pd.concat([elecLoad,
                                      sample_load(data=electricload_season,
                                                  regularSeasonHours=regularSeasonHours,
                                                  scenario=scenario, season=s,
                                                  seasons=seasons, period=i, 
                                                  sample_hour=sample_hour)],
                                     ignore_index=True)
                
                # Sample seasonal hydro limit for regular seasons
                hydroSeasonal = pd.concat([hydroSeasonal,
                                           sample_hydro(data=hydroseasonal_season,
                                                        regularSeasonHours=regularSeasonHours,
                                                        scenario=scenario, season=s, 
                                                        seasons=seasons, period=i,
                                                        sample_hour=sample_hour)],
                                          ignore_index=True)
            
            ################
            ##PEAK SEASONS##
            ################
            
            # Get peak sample year (2015-2019)
                    
            sample_year = np.random.choice(list(range(2015,2020)))
                
            if fix_sample:
                sample_year = sampling_key.loc[(i,scenario,'peak'),'Year']
            else:
                df = pd.DataFrame(data={'Period': i,
                                        'Scenario': scenario,
                                        'Season': 'peak',
                                        'Year': sample_year,
                                        'Hour': 0}, index=[0])
                sampling_key = pd.concat([sampling_key, df], ignore_index=True)
        
            # Filter out the hours within the sample year
                
            solar_data_year = solar_data.loc[solar_data.year.isin([sample_year]), :]
            windonshore_data_year = windonshore_data.loc[windonshore_data.year.isin([sample_year]), :]
            windoffshore_data_year = windoffshore_data.loc[windoffshore_data.year.isin([sample_year]), :]
            hydroror_data_year = hydroror_data.loc[hydroror_data.year.isin([sample_year]), :]
            hydroseasonal_data_year = hydroseasonal_data.loc[hydroseasonal_data.year.isin([sample_year]), :]
            electricload_data_year = electricload_data.loc[electricload_data.year.isin([sample_year]), :]

            #Peak1: The highest load when all loads are summed together
            electricload_data_year_notime = remove_time_index(electricload_data_year)
            overall_sample = electricload_data_year_notime.sum(axis=1).idxmax()
            #Peak2: The highest load of a single country
            max_load_country = electricload_data_year_notime.max().idxmax()
            country_sample = electricload_data_year_notime[max_load_country].idxmax()

            #Sample generator availability for peak seasons
            genAvail = pd.concat([genAvail,
                                  sample_generator_peak(data=solar_data_year,
                                                        seasons=seasons,
                                                        g="Solar", scenario=scenario, period=i,
                                                        regularSeasonHours=regularSeasonHours,
                                                        peakSeasonHours=peakSeasonHours,
                                                        overall_sample=overall_sample,
                                                        country_sample=country_sample)],
                                 ignore_index=True)
            genAvail = pd.concat([genAvail,
                                  sample_generator_peak(data=windonshore_data_year,
                                                        seasons=seasons, 
                                                        g="Windonshore", scenario=scenario, 
                                                        period=i, 
                                                        regularSeasonHours=regularSeasonHours,
                                                        peakSeasonHours=peakSeasonHours,
                                                        overall_sample=overall_sample, 
                                                        country_sample=country_sample)],
                                 ignore_index=True)
            if north_sea:
                genAvail = pd.concat([genAvail,
                      sample_generator_peak(data=windoffshore_data_year,
                                            seasons=seasons, 
                                            g="Windoffshoregrounded", scenario=scenario,
                                            period=i, 
                                            regularSeasonHours=regularSeasonHours, 
                                            peakSeasonHours=peakSeasonHours, 
                                            overall_sample=overall_sample, 
                                            country_sample=country_sample)],
                     ignore_index=True)
                genAvail = pd.concat([genAvail,
                      sample_generator_peak(data=windoffshore_data_year,
                                            seasons=seasons, 
                                            g="Windoffshorefloating", scenario=scenario,
                                            period=i, 
                                            regularSeasonHours=regularSeasonHours, 
                                            peakSeasonHours=peakSeasonHours, 
                                            overall_sample=overall_sample, 
                                            country_sample=country_sample)],
                     ignore_index=True)
            else:
                genAvail = pd.concat([genAvail,
                                      sample_generator_peak(data=windoffshore_data_year,
                                                            seasons=seasons, 
                                                            g="Windoffshore", scenario=scenario,
                                                            period=i, 
                                                            regularSeasonHours=regularSeasonHours, 
                                                            peakSeasonHours=peakSeasonHours, 
                                                            overall_sample=overall_sample, 
                                                            country_sample=country_sample)],
                                     ignore_index=True)
            genAvail = pd.concat([genAvail,
                                  sample_generator_peak(data=hydroror_data_year,
                                                        seasons=seasons, 
                                                        g="Hydrorun-of-the-river",
                                                        scenario=scenario, period=i, 
                                                        regularSeasonHours=regularSeasonHours,
                                                        peakSeasonHours=peakSeasonHours,
                                                        overall_sample=overall_sample, 
                                                        country_sample=country_sample)],
                                 ignore_index=True)
            
            #Sample electric load for peak seasons
            elecLoad = pd.concat([elecLoad,
                                  sample_load_peak(data=electricload_data_year,
                                                   seasons=seasons,
                                                   scenario=scenario, period=i, 
                                                   regularSeasonHours=regularSeasonHours, 
                                                   peakSeasonHours=peakSeasonHours,
                                                   overall_sample=overall_sample, 
                                                   country_sample=country_sample)],
                                 ignore_index=True)
            
            #Sample seasonal hydro limit for peak seasons
            hydroSeasonal = pd.concat([hydroSeasonal,
                                       sample_hydro_peak(data=hydroseasonal_data_year,
                                                         seasons=seasons,
                                                         scenario=scenario, period=i, 
                                                         regularSeasonHours=regularSeasonHours, 
                                                         peakSeasonHours=peakSeasonHours,
                                                         overall_sample=overall_sample, 
                                                         country_sample=country_sample)],
                                      ignore_index=True)

    #Replace country codes with country names
    genAvail = genAvail.replace({"Node": dict_countries})
    elecLoad = elecLoad.replace({"Node": dict_countries})
    hydroSeasonal = hydroSeasonal.replace({"Node": dict_countries})

    #Make header for .tab-file
    genAvail = genAvail[["Node", "IntermitentGenerators", "Operationalhour",
                         "Scenario", "Period",
                         "GeneratorStochasticAvailabilityRaw"]]
    elecLoad = elecLoad[["Node", "Operationalhour", "Scenario","Period", 
                         'ElectricLoadRaw_in_MW']]
    hydroSeasonal = hydroSeasonal[["Node", "Period", "Season", 
                                   "Operationalhour", "Scenario",
                                   "HydroGeneratorMaxSeasonalProduction"]]
    
    genAvail.loc[genAvail["GeneratorStochasticAvailabilityRaw"] <= 0.001,"GeneratorStochasticAvailabilityRaw"] = 0
    elecLoad.loc[elecLoad['ElectricLoadRaw_in_MW'] <= 0.001,'ElectricLoadRaw_in_MW'] = 0
    hydroSeasonal.loc[hydroSeasonal["HydroGeneratorMaxSeasonalProduction"] <= 0.001,"HydroGeneratorMaxSeasonalProduction"] = 0
    

    #Make file_path (if it does not exist) and print .tab-files
    if not os.path.exists(tab_file_path):
        os.makedirs(tab_file_path)
        
    # Save sampling key
    if fix_sample:
        sampling_key = sampling_key.reset_index(level=['Period','Scenario','Season'])
        
    sampling_key.to_csv(
        tab_file_path / "sampling_key.csv",
        header=True, index=None, mode='w')        

    genAvail.to_csv(
        tab_file_path / "Stochastic_StochasticAvailability.tab",
        header=True, index=None, sep='\t', mode='w')
    elecLoad.to_csv(
        tab_file_path / "Stochastic_ElectricLoadRaw.tab",
        header=True, index=None, sep='\t', mode='w')
    hydroSeasonal.to_csv(
        tab_file_path / "Stochastic_HydroGenMaxSeasonalProduction.tab",
        header=True, index=None, sep='\t', mode='w')
