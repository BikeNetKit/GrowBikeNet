import os
import numpy as np
import networkx as nx
import osmnx as ox
import geopandas as gpd
from slugify import slugify
import warnings
from growbikenet.functions import (
    get_principal_bearing,
    get_grid_seed_points,
    snap_seed_points,
    filter_seed_points,
    create_delaunay_edges,
    add_path_to_df,
    create_gdf_with_geoms,
    node_to_edge_attributes,
    df_from_graph,
    rank_df,
)
from growbikenet.visualizations import make_video, create_plots


def growbikenet(
    city_name,
    proj_crs="3857",
    ranking="betweenness_centrality",
    seed_point_type="grid",
    seed_point_grid_spacing=1707,
    seed_point_delta=500,
    existing_network_spacing=None,
    export_data=True,
    export_data_slug=None,
    export_plots=False,
    export_video=False,
):
    """Creates a list of edges ordered by a specified ranking method.

    The edges form a subnetwork of a city's street network, interpreted as a growing bicycle network following [1]_. By default, growth is from scratch, but the existing bicycle network can also be used as a starting point[2]_. Note that the original paper [1]_ uses minimum weight triangulation, but Delaunay triangulation is much faster due to the Delaunay scipy function and gives in most cases identical results. Triangulation is calculated for the abstract network, but metrics (betweenness, closeness) are calculated for the routed network accounting for lengths.

    Parameters
    ----------
    city_name : str
        Name of the city that the analysis should be performed on
    proj_crs : str, default '3857'
        Coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator)
    ranking : str, default 'betweenness_centrality'
        Method used to rank edges. Must be 'betweenness_centrality' (default), 'closeness_centrality', or 'all'. If 'all', will also add a random ranking.
    seed_point_type : str, optional, default 'grid'
        If set to 'grid', creates a square grid
        If set to 'rail', uses rail stations
    seed_point_grid_spacing : int, optional, default 1707
        If seed_point_type is set to 'grid', this is the spacing between seed points, in meters
    seed_point_delta : int, optional, default 500
        Maximum distance between generated seed points and osm nodes for snapping
    existing_network_spacing : int, optional, default None
        Spacing between seed points, in meters, only on the existing bicycle network. If not set to a positive integer, the existing network is ignored.
    export_data : bool, optional, default True
        If set to True, data will be saved to a file. The filename is [slug]-[ranking]-[seed_point_type].gpkg, where slug is a string id made out of city_name
    export_data_slug : string, optional, default None
        If not set to None, it will be slugified and used as the slug in the filename of the data export
    export_plots : bool, optional, default False
        If set to True, plots will be saved to a file
    export_video : bool, optional, default False
        If set to True, video will be saved to a file (only possible if export_plots is set to True)

    Returns
    -------
    a_edges : geopandas.geodataframe.GeoDataFrame
        ordered geodataframe of all edges in street network

    References
    ----------
    .. [1] M. Szell, S. Mimar, T. Perlman, G. Ghoshal, R. Sinatra, "Growing urban bicycle networks", Scientific Reports 12, 6765 (2022)
    .. [2] P. Folco, L. Gauvin, M. Tizzoni, M. Szell, "Data-driven micromobility network planning for demand and safety", Environment and planning B: Urban analytics and city science 50(8), 2087-2102 (2023)

    """
    # check if user input is valid
    if type(city_name) is not str:
        raise TypeError("city_name must be a string")
    if type(proj_crs) is not str:
        raise TypeError("proj_crs must be a string")
    if type(ranking) is not str:
        raise TypeError("ranking must be a string")
    if ranking not in ["betweenness_centrality", "closeness_centrality", "all"]:
        raise ValueError(
            "ranking must be either 'betweenness_centrality', 'closeness_centrality', or 'all'"
        )
    if seed_point_type != "grid" and seed_point_type != "rail":
        raise ValueError("seed_point_type must be 'grid' or 'rail'")
    if seed_point_type == "grid" and type(seed_point_grid_spacing) is not int:
        raise TypeError("seed_point_grid_spacing must be an integer")
    if seed_point_type == 'grid' and type(seed_point_grid_spacing) is int and seed_point_grid_spacing <= 0:  
        raise ValueError("seed_point_grid_spacing must be a positive integer")
    if type(seed_point_delta) is not int:
        raise TypeError("seed_point_delta must be an integer")
    if type(seed_point_delta) is int and seed_point_delta <= 0:
        raise ValueError("seed_point_delta must be a positive integer")
    if type(existing_network_spacing) is not int and existing_network_spacing is not None:
        raise TypeError("existing_network_spacing must be None or a positive integer")
    if type(existing_network_spacing) is int and existing_network_spacing <= 0:
        raise ValueError("existing_network_spacing must be None or a positive integer")
    if type(existing_network_spacing) is int and existing_network_spacing >= seed_point_grid_spacing:
        warnings.warn("existing_network_spacing is recommended to be smaller than seed_point_grid_spacing to ensure that the existing bicycle network is built first.")
    if type(seed_point_delta) is not int:
        raise TypeError("seed_point_delta must be an integer")
    if type(export_data) is not bool:
        raise TypeError("export_data must be a boolean")
    if export_data_slug is not None and type(export_data_slug) is not str:
        raise TypeError("export_data_slug must be None or a string")
    if type(export_data_slug) is str and (
        len(export_data_slug) < 1 or len(slugify(export_data_slug)) < 1
    ):
        raise ValueError(
            "export_data_slug must contain at least one non-special character"
        )
    if type(export_plots) is not bool:
        raise TypeError("export_plots must be a boolean")
    if type(export_video) is not bool:
        raise TypeError("export_video must be a boolean")

    np.random.seed(42)  # Set random number generator seed for reproducibility

    ### Download and preprocess data from OSM
    print("Downloading OSM data..")

    # Fetch street network data from osmnx
    # Due to retain_all=False, this fetches the largest connected component
    nodes, edges, g_undir = prepare_network(city_name, proj_crs, network_type='all_public', retain_all=False)

    if existing_network_spacing:
        nodes, edges, g_undir, nodes_exnw, edges_exnw = update_with_existing_bike_network(city_name, proj_crs, g_undir)

    ### Create seed points
    print("Creating " + seed_point_type + " seed points..")

    if seed_point_type == "grid":
        # Bearings work on unprojected graph
        ox.bearing.add_edge_bearings(g_undir)
        principal_bearing = get_principal_bearing(g_undir)

        # But this is on the projected edges now
        seed_points = get_grid_seed_points(
            edges, seed_point_grid_spacing, principal_bearing
        )
    elif seed_point_type == "rail":
        seed_points = ox.features_from_place(
            city_name, {"railway": ["station", "halt"]}
        )
        seed_points = seed_points[seed_points["geometry"].type == "Point"]
        seed_points.to_crs(proj_crs, inplace=True)

    # Snap seed points to OSM nodes
    seed_points_snapped = snap_seed_points(seed_points, nodes)
    seed_points_snapped = filter_seed_points(seed_points_snapped, seed_point_delta)
    
    if existing_network_spacing:
        seed_points_snapped = update_seed_points_with_existing_bike_network(seed_points_snapped, nodes_exnw, existing_network_spacing, proj_crs)
          
    # Abort if only 0 or 1 seed points
    if len(seed_points_snapped) < 2:
        raise RuntimeError("Found less than 2 seed points, but more are needed.")

    ### Triangulate
    # Triangulation is calculated for the abstract network, but metrics (betweenness, closeness) are calculated for the routed network accounting for lengths.
    print("Triangulation..")

    # Create df with delaunay edges
    df = create_delaunay_edges(seed_points_snapped)

    # Map each abstract edge to a merged geometry of corresponding osmnx edges (routed on g_undir)
    df = add_path_to_df(df, edges, g_undir)

    # Get "routed" geometry (LineString) for each abstract edge (row)
    print("Routing..")
    gdf = create_gdf_with_geoms(df, edges)

    # Add distances between source and target from geometry
    gdf["dist"] = gdf["geometry"].length

    edge_list = gdf["pair"]
    dist_list = gdf["dist"]
    dist_dict = dict(zip(edge_list, dist_list))
    geom_dict = dict(zip(edge_list, gdf["geometry"].tolist()))

    # Make graph object from edge list
    A = nx.Graph()
    A.add_nodes_from(seed_points_snapped.index)
    A.add_edges_from(edge_list)
    nx.set_edge_attributes(A, dist_dict, "distance")
    nx.set_edge_attributes(A, geom_dict, "geometry")

    ### Compute edge attributes
    print("Computing edge attributes..")
    if ranking == "betweenness_centrality" or ranking == "all":
        # Add betweenness attributes to edges
        bc_values = nx.edge_betweenness_centrality(
            A, weight="distance", normalized=True
        )
        nx.set_edge_attributes(A, bc_values, name="betweenness_centrality")
    if ranking == "closeness_centrality" or ranking == "all":
        # Add closeness attributes to nodes and edges
        cc_values_nodes = nx.closeness_centrality(A, distance="distance")
        nx.set_node_attributes(A, cc_values_nodes, name="closeness_centrality")
        cc_values = node_to_edge_attributes(cc_values_nodes, A.edges)
        nx.set_edge_attributes(A, cc_values, name="closeness_centrality")

    ### Export attributes to gdfs:

    # Create dataframe and add method as edge attribute
    a_edges = df_from_graph(A, ranking)

    # Rank edges by specified method
    a_edges = rank_df(a_edges, ranking)

    a_edges = gpd.GeoDataFrame(a_edges, crs=proj_crs, geometry="geometry")

    # Generate export data filename
    if export_data or export_plots or export_video:
        os.makedirs("./results/", exist_ok=True)
        if export_data_slug is None:
            city_string = city_name
        else:
            city_string = export_data_slug
        export_data_filename = (
            slugify(city_string) + "-" + ranking + "-" + seed_point_type + ".gpkg"
        )

    # Save to file
    if export_data:
        ### save data
        print("Saving data..")
        a_edges.to_file("./results/"+export_data_filename, driver="GPKG")

    if export_plots or export_video:
        ### Visualize
        print("Creating visualizations..")

        # Read in file to plot
        routed_edges_gdf = gpd.read_file(export_data_filename)

        # Viz/plot settings (move to config file later)
        # Define color palette (from Michael's project: https://github.com/mszell/bikenwgrowth/blob/main/parameters/parameters.py)
        streetcolor = "#999999"
        edgecolor = "#0EB6D2"
        seedcolor = "#ff7338"
        # Define linewidths
        lws = {"street": 0.75, "bike": 2}

        if ranking == "all": 
            ranking_list = ["betweenness_centrality", "closeness_centrality", "random"]
        else:
            ranking_list = [ranking]
        for ranking_this in ranking_list:
            os.makedirs("./results/plots/ordering_"+ranking_this+"/", exist_ok=True)
            create_plots(
                routed_edges_gdf,
                seed_points_snapped,
                streetcolor,
                edgecolor,
                seedcolor,
                lws,
                ranking_this,
            )

        if export_video:
            for ranking_this in ranking_list:
                print("Generating video..")
                os.makedirs("./results/plots/ordering_"+ranking_this+"/video/", exist_ok=True)
                make_video(img_folder_name="./results/plots/ordering_"+ranking_this+"/", fps=5)

    return a_edges
