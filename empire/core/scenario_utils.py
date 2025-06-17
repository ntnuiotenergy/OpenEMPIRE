import pandas as pd

def make_datetime(data, time_format):
    data["time"] = pd.to_datetime(data["time"], format=time_format, exact=False)
    data["year"] = data["time"].dt.year
    data["month"] = data["time"].dt.month
    data["hour"] = data["time"].dt.hour
    data["dayofweek"] = data["time"].dt.dayofweek
    return data

def year_season_filter(data, sample_year, season):
    data = data.loc[data.year.isin([sample_year]), :]
    data = data.loc[data.month.isin(season_month(season)), :]
    return data

def remove_time_index(data):
    data = data.reset_index(drop=True)
    data = data.drop(["time", "year", "month", "dayofweek", "hour"], axis=1)
    return data

def season_month(season: str):
    if season == "winter":
        return [1, 2, 3]
    if season == "spring":
        return [4, 5, 6]
    if season == "summer":
        return [7, 8, 9]
    if season == "fall":
        return [10, 11, 12]

    raise ValueError(f"{season} is not a valid season.") 