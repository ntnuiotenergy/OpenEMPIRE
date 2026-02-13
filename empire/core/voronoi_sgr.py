# File: empire/core/voronoi_sgr.py

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial import Voronoi
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Add 3D plotting capability
import time  # Add time module for sleep function

from empire.core.scenario_utils import make_datetime, year_season_filter, remove_time_index, season_month

def compute_voronoi_clusters(candidates: np.ndarray,
                             n_cluster: int = 10,
                             output_dir: Path | None = None,
                             mu_percentile: int = 80) -> pd.DataFrame:
    """Compute Voronoi clusters from candidate windows.

    Args:
        candidates: Structured array of candidate windows with Year, Season, and Feature columns
        mu: Optional regularization parameter
        n_cluster: Number of clusters to create
        output_dir: Optional directory to save plots. If None, uses current working directory.
        mu_percentile: Percentile used for automatic mu calculation (default: 80)

    Returns:
        DataFrame containing cluster assignments
    """
    if output_dir is None:
        output_dir = Path.cwd() / "VoronoiClusters"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Computing Voronoi clusters with candidates shape={candidates.shape}")
    print(f"Using mu_percentile={mu_percentile}")
    
    # Extract numeric features for PCA
    feature_columns = [col for col in candidates.dtype.names if col.startswith('Feature')]
    features = np.column_stack([candidates[col] for col in feature_columns])
    
    # Reduce dimensionality to 4D using PCA
    print("Reducing dimensionality with PCA...")
    pca = PCA(n_components=4)
    candidates_4d = pca.fit_transform(features)
    print(f"Reduced candidates shape: {candidates_4d.shape}")    
    total_explained_variance = np.sum(pca.explained_variance_ratio_)
    print(f"Total explained variance by first 4 components: {total_explained_variance:.2%}")
    
    # Create and save 3D scatter plot of the first three components
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(candidates_4d[:, 0], candidates_4d[:, 1], candidates_4d[:, 2], alpha=0.5)
    ax.set_xlabel("First Principal Component")
    ax.set_ylabel("Second Principal Component")
    ax.set_zlabel("Third Principal Component")
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    
    # Save the plot
    plt.savefig(output_dir / "voronoi_scatter_pca_3d.png")
    plt.close()
    
    # Compute the Voronoi diagram on the reduced data
    vor = Voronoi(candidates_4d)
    
    # Compute the "radius" for each Voronoi vertex
    vertex_radii = []
    for vertex in vor.vertices:
        r = np.min(np.linalg.norm(candidates_4d - vertex, axis=1))
        vertex_radii.append(r)
    vertex_radii = np.array(vertex_radii)
    
    # Calculate mu using the specified percentile
    sorted_radii = np.sort(vertex_radii)
    mu = np.percentile(sorted_radii, mu_percentile)
    print(f"Calculated mu using {mu_percentile}th percentile: {mu:.4f}")
    print(f"Vertex radii range: min={sorted_radii[0]:.4f}, max={sorted_radii[-1]:.4f}")
    
    # Sort vertex indices by ascending radius and take first n_cluster as prototypes
    proto_ids = np.argsort(vertex_radii)[:n_cluster]
    label_lookup = {idx: k for k, idx in enumerate(proto_ids)}
    
    def nearest_proto(pt):
        dists = np.linalg.norm(vor.vertices[proto_ids] - pt, axis=1)
        k = np.argmin(dists)
        min_dist = dists[k]
        is_singleton = min_dist > mu
        if is_singleton:
            print(f"Found singleton with distance {min_dist:.4f} > mu={mu:.4f}")
        return k if not is_singleton else -1  # -1 for singletons
    
    # Assign each point to its nearest prototype
    cluster_assignments = np.array([nearest_proto(pt) for pt in candidates_4d])
    
    # Print cluster statistics
    n_singletons = np.sum(cluster_assignments == -1)
    print(f"Cluster assignments: {n_singletons} singletons out of {len(cluster_assignments)} total points")
    for k in range(n_cluster):
        n_in_cluster = np.sum(cluster_assignments == k)
        print(f"Cluster {k}: {n_in_cluster} points")
    
    # Save cluster statistics to file
    stats_file = output_dir / "cluster_statistics.txt"
    with open(stats_file, "w") as f:
        f.write(f"Voronoi Clustering Statistics\n")
        f.write(f"===========================\n\n")
        f.write(f"Using mu_percentile: {mu_percentile}\n")
        f.write(f"Calculated mu value: {mu:.4f}\n")
        f.write(f"Vertex radii range: min={sorted_radii[0]:.4f}, max={sorted_radii[-1]:.4f}\n\n")
        f.write(f"Cluster Assignments:\n")
        f.write(f"-------------------\n")
        f.write(f"Total points: {len(cluster_assignments)}\n")
        f.write(f"Singletons: {n_singletons} ({n_singletons/len(cluster_assignments)*100:.1f}%)\n")
        for k in range(n_cluster):
            n_in_cluster = np.sum(cluster_assignments == k)
            f.write(f"Cluster {k}: {n_in_cluster} points ({n_in_cluster/len(cluster_assignments)*100:.1f}%)\n")
    
    # Create output DataFrame
    out = pd.DataFrame({
        "Year": candidates['Year'],
        "Season": candidates['Season'],
        "SampleIndex": np.arange(len(candidates)),
        "ClusterGroup": cluster_assignments
    })
    
    # Save scatter plot with cluster assignments
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    colors = plt.cm.rainbow(np.linspace(0, 1, n_cluster))
    for k in range(n_cluster):
        mask = cluster_assignments == k
        ax.scatter(candidates_4d[mask, 0], candidates_4d[mask, 1], candidates_4d[mask, 2], 
                  c=[colors[k]], alpha=0.5)
    # Plot singletons in gray
    mask = cluster_assignments == -1
    if np.any(mask):
        ax.scatter(candidates_4d[mask, 0], candidates_4d[mask, 1], candidates_4d[mask, 2], 
                  c='gray', alpha=0.5)
    ax.set_xlabel("First Principal Component")
    ax.set_ylabel("Second Principal Component")
    ax.set_zlabel("Third Principal Component")
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    plt.tight_layout()
    plt.savefig(output_dir / "voronoi_scatter_clusters.png")
    plt.close()
    
    return out


def extract_candidate_windows(scenario_data_path: Path, season: str, regularSeasonHours: int, time_format: str):
    """
    Extract candidate windows from the electric load CSV file for a given season across all years.

    Parameters:
      scenario_data_path: Path to the folder containing scenario data files.
      season: Season (e.g., "winter", "spring", etc.) to filter the data.
      regularSeasonHours: Number of consecutive hours that form one candidate window.
      time_format: Datetime format used in the CSV file.
      
    Returns:
      A tuple (candidates, sample_hours) where:
         - candidates: A NumPy array of shape (n_candidates, n_features) with each candidate window flattened.
         - sample_hours: A list of starting indices for each candidate window.
    """
    # Load the electric load data
    electricload_path = scenario_data_path / "electricload.csv"
    print(f"Loading data from {electricload_path}")
    df = pd.read_csv(electricload_path)
    
    # Convert the 'time' column to datetime
    print("Converting time column to datetime")
    df = make_datetime(df, time_format)
    
    # Get all available years
    available_years = df['time'].dt.year.unique()
    print(f"Available years: {available_years}")
    
    all_candidates = []
    all_sample_hours = []
    all_years = []
    all_seasons = []
    
    for year in available_years:
        print(f"Processing year {year}")
        # Filter data for the specified season and year
        df_season = year_season_filter(df, year, season)
        df_season = df_season.reset_index(drop=True)
        
        # Remove non-numeric columns (time, year, etc.) so that only load values remain
        df_numeric = remove_time_index(df_season)
        
        n_rows = df_numeric.shape[0]
        if n_rows < regularSeasonHours:
            print(f"Warning: Not enough data points in year {year}, season {season}. Skipping.")
            continue
            
        # Calculate the maximum starting index for the candidate windows
        max_start = n_rows - regularSeasonHours - 1
        
        # Slide the window over the data
        for i in range(max_start):
            # Flatten the window (all columns concatenated)
            window = df_numeric.iloc[i:i + regularSeasonHours].values.flatten()
            all_candidates.append(window)
            all_sample_hours.append(i)
            all_years.append(year)
            all_seasons.append(season)
    
    if not all_candidates:
        raise ValueError(f"No valid windows found for season {season}")
    
    # Convert to numpy arrays
    candidates = np.array(all_candidates, dtype=float)  # Ensure numeric type
    sample_hours = np.array(all_sample_hours)
    years = np.array(all_years)
    seasons = np.array(all_seasons)
    
    # Create a structured array to hold both numeric and string data
    dtype = [('Year', int), ('Season', 'U10')] + [('Feature{}'.format(i), float) for i in range(candidates.shape[1])]
    structured_candidates = np.zeros(len(candidates), dtype=dtype)
    structured_candidates['Year'] = years
    structured_candidates['Season'] = seasons
    for i in range(candidates.shape[1]):
        structured_candidates['Feature{}'.format(i)] = candidates[:, i]
    
    print(f"Final candidates array shape: {structured_candidates.shape}")
    return structured_candidates, sample_hours

def make_voronoi_filter(scenario_data_path: Path, 
                        regularSeasonHours: int, 
                        time_format: str, 
                        n_cluster: int = 10,
                        mu_percentile: int = 80) -> pd.DataFrame:
    """
    Create a Voronoi-based filter for scenario generation.
    
    Parameters:
      scenario_data_path: Path to the folder containing scenario data files.
      regularSeasonHours: Number of consecutive hours that form one candidate window.
      time_format: Datetime format used in the CSV file.
      n_cluster: Number of clusters to create.
      mu_percentile: Percentile used for automatic mu calculation (default: 80)
      
    Returns:
      A DataFrame containing the filter with columns:
        - Year: The year of the data
        - Season: The season (e.g., "winter", "spring", etc.)
        - SampleIndex: The starting hour index for the window
        - ClusterGroup: The cluster assignment (-1 for singletons)
    """
    # Create output directory if it doesn't exist
    output_dir = Path.cwd() / "VoronoiClusters"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each season
    seasons = ["winter", "spring", "summer", "fall"]
    all_results = []
    
    for season in seasons:
        print(f"\nProcessing season: {season}")
        
        # Extract candidate windows for all years
        candidates, sample_hours = extract_candidate_windows(
            scenario_data_path, season, regularSeasonHours, time_format
        )
        
        # Compute Voronoi clusters
        clusters_df = compute_voronoi_clusters(
            candidates, n_cluster=n_cluster, output_dir=output_dir, mu_percentile=mu_percentile)
        
        # Add sample hours to the DataFrame
        clusters_df['SampleIndex'] = sample_hours
        
        # Save the results for this season
        all_results.append(clusters_df)
    
    # Combine results from all seasons
    final_df = pd.concat(all_results, ignore_index=True)
    
    # Save the final filter
    output_path = output_dir / "voronoi_filter.csv"
    final_df.to_csv(output_path, index=False)
    print(f"\nSaved Voronoi filter to {output_path}")
    
    return final_df
