import pandas as pd
import numpy as np
import os

def gather_season(data, season):
    if season=="winter":
        return data.loc[data.month.isin([12, 1, 2]), :]
    elif season=="spring":
        return data.loc[data.month.isin([3, 4, 5]), :]
    elif season=="summer":
        return data.loc[data.month.isin([6, 7, 8]), :]
    elif season=="fall":
        return data.loc[data.month.isin([9, 10, 11]), :]

def remove_time_index(data):
    data = data.reset_index(drop=True)
    data = data.drop(['time', 'year', 'month', 'dayofweek', 'hour'], axis=1)
    return data


def filter_sample_year(data, sample_year):
    data["time"] = pd.to_datetime(data["time"])
    data['year'] = data['time'].dt.year
    data['month'] = data['time'].dt.month
    data['hour'] = data['time'].dt.hour
    data['dayofweek'] = data['time'].dt.dayofweek
    if sample_year != None:
        data = data.loc[data.year.isin(sample_year), :]
    return data

def gather_regular_sample(data, season, seasons, regularSeasonHours,
                          sample_hour):
    data = gather_season(data=data, season=season)
    data = data.reset_index(drop=True)
    sample_data = data.iloc[sample_hour:sample_hour + regularSeasonHours,:]
    
    # Sort sample_data to start on midnight monday
    sample_data = sample_data.sort_values(by=['dayofweek','hour'])
    
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
    if generator=='Windoffshore':
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
                generator_data = generator_data.append(df, ignore_index=True)
        else:
            df = pd.DataFrame(
                data={'Node': c, "IntermitentGenerators": generator,
                      "Operationalhour": hours,
                      "Scenario": "scenario" + str(scenario),
                      "Period": period,
                      "GeneratorStochasticAvailabilityRaw": 
                          sample_data[c].values})
            generator_data = generator_data.append(df, ignore_index=True)
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
            hydro_data = hydro_data.append(df, ignore_index=True)
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
            load = load.append(df, ignore_index=True)
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
    
    # Sort data to start on midnight 
    country_peak = country_peak.sort_values(by=['hour'])
    overall_peak = overall_peak.sort_values(by=['hour'])
    
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
        peak_data = peak_data.append(df, ignore_index=True)
        df = pd.DataFrame(
            data={'Node': c, "Period": period, "Season": "peak2",
                  "Operationalhour": overall_hours,
                  "Scenario": "scenario" + str(scenario),
                  "HydroGeneratorMaxSeasonalProduction": 
                      overall_peak[c].values})
        peak_data = peak_data.append(df, ignore_index=True)
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
        peak_data = peak_data.append(df, ignore_index=True)
        df = pd.DataFrame(
            data={'Node': c, "Period": period, 
                  "Operationalhour": overall_hours,
                  "Scenario": "scenario" + str(scenario),
                  "ElectricLoadRaw_in_MW": overall_peak[c].values})
        peak_data = peak_data.append(df, ignore_index=True)
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
    if g=='Windoffshore':
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
                peak_data = peak_data.append(df, ignore_index=True)
                df = pd.DataFrame(
                data={'Node': c_no, "IntermitentGenerators": g, 
                      "Operationalhour": overall_hours, 
                      "Scenario": "scenario" + str(scenario),
                      "Period": period, 
                      "GeneratorStochasticAvailabilityRaw": 
                          overall_peak[c].values})
                peak_data = peak_data.append(df, ignore_index=True)
        else:
            df = pd.DataFrame(
            data={'Node': c, "IntermitentGenerators": g, 
                  "Operationalhour": country_hours, 
                  "Scenario": "scenario" + str(scenario),
                  "Period": period,
                  "GeneratorStochasticAvailabilityRaw": 
                      country_peak[c].values})
            peak_data = peak_data.append(df, ignore_index=True)
            df = pd.DataFrame(
            data={'Node': c, "IntermitentGenerators": g, 
                  "Operationalhour": overall_hours,
                  "Scenario": "scenario" + str(scenario),
                  "Period": period,
                 "GeneratorStochasticAvailabilityRaw": 
                     overall_peak[c].values})
            peak_data = peak_data.append(df, ignore_index=True)
    return peak_data

def generate_random_scenario(filepath, tab_file_path, scenarios, seasons,
                             Periods, regularSeasonHours, peakSeasonHours, 
                             dict_countries):
    
    print("Generating random scenarios...")

    # Generate dataframes to print as stochastic-files
    genAvail = pd.DataFrame()
    elecLoad = pd.DataFrame()
    hydroSeasonal = pd.DataFrame()
    
    # Load all the raw scenario data
    solar_data = pd.read_csv(filepath + "/solar.csv")
    windonshore_data = pd.read_csv(filepath + "/windonshore.csv")
    windoffshore_data = pd.read_csv(filepath + "/windoffshore.csv")
    hydrorunoftheriver_data = pd.read_csv(filepath + "/hydroror.csv")
    hydroseasonal_data = pd.read_csv(filepath + "/hydroseasonal.csv")
    electricload_data = pd.read_csv(filepath + "/electricload.csv")

    for i in range(1,Periods+1):
        years = []
        for scenario in range(1,scenarios+1):
            
            # Get sample years for each scenario (solar/wind, hydro, load)
            
            sample_year = list(np.random.randint(1985, 2017, 1))
            sample_year_load = list(np.random.randint(2015, 2019, 1))
            sample_year_hydro = list(np.random.randint(2015, 2020, 1))
            
            # Filter out the hours within the sample year
            
            solar_data_year = filter_sample_year(
                data=solar_data, sample_year=sample_year)
            windonshore_data_year = filter_sample_year(
                data=windonshore_data, sample_year=sample_year)
            windoffshore_data_year = filter_sample_year(
                data=windoffshore_data, sample_year=sample_year)
            hydrorunoftheriver_data_year = filter_sample_year(
                data=hydrorunoftheriver_data, sample_year=sample_year_hydro)
            hydroseasonal_data = filter_sample_year(
                data=hydroseasonal_data, sample_year=None)
            electricload_data_year = filter_sample_year(
                data=electricload_data, sample_year=sample_year_load)

            # Ensure the same climatic year is not chosen twice for wind/solar
            
            while sample_year in years:
                sample_year = list(np.random.randint(1985, 2016, 1))
            years.append(sample_year[0])

            ###################
            ##REGULAR SEASONS##
            ###################

            for s in seasons:
                
                # Get the sample range for regular season s. 
                # 'max_sample' is the max "last hour" for season s
                
                max_sample = min(
                    gather_season(data=hydrorunoftheriver_data_year,
                                  season=s).shape[0],
                    gather_season(data=electricload_data_year,
                                  season=s).shape[0], 
                    gather_season(data=windoffshore_data_year,
                                  season=s).shape[0])
                sample_hour = np.random.randint(
                    0, max_sample - regularSeasonHours - 1)
                
                # Sample generator availability for regular seasons
                genAvail = genAvail.append(
                    sample_generator(data=solar_data_year,
                                     regularSeasonHours=regularSeasonHours,
                                     scenario=scenario, season=s,
                                     seasons=seasons, period=i,
                                     generator="Solar",
                                     sample_hour=sample_hour))
                genAvail = genAvail.append(
                    sample_generator(data=windonshore_data_year,
                                     regularSeasonHours=regularSeasonHours,
                                     scenario=scenario, season=s,
                                     seasons=seasons, period=i,
                                     generator="Windonshore",
                                     sample_hour=sample_hour))
                genAvail = genAvail.append(
                    sample_generator(data=windoffshore_data_year,
                                     regularSeasonHours=regularSeasonHours, 
                                     scenario=scenario, season=s,
                                     seasons=seasons, period=i,
                                     generator="Windoffshore", 
                                     sample_hour=sample_hour))
                genAvail = genAvail.append(
                    sample_generator(data=hydrorunoftheriver_data_year,
                                     regularSeasonHours=regularSeasonHours, 
                                     scenario=scenario, season=s, 
                                     seasons=seasons, period=i, 
                                     generator="Hydrorun-of-the-river", 
                                     sample_hour=sample_hour))

                # Sample electric load for regular seasons
                elecLoad = elecLoad.append(
                    sample_load(data=electricload_data_year,
                                regularSeasonHours=regularSeasonHours,
                                scenario=scenario, season=s,
                                seasons=seasons, period=i, 
                                sample_hour=sample_hour))
                
                # Sample seasonal hydro limit for regular seasons
                hydroSeasonal = hydroSeasonal.append(
                    sample_hydro(data=hydroseasonal_data,
                                 regularSeasonHours=regularSeasonHours,
                                 scenario=scenario, season=s, 
                                 seasons=seasons, period=i,
                                 sample_hour=sample_hour))
            
            ################
            ##PEAK SEASONS##
            ################
            
            #Peak1: The highest load when all loads are summed together
            electricload_data_year_notime = remove_time_index(electricload_data_year)
            overall_sample = electricload_data_year_notime.sum(axis=1).idxmax()
            #Peak2: The highest load of a single country
            max_load_country = electricload_data_year_notime.max().idxmax()
            country_sample = electricload_data_year_notime[max_load_country].idxmax()

            #Sample generator availability for peak seasons
            genAvail = genAvail.append(
                sample_generator_peak(data=solar_data_year,
                                      seasons=seasons,
                                      g="Solar", scenario=scenario, period=i,
                                      regularSeasonHours=regularSeasonHours,
                                      peakSeasonHours=peakSeasonHours,
                                      overall_sample=overall_sample,
                                      country_sample=country_sample))
            genAvail = genAvail.append(
                sample_generator_peak(data=windonshore_data_year,
                                      seasons=seasons, 
                                      g="Windonshore", scenario=scenario, 
                                      period=i, 
                                      regularSeasonHours=regularSeasonHours,
                                      peakSeasonHours=peakSeasonHours,
                                      overall_sample=overall_sample, 
                                      country_sample=country_sample))
            genAvail = genAvail.append(
                sample_generator_peak(data=windoffshore_data_year,
                                      seasons=seasons, 
                                      g="Windoffshore", scenario=scenario,
                                      period=i, 
                                      regularSeasonHours=regularSeasonHours, 
                                      peakSeasonHours=peakSeasonHours, 
                                      overall_sample=overall_sample, 
                                      country_sample=country_sample))
            genAvail = genAvail.append(
                sample_generator_peak(data=hydrorunoftheriver_data_year,
                                      seasons=seasons, 
                                      g="Hydrorun-of-the-river",
                                      scenario=scenario, period=i, 
                                      regularSeasonHours=regularSeasonHours,
                                      peakSeasonHours=peakSeasonHours,
                                      overall_sample=overall_sample, 
                                      country_sample=country_sample))
            
            #Sample electric load for peak seasons
            elecLoad = elecLoad.append(
                sample_load_peak(data=electricload_data_year,
                                 seasons=seasons,
                                 scenario=scenario, period=i, 
                                 regularSeasonHours=regularSeasonHours, 
                                 peakSeasonHours=peakSeasonHours,
                                 overall_sample=overall_sample, 
                                 country_sample=country_sample))
            
            #Sample seasonal hydro limit for peak seasons
            hydroSeasonal = hydroSeasonal.append(
                sample_hydro_peak(data=hydroseasonal_data,
                                  seasons=seasons,
                                  scenario=scenario, period=i, 
                                  regularSeasonHours=regularSeasonHours, 
                                  peakSeasonHours=peakSeasonHours,
                                  overall_sample=overall_sample, 
                                  country_sample=country_sample))

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

    #Make filepath (if it does not exist) and print .tab-files
    if not os.path.exists(tab_file_path):
        os.makedirs(tab_file_path)
    genAvail.to_csv(
        tab_file_path + "/Stochastic_StochasticAvailability" + '.tab',
        header=True, index=None, sep='\t', mode='w')
    elecLoad.to_csv(
        tab_file_path + "/Stochastic_ElectricLoadRaw" + '.tab',
        header=True, index=None, sep='\t', mode='w')
    hydroSeasonal.to_csv(
        tab_file_path + "/Stochastic_HydroGenMaxSeasonalProduction" + '.tab',
        header=True, index=None, sep='\t', mode='w')