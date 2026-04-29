import osmnx as ox
from slugify import slugify
from growbikenet.functions import *
from growbikenet.visualizations import *


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
    
    # Check if user input is valid
    if type(city_name) != str:
        raise TypeError("city_name must be a string")
    if type(proj_crs) != str:
        raise TypeError("proj_crs must be a string")
    if type(ranking) != str:
        raise TypeError("ranking must be a string")
    if ranking not in ["betweenness_centrality", "closeness_centrality", "all"]:
        raise ValueError(
            "ranking must be either 'betweenness_centrality', 'closeness_centrality', or 'all'"
        )
    if seed_point_type != "grid" and seed_point_type != "rail":
        raise ValueError("seed_point_type must be 'grid' or 'rail'")
    if seed_point_type == "grid" and type(seed_point_grid_spacing) != int:
        raise TypeError("seed_point_grid_spacing must be an integer")
    if seed_point_type == 'grid' and type(seed_point_grid_spacing) == int and seed_point_grid_spacing <= 0:  
        raise ValueError("seed_point_grid_spacing must be a positive integer")
    if type(seed_point_delta) != int:
        raise TypeError("seed_point_delta must be an integer")
    if type(seed_point_delta) == int and seed_point_delta <= 0:
        raise ValueError("seed_point_delta must be a positive integer")
    if type(existing_network_spacing) is not int and existing_network_spacing is not None:
        raise TypeError("existing_network_spacing must be None or a positive integer")
    if type(existing_network_spacing) is int and existing_network_spacing <= 0:
        raise ValueError("existing_network_spacing must be None or a positive integer")
    if type(export_data) != bool:
        raise TypeError("export_data must be a boolean")
    if export_data_slug is not None and type(export_data_slug) != str:
        raise TypeError("export_data_slug must be None or a string")
    if type(export_data_slug) == str and (
        len(export_data_slug) < 1 or len(slugify(export_data_slug)) < 1
    ):
        raise ValueError(
            "export_data_slug must contain at least one non-special character"
        )
    if type(export_plots) != bool:
        raise TypeError("export_plots must be a boolean")
    if type(export_video) != bool:
        raise TypeError("export_video must be a boolean")

    np.random.seed(42)  # Set random number generator seed for reproducibility

    ### Download and preprocess data from OSM
    print("Downloading OSM data..")

    # Fetch street network data from osmnx
    nodes, edges, g_undir = prepare_network(city_name, proj_crs, network_type='all_public', retain_all=False)

    if existing_network_spacing:
        cf = ['["cycleway"~"track"]',
              '["highway"~"cycleway"]',
              '["highway"~"path"]["bicycle"~"designated"]',
              '["cycleway:right"~"track"]',
              '["cycleway:left"~"track"]',
              '["cyclestreet"]',
              '["highway"~"living_street"]'
             ]
        for custom_tag in ["cycleway", "bicycle", "cycleway:right", "cycleway:left", "cyclestreet"]:
            if custom_tag not in ox.settings.useful_tags_way:
                ox.settings.useful_tags_way.extend(custom_tag)
        nodes_exnw, edges_exnw, g_undir_exnw = prepare_network(city_name, proj_crs, custom_filter=cf, retain_all=True)
        g_undir = nx.compose(g_undir_exnw, g_undir) # Merge to be sure we have everything from both
        # Take largest connected component lcc
        lcc = max(nx.connected_components(g_undir), key=len)
        g_undir = g_undir.subgraph(lcc).copy() 
        # TO DO: Restrict nodes and edges of existing net to the lcc
        # print(g_undir.nodes())
        # print(nodes_exnw)
        # print(edges_exnw)
        # sys.exit()
        _, edges = nx_to_nodes_edges(g_undir, proj_crs)

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
        seed_points.to_crs(edges.crs, inplace=True)

    # Snap seed points to OSM nodes
    seed_points_snapped = snap_seed_points(seed_points, nodes)
    seed_points_snapped = filter_seed_points(seed_points_snapped, seed_point_delta)
    
    if existing_network_spacing:
        # If the existing bicycle network is used, create extra seed points on it. They are by construction already snapped.
        # print(nodes_exnw)
        # sys.exit()
        seed_points_exnw = get_existing_network_seed_points(nodes_exnw, existing_network_spacing)
        seed_points_exnw.to_crs(edges.crs, inplace=True)

        # Afterwards, drop all previously determined seed points (grid or rail) that are now too close to these extra points.
        buffer_seed_points_exnw = gpd.GeoDataFrame(seed_points_exnw.buffer(existing_network_spacing))
        buffer_seed_points_exnw = buffer_seed_points_exnw.rename(columns={0:'geometry'}).set_geometry('geometry') # https://gis.stackexchange.com/questions/266098/how-to-convert-a-geoseries-to-a-geodataframe-with-geopandas
        buffer_seed_points_exnw.to_crs(edges.crs, inplace=True)

        # Delete the seed points that are too close to seed_points_exnw via its buffer
        seed_points_snapped = seed_points_snapped.overlay(buffer_seed_points_exnw, how='difference')

        # Merge original snapped points with new existing network points (=already snapped)
        seed_points_snapped = seed_points_snapped.overlay(seed_points_exnw, how='union')

        # Bring back to original form (geometry and osmid columns, osmid index)
        # This is a bit of a mess but it works. Simplify it in the future.
        seed_points_snapped.loc[seed_points_snapped['osmid_1'].isnull(), 'osmid_1'] = seed_points_snapped['osmid_2'] # _1 comes from one side, _2 from the other. One has NaNs, the other too. https://stackoverflow.com/a/60132614
        seed_points_snapped.drop(["y","x","street_count", "highway", "railway", "osmid_2"], axis=1, inplace=True)
        seed_points_snapped.rename(columns={"osmid_1": "osmid"}, inplace=True)
        seed_points_snapped.set_index("osmid", drop=False, inplace=True)
        
        # seed_points_snapped.drop(["osmid"], axis=1, inplace=True)
        # print(seed_points_snapped)
        # seed_points_snapped.to_file("test.gpkg", driver="GPKG")
        
    # Abort if only 0 or 1 seed points
    if len(seed_points_snapped) < 2:
        raise RuntimeError("Found less than 2 seed points, but more are needed.")

    ### Triangulate
    # Triangulation is calculated for the abstract network, but metrics (betweenness, closeness) are calculated for the routed network accounting for lengths.
    print("Greedy triangulation..")

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

    a_edges = gpd.GeoDataFrame(a_edges, crs=edges.crs, geometry="geometry")

    # Generate export data filename
    if export_data or export_plots or export_video:
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
        a_edges.to_file(export_data_filename, driver="GPKG")

    if export_plots or export_video:
        ### Visualize
        print("Creating visualizations..")

        # Create directories
        os.makedirs("./results/", exist_ok=True)
        os.makedirs("./results/plots/", exist_ok=True)
        os.makedirs("./results/plots/video/", exist_ok=True)

        # Read in file to plot
        routed_edges_gdf = gpd.read_file(export_data_filename)

        # Viz/plot settings (move to config file later)

        # Define color palette (from Michael's project: https://github.com/mszell/bikenwgrowth/blob/main/parameters/parameters.py)
        streetcolor = "#999999"
        edgecolor = "#0EB6D2"
        seedcolor = "#ff7338"

        # Define linewidths

        lws = {"street": 0.75, "bike": 2}

        create_plots(
            routed_edges_gdf,
            seed_points_snapped,
            streetcolor,
            edgecolor,
            seedcolor,
            lws,
        )
        if export_video:
            print("Generating video..")
            make_video(img_folder_name="./results/plots/", fps=1)

    return a_edges
