import osmnx as ox
from growbikenet.functions import *
from growbikenet.visualizations import *

def growbikenet(
        city_name,
        proj_crs='3857',
        ranking='betweenness_centrality',
        seed_point_type='grid',
        seed_point_grid_spacing=1707,
        seed_point_delta=500,
        export_data=True,
        export_data_slug=None,
        export_plots=False,
        export_video=False,
):
    """
creates list of edges that form city network, ordered by specified ranking method

Parameters
----------
city_name : str
    name of the city that the analysis should be performed on
proj_crs : str, default '3857'
    coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator)
ranking : str, default 'betweenness_centrality'
    method used to rank edges. Must be 'betweenness_centrality' (default) or 'closeness_centrality'
seed_point_type : str, optional, default 'grid'
    if set to 'grid', creates a square grid
    if set to 'rail', uses rail stations
seed_point_grid_spacing : int, optional, default 1707
    if seed_point_type is set to 'grid', this is the spacing between seed points, in meters
seed_point_delta : int, optional, default 500
    maximum distance between generated seed points and osm nodes for snapping
export_data : bool, optional, default True
    if set to True, data will be saved to a file. The filename is [slug]-[ranking]-[seed_point_type].gpkg, where slug is a string id made out of city_name
export_data_slug : string, optional, default None
    if not set to None, it will be slugified and used as the slug in the filename of the data export
export_plots : bool, optional, default False
    if set to True, plots will be saved to a file
export_video : bool, optional, default False
    if set to True, video will be saved to a file (only possible if export_plots is set to True)

Returns
-------
a_edges : geopandas.geodataframe.GeoDataFrame
    ordered geodataframe of all edges in street network

"""
    # check if user input is valid
    if type(city_name) != str:
        raise TypeError("city_name must be a string")
    if type(proj_crs) != str:
        raise TypeError("proj_crs must be a string")
    if type(ranking) != str:
        raise TypeError("ranking must be a string")
    if ranking != 'betweenness_centrality' and ranking != 'closeness_centrality':
        raise ValueError("ranking must be 'betweenness_centrality' or 'closeness_centrality'")
    if seed_point_type != 'grid' and seed_point_type != 'rail':
        raise ValueError("seed_point_type must be 'grid' or 'rail'")
    if seed_point_type == 'grid' and type(seed_point_grid_spacing) != int:
        raise TypeError("seed_point_grid_spacing must be an integer")
    if type(seed_point_delta) != int:
        raise TypeError("seed_point_delta must be an integer")
    if type(export_data) != bool:
        raise TypeError("export_data must be a boolean")
    if export_data_slug is not None and type(export_data_slug) != str:
        raise TypeError("export_data_slug must be None or a string")
    if type(export_data_slug) == str and (len(export_data_slug) < 1 or len(slugify(export_data_slug)) < 1):
        raise ValueError("export_data_slug must contain at least one non-special character")
    if type(export_plots) != bool:
        raise TypeError("export_plots must be a boolean")
    if type(export_video) != bool:
        raise TypeError("export_video must be a boolean")


    ### downloading and preprocessing data from OSM
    print("Downloading OSM data..")

    # fetch street network data from osmnx
    g = ox.graph_from_place(
    city_name, network_type='all'
    )
    g_undir = g.to_undirected().copy() # convert to undirected (dropping OSMnx keys!)

    # export osmnx data to gdfs
    nodes, edges = ox.graph_to_gdfs(
    g_undir,
    nodes=True,
    edges=True,
    node_geometry=True,
    fill_edge_geometry=True
    )

    # # save "original" graph data (in orig_crs)
    # nodes.to_file("nodes.gpkg", driver='GPKG')
    # edges.to_file("edges.gpkg", driver='GPKG')

    # replace after dropping edges with key = 1
    edges = edges.loc[:,:,0].copy()
    # this also means we are dropping the "key" level from edge index (u,v,key becomes: u,v)

    # project geometries of nodes, edges, seed points
    edges = edges.to_crs(proj_crs)
    nodes = nodes.to_crs(proj_crs)

    # add osm ID as column to node gdf
    nodes["osmid"] = nodes.index

    ### creating seed points
    print("Creating " + seed_point_type + " seed points..")

    if seed_point_type == "grid":
        # Bearings work on unprojected graph
        ox.bearing.add_edge_bearings(g_undir)
        principal_bearing = get_principal_bearing(g_undir)

        # But this is on the projected edges now
        seed_points = get_grid_seed_points(edges, seed_point_grid_spacing, principal_bearing)
    elif seed_point_type == "rail":
        seed_points = ox.features_from_place(city_name, {'railway':['station','halt']})
        seed_points = seed_points[seed_points['geometry'].type == "Point"]
        seed_points.to_crs(edges.crs, inplace=True)

    # Snap seed points to OSM nodes
    seed_points_snapped = snap_seed_points(seed_points, nodes)
    seed_points_snapped = filter_seed_points(seed_points_snapped, seed_point_delta)

    # Abort if only 0 or 1 seed points
    if len(seed_points_snapped) < 2:
        raise RuntimeError("Found less than 2 seed points")
    

    ### running greedy triangulation
    print("Greedy triangulation..")

    # create df with all potential edges in triangulation
    df = create_potential_triangulation(seed_points_snapped)

    # filter edges that intersect with existing edges
    edge_list = filter_triangulation(df)

    # make graph object from edge list
    A = nx.Graph()
    A.add_nodes_from(seed_points_snapped.index)
    A.add_edges_from(edge_list)

    ### compute edge attributes
    print("Computing edge attributes..")

    if ranking == 'betweenness_centrality':
        # add betweenness attributes to edges
        bc_values = nx.edge_betweenness_centrality(A, normalized=True)
        nx.set_edge_attributes(A, bc_values, name='betweenness_centrality')

    elif ranking == 'closeness_centrality':
        # add closeness attributes to nodes and edges
        cc_values_nodes = nx.closeness_centrality(A)
        nx.set_node_attributes(A, cc_values_nodes, name='closeness_centrality')

        cc_values = node_to_edge_attributes(cc_values_nodes, A.edges)
        nx.set_edge_attributes(A, cc_values, name='closeness_centrality')

    # export attributes to gdfs:

    # create dataframe and add method as edge attribute
    a_edges = df_from_graph(A, ranking)

    # rank edges by specified method
    a_edges = rank_df(a_edges, ranking)

    # map each abstract edge to a merged geometry of corresponding osmnx edges (routed on g_undir)
    a_edges = add_path_to_df(a_edges, edges, g_undir)

    ### route abstract edges on street network
    print("Routing..")

    # get "routed" geometry (LineString) for each abstract edge (row)
    a_edges = create_gdf_with_geoms(a_edges, edges)

    
    # generate export data filename
    if export_data or export_plots or export_video:
        if export_data_slug is None:
            city_string = city_name
        else:
            city_string = export_data_slug
        export_data_filename = slugify(city_string) + "-" + ranking + "-" + seed_point_type + ".gpkg"

    # save to file
    if export_data:
        ### save data
        print("Saving data..")
        a_edges.to_file(export_data_filename, driver="GPKG")

    if export_plots or export_video:
        ### Visualization
        print("Creating visualizations..")

        # create directories
        os.makedirs("./results/", exist_ok=True)
        os.makedirs("./results/plots/", exist_ok=True)
        os.makedirs("./results/plots/video/", exist_ok=True)

        # read in file to plot
        routed_edges_gdf = gpd.read_file(export_data_filename)

        # viz/plot settings (move to config file later)

        # define color palette (from Michael's project: https://github.com/mszell/bikenwgrowth/blob/main/parameters/parameters.py)
        streetcolor = "#999999"
        edgecolor = "#0EB6D2"
        seedcolor = "#ff7338"

        # define linewidths

        lws = {
        "street": 0.75,
        "bike": 2
        }

        create_plots(routed_edges_gdf,seed_points_snapped,streetcolor,edgecolor,seedcolor,lws)
        if export_video:
            print("Generating video..")
            make_video(
                img_folder_name="./results/plots/",
                fps = 1
            )

    return a_edges