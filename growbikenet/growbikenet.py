import os
import numpy as np
import networkx as nx
import osmnx as ox
import geopandas as gpd
import pandas as pd
from slugify import slugify
import warnings
from tqdm import tqdm
import time
import datetime
from growbikenet.functions import (
    validate_parameters,
    orientation_order,
    resolve_auto_parameters,
    get_principal_bearing,
    prepare_seed_points,
    get_grid_seed_points,
    get_tags_seed_points,
    snap_seed_points,
    filter_seed_points,
    create_delaunay_edges,
    add_path_to_df,
    create_gdf_with_geoms,
    node_to_edge_attributes,
    df_from_graph,
    rank_df,
    download_network,
    update_with_existing_bike_network,
    update_seed_points_with_existing_bike_network,
    remove_edge_overlaps,
    import_network,
)
from growbikenet.visualizations import make_video, create_plots


def growbikenet(
    city_name,
    crs_projected='3857',
    ranking='betweenness_centrality',
    seed_point_type='auto',
    seed_point_grid_spacing='auto',
    seed_point_delta='auto',
    seed_point_linking='auto',
    existing_network_spacing=None,
    export_data=True,
    export_file_format='geojson',
    export_data_slug=None,
    export_plots=False,
    export_video=False,
    allow_edge_overlaps=False,
    city_boundary_file=None,
    street_network_file=None,
    seed_points_file=None,
    seed_point_tags=None,
):
    """Creates a list of urban street network edges ordered by a ranking method.

    The edges form a subnetwork of a city's street network, interpreted as a growing bicycle network following [1]_. By default, growth is from scratch, but the existing bicycle network can also be used as a starting point[2]_. The original paper [1]_ uses minimum weight triangulation, but Delaunay triangulation is implemented much faster and in practice gives identical results. Triangulation and metrics (betweenness, closeness) are calculated for the unrouted, abstract network for which egde lengths are taken from the routed network.

    Parameters
    ----------
    city_name : str
        Name of the city that the analysis should be performed on. This is the query string used to fetch the data from nominatim. Overruled for data fetching if city_boundary_file or street_network_file is set.
    crs_projected : str, default '3857'
        Coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator). If this web mercator projection is not needed, then for Europe '3035' (LAEA) and globally '54035' (Equal Earth) is better.
    ranking : str, default 'betweenness_centrality'
        Method used to rank edges. Must be 'betweenness_centrality' (default), 'closeness_centrality', or 'random'.
    seed_point_type : str ('auto' | 'grid_square' | 'grid_triangle' | 'rail' | 'school' | 'park' | 'file' | 'tags'), default 'auto'
        If set to 'auto', selects 'grid_square' or 'grid_triangle' automatically depending on the street network's orientation entropy, see [3]_.
        If set to 'grid_square', creates a square grid. 
        If set to 'grid_triangle', creates a triangle grid. In this case, seed_point_linking must not be set to 'quadrangulate'.
        If set to 'rail', uses railway stations and halts.
        If set to 'school', uses kindergartens, schools, colleges, and universities.
        If set to 'park', uses parks, gardens, nature reserves, and public bathing places.
        If set to 'file', imports seed_points_file.
        If set to 'tags', uses geocodable seed_point_tags, see [4]_. 
    seed_point_grid_spacing : 'auto' | int, default 'auto'
        If seed_point_type is set to 'grid_square' or 'grid_triangle', this is the spacing between seed points, in meters.
        Auto-value for seed_point_type 'grid_square' with seed_point_linking 'triangulate_delaunay': 1707
        Auto-value for seed_point_type 'grid_square' with seed_point_linking 'quadrangulate': 1000
        Auto-value for seed_point_type 'grid_triangle': 1154
        Auto-value otherwise: 1707
        These values ensure that any point in the city is always within 500m of the network (under perfect conditions). For case 1707, see [1]_.
    seed_point_delta : 'auto' | int, default 'auto'
        Maximum distance between raw seed points and osm nodes for snapping, in meters.
        Auto-value is round(seed_point_grid_spacing/4).
    seed_point_linking : str ('auto' | 'triangulate_delaunay' | 'quadrangulate'), default 'auto'
        The algorithm for linking up the seed points into an unrouted, abstract network.
        If set to 'auto', selects 'triangulate_delaunay' or 'quadrangulate' automatically depending on the street network's orientation entropy, see [3]_.
        If set to 'triangulate_delaunay', uses Delaunay triangulation.
        If set to 'quadrangulate', uses quadrangulation, which only works for seed_point_type 'grid_square' and existing_network_spacing None. Useful for grid-like street networks like Manhattan or Barcelona.
    existing_network_spacing : int, default None
        Spacing between seed points, in meters, only on the existing bicycle network. If not set to a positive integer, the existing network is ignored. existing_network_spacing is recommended to be smaller than seed_point_grid_spacing, ideally around 25%, to ensure that the existing bicycle network is built first.
    export_data : bool, default True
        If set to True, data is saved to a file. The filename is [slug]-[ranking]-[seed_point_type].[export_file_format], where slug is a string id made out of city_name.
    export_file_format : str ('geojson' | 'gpkg'), default 'geojson'
        File format for the data export, relevant if export_data set to True. Default 'geojson', also possible 'gpkg'. If exporting as geojson, generates extra files for seed points and city boundary. If exporting as gkpg, these are added all in one file as extra layers.
    export_data_slug : str | None, default None
        If not set to None, the city_name will be slugified and used as the slug in the filename of the data export.
    export_plots : bool, default False
        If set to True, plots are saved to files, overwriting existing ones.
    export_video : bool, default False
        If set to True, video is saved to file (only possible if export_plots is set to True), overwriting existing ones.
    allow_edge_overlaps : bool, default False
        If set to False, removes edge overlaps in consecutive growth stages and deletes growth stages that do not add anything new.
    city_boundary_file : str | None, default None
        If not set to None, the study area will be selected from the (Multi)Polygon provided in the city_boundary_file shape file, ideally in unprojected latitude-longitude degrees (EPSG:4326), but EPSG:3857 also works. For example, "./tests/test_data/copenhagen.shp". city_boundary_file and street_network_file cannot both be set.
    street_network_file : str | None, default None
        If not set to None, the street network will be loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326 with layers nodes and edges, with the structure that a osmnx street network has after saved via ox.io.save_graph_geopackage(). For example, "./tests/test_data/oelde_streets.shp". This does not work with seed_point_type="rail". city_boundary_file and street_network_file cannot both be set.
    seed_points_file : str | None, default None
        If not set to None, the seed points will be loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326 containing only point objects. For example, "./tests/test_data/oelde_seed_points.shp". seed_point_type must be set to 'file'.
    seed_point_tags : None | dict[str, bool | str | list[str]], default None
        If not None, must be a geocodable seed_point_tags, see [4]_, and seed_point_type must be set to 'tags'. For example, seed_point_tags={"railway": ["station", "halt"]} will retrieve exactly the same as seed_point_type='rail'.

    Returns
    -------
    edges_ranked : geopandas.geodataframe.GeoDataFrame
        ordered geodataframe of all edges in street network

    Examples
    --------
    Minimum working example: Grow a bicycle network from scratch in Lyon.

    >>> edges_ranked = growbikenet("Lyon")

    Grow a bicycle network from scratch in Copenhagen, providing a study area polygon to include also Frederiksberg and Amager.

    >>> edges_ranked = growbikenet("Copenhagen", city_boundary_file="./tests/test_data/copenhagen.shp") 

    Expand the existing bicycle network of Lyon, connecting all educational institutions.

    >>> edges_ranked = growbikenet("Lyon", seed_point_type='school', existing_network_spacing=500) 

    Grow a bicycle network in Oelde from scratch, working offline by importing the street network and custom seed points from file.

    >>> edges_ranked = growbikenet("Oelde", street_network_file="./tests/test_data/oelde_streets.gpkg", seed_point_type='file', seed_points_file="./tests/test_data/oelde_seed_points.gpkg")

    References
    ----------
    .. [1] M. Szell, S. Mimar, T. Perlman, G. Ghoshal, R. Sinatra, "Growing urban bicycle networks", Scientific Reports 12, 6765 (2022)
    .. [2] P. Folco, L. Gauvin, M. Tizzoni, M. Szell, "Data-driven micromobility network planning for demand and safety", Environment and planning B: Urban analytics and city science 50(8), 2087-2102 (2023)
    .. [3] G. Boeing, "Urban spatial order: Street network orientation, configuration, and entropy", Applied Network Science 4, 67 (2019)
    .. [4] https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.features.features_from_place

    """
    starttime = time.time()

    # Constants
    # Pre-defined tags to select tags as seed points
    PRESET_TAGS = {
                "rail": {"railway": ["station", "halt"]},
                "school": {"amenity": ["kindergarten", "school", "college", "university"]},
                "park": {"leisure": ["park", "garden", "nature_reserve", "bathing_place"]},
                }
    # Orientation order limits between street networks with:
    # 1) negligible grid elements, 2) some grid elements, 3) grid.
    # I aimed to use the tercile limits from the paper [4]_ (Fig 2), but the values
    # here are lower for unknown reasons, also with the unweighted version. Also, I 
    # wanted to have Barcelona in the grid category. So I lowered the limits.
    PHI_LIMITS = [0.02, 0.08] # Tercile limits in the paper: 0.033, 0.161
    
    validate_parameters(
        city_name,
        crs_projected,
        ranking,
        seed_point_type,
        seed_point_grid_spacing,
        seed_point_delta,
        seed_point_linking,
        existing_network_spacing,
        export_data,
        export_file_format,
        export_data_slug,
        export_plots,
        export_video,
        allow_edge_overlaps,
        city_boundary_file,
        street_network_file,
        seed_points_file,
        seed_point_tags,
        PRESET_TAGS
    )

    np.random.seed(42)  # Set random number generator seed for reproducibility

    print("==============================================")
    print("RUNNING GROWBIKENET FOR CITY: " + city_name)
    print(ranking + " | " + seed_point_type + " | " + ("from existing bike network " if existing_network_spacing else "from scratch"))
    print("----------------------------------------------╮")
    
    if street_network_file is not None:
        ### Import and preprocess data from file
        city_boundary_exists = False
        progress_bar = tqdm(
            desc="{:<23}".format("Importing network data"),
            total=1,
            unit="network",
            bar_format='{l_bar}{bar:16}{r_bar}',
        )
        nodes, edges, g_undir = import_network(street_network_file, crs_projected)
        progress_bar.update(1)
    else:
        ### Download and preprocess data from OSM
        city_boundary_exists = True
        progress_bar = tqdm(
            desc="{:<23}".format("Downloading OSM data"),
            total=1+int(bool(existing_network_spacing)),
            unit="network",
            bar_format='{l_bar}{bar:16}{r_bar}',
        )
        # Get city boundary 
        if city_boundary_file:
            city_boundary_shp = gpd.read_file(city_boundary_file)
            city_boundary_gdf = city_boundary_shp.iloc[[0]]    
        else:
            city_boundary_gdf = ox.geocoder.geocode_to_gdf(city_name)
        city_boundary_geometry = city_boundary_gdf.geometry[0]

        # Fetch street network data from osmnx
        # Due to retain_all=False, this fetches the largest connected component
        nodes, edges, g_undir = download_network(city_name, crs_projected, network_type='all_public', retain_all=False, city_boundary_geometry=city_boundary_geometry)
        progress_bar.update(1)

        if existing_network_spacing is not None: # update g_undir: add the existing bike network
            nodes, edges, g_undir, nodes_exnw, edges_exnw = update_with_existing_bike_network(city_name, crs_projected, g_undir, city_boundary_geometry=city_boundary_geometry)
            progress_bar.update(1)
    progress_bar.close()


    # Now that the graph is ready, decide auto values
    ox.bearing.add_edge_bearings(g_undir)
    phi = orientation_order(g_undir)
    seed_point_type, seed_point_grid_spacing, seed_point_delta, seed_point_linking, existing_network_spacing = resolve_auto_parameters(
        seed_point_type,
        seed_point_grid_spacing,
        seed_point_delta,
        seed_point_linking,
        existing_network_spacing,
        phi,
        PHI_LIMITS
    )
    # At this point no value should be on 'auto' any longer and inconsistencies should be resolved.


    ### Create seed points
    progress_bar = tqdm(
        desc="{:<23}".format("Creating seed points"),
        total=3+int(bool(existing_network_spacing)), # 3 or 4
        unit="step",
        bar_format='{l_bar}{bar:16}{r_bar}',
        )

    if seed_point_type == 'grid_square' or seed_point_type == 'grid_triangle':
        # Bearings work on unprojected graph
        principal_bearing = get_principal_bearing(g_undir)

        # But this is on the projected edges now
        seed_points, seed_network = get_grid_seed_points(
            edges, seed_point_grid_spacing, principal_bearing, seed_point_type
        ) # The seed_network is only relevant for quadrangulation
    elif seed_point_type in PRESET_TAGS:
        seed_point_tags = PRESET_TAGS[seed_point_type]
    elif seed_point_type == "file":
        seed_points = gpd.read_file(seed_points_file)
        seed_points = prepare_seed_points(seed_points, crs_projected)

    if seed_point_type == "tags" or seed_point_type in PRESET_TAGS:
        seed_points = get_tags_seed_points(city_name, crs_projected=crs_projected, tags=seed_point_tags, city_boundary_geometry=city_boundary_geometry)
    progress_bar.update(1)

    # Snap seed points to OSM nodes
    seed_points_snapped = snap_seed_points(seed_points, nodes)
    if seed_point_linking == "quadrangulate": # Map geometry to osmid
        mapping = {row.geometry_generated: row.osmid for row in seed_points_snapped.itertuples()}
        nx.relabel_nodes(seed_network, mapping, copy=False)
    progress_bar.update(1)
    seed_points_snapped_filtered = filter_seed_points(seed_points_snapped, seed_point_delta)
    if seed_point_linking == "quadrangulate": # Remove all filtered out nodes
        filtered_nodes = set(seed_points_snapped.osmid) - set(seed_points_snapped_filtered.osmid)
        seed_network.remove_nodes_from(filtered_nodes)
        seed_network = seed_network.subgraph(sorted(nx.connected_components(seed_network), key=len, reverse=True)[0]) # Keep only the largest connected component (the network might have fallen apart)
    progress_bar.update(1)

    if existing_network_spacing is not None:
        seed_points_snapped_filtered = update_seed_points_with_existing_bike_network(seed_points_snapped_filtered, nodes_exnw, existing_network_spacing, crs_projected)
        progress_bar.update(1)
    progress_bar.close()


    # Abort if less than 3 seed points. Triangulation needs at least 3.
    if len(seed_points_snapped_filtered) < 3:
        raise RuntimeError("Found less than 3 seed points, but more are needed.")

    if seed_point_linking != "quadrangulate":
        ### Triangulate
        # Triangulation and metrics (betweenness, closeness) are calculated for the unrouted, abstract network for which egde lengths are taken from the routed network.
        progress_bar = tqdm(
            desc="{:<23}".format("Triangulation"),
            total=1,
            unit="step",
            bar_format='{l_bar}{bar:16}{r_bar}',
            )
        # Create unrouted network with delaunay triangulation edges
        grown_bikenet_edges_abstract = create_delaunay_edges(seed_points_snapped_filtered)
    else: # Build the same dataframe structure for the abstract network from the seed_network.edges
        progress_bar = tqdm(
            desc="{:<23}".format("Quadrangulation"),
            total=1,
            unit="step",
            bar_format='{l_bar}{bar:16}{r_bar}',
            )
        grown_bikenet_edges_abstract = pd.DataFrame({
            'pair': seed_network.edges,
            'source': [e[0] for e in seed_network.edges],
            'target': [e[1] for e in seed_network.edges]
            }) # Afterwards, all steps are identical
    progress_bar.update(1)
    progress_bar.close()

    ### Get routed geometry (LineString) for each abstract edge (row)
    progress_bar = tqdm(
        desc="{:<23}".format("Routing"),
        total=3,
        unit="step",
        bar_format='{l_bar}{bar:16}{r_bar}',
        )

    # Map each unrouted edge to a merged geometry of corresponding osmnx edges (routed on g_undir)
    grown_bikenet_edges_abstract = add_path_to_df(grown_bikenet_edges_abstract, edges, g_undir)
    progress_bar.update(1)

    grown_bikenet_edges = create_gdf_with_geoms(grown_bikenet_edges_abstract, edges)
    progress_bar.update(1)

    # Add distances between source and target from geometry
    grown_bikenet_edges["dist"] = grown_bikenet_edges["geometry"].length

    edge_list = grown_bikenet_edges["pair"]
    dist_list = grown_bikenet_edges["dist"]
    dist_dict = dict(zip(edge_list, dist_list))
    geom_dict = dict(zip(edge_list, grown_bikenet_edges["geometry"].tolist()))

    # Make graph object from edge list
    B = nx.Graph() # B like bike network
    B.add_nodes_from(seed_points_snapped_filtered.index)
    B.add_edges_from(edge_list)
    nx.set_edge_attributes(B, dist_dict, "distance")
    nx.set_edge_attributes(B, geom_dict, "geometry")

    progress_bar.update(1)
    progress_bar.close()

    ### Compute edge attributes
    progress_bar = tqdm(
        desc="{:<23}".format("Computing edge metrics"),
        total=2,
        unit="step",
        bar_format='{l_bar}{bar:16}{r_bar}',
        )

    # The ranking=="random" case has no edge attributes and is handled in rank_df
    if ranking == "betweenness_centrality":
        # Add betweenness attributes to edges
        bc_values = nx.edge_betweenness_centrality(
            B, weight="distance", normalized=True
        )
        nx.set_edge_attributes(B, bc_values, name="betweenness_centrality")
    elif ranking == "closeness_centrality":
        # Add closeness attributes to nodes and edges
        cc_values_nodes = nx.closeness_centrality(B, distance="distance")
        nx.set_node_attributes(B, cc_values_nodes, name="closeness_centrality")
        cc_values = node_to_edge_attributes(cc_values_nodes, B.edges)
        nx.set_edge_attributes(B, cc_values, name="closeness_centrality")
    progress_bar.update(1)

    # Export attributes to gdfs:
    # Create dataframe and add method as edge attribute
    edges_ranked = df_from_graph(B, ranking)

    # Rank edges by specified method
    edges_ranked = rank_df(edges_ranked, ranking)

    edges_ranked = gpd.GeoDataFrame(edges_ranked, crs=crs_projected, geometry="geometry")

    # Add existing bike network on top, https://stackoverflow.com/a/43408736
    if existing_network_spacing:
        existing_bikenet = gpd.GeoDataFrame({c: None for c in edges_ranked.columns}, index=[-1], crs=crs_projected)
        existing_bikenet.loc[-1, 'geometry'] = gpd.GeoSeries(edges_exnw.geometry).union_all()
        edges_ranked.loc[-1] = existing_bikenet.loc[-1]
        edges_ranked.index = edges_ranked.index+1
        edges_ranked.sort_index(inplace=True)
        edges_ranked.crs = crs_projected
    progress_bar.update(1)
    progress_bar.close()

    ### Remove edge overlaps
    if not allow_edge_overlaps:
        edges_ranked = remove_edge_overlaps(edges_ranked) # Can take a while, could be sped up.
        overlap_string = ""
    else:
        overlap_string = "_with-overlaps"

    # Add lengths and cumulative lengths, rounded to integer meters
    edges_ranked['length'] = edges_ranked.geometry.length
    edges_ranked['length_cumulative'] = edges_ranked.geometry.length.cumsum()
    edges_ranked = edges_ranked.astype({'length': int, 'length_cumulative': int})

    # Generate export data filename
    if export_data or export_plots or export_video:
        os.makedirs("./results/", exist_ok=True)
        if export_data_slug is None:
            city_string = city_name
        else:
            city_string = export_data_slug
        if existing_network_spacing:
            exnw_string = "_with-bikenw"
        else:
            exnw_string = ""
        export_data_filename = (
            slugify(city_string) + "-" + ranking + "-" + seed_point_type + overlap_string + exnw_string + "." + export_file_format
        )

    ### Export data
    if export_data:
        progress_bar = tqdm(
        desc="{:<23}".format("Exporting data"),
        total=1,
        unit="step",
        bar_format='{l_bar}{bar:16}{r_bar}',
        )
        seed_points_snapped_filtered.drop(["osmid"], axis=1, inplace=True)
        # We have meter precision, so rounding to integers is fine. Better would be to 
        # change dtypes to int, but this does not seem possible without manual looping.
        if city_boundary_exists:
            city_boundary_gdf.to_crs(epsg=crs_projected, inplace=True)
            city_boundary_gdf.geometry = city_boundary_gdf.geometry.set_precision(grid_size=1) 
        seed_points_snapped_filtered.geometry = seed_points_snapped_filtered.geometry.set_precision(grid_size=1)
        edges_ranked.geometry = edges_ranked.geometry.set_precision(grid_size=1)
        if export_file_format == "geojson":
            edges_ranked.to_file("./results/"+export_data_filename, driver="GeoJSON")
            seed_points_snapped_filtered.to_file("./results/"+slugify(city_string)+"-"+seed_point_type+exnw_string+".geojson", driver="GeoJSON")
            if city_boundary_exists: city_boundary_gdf.to_file("./results/"+slugify(city_string)+"-city_boundary.geojson", driver="GeoJSON")
        elif export_file_format == "gpkg":
            if existing_network_spacing:
                edges_ranked.iloc[[0]].to_file("./results/"+export_data_filename, driver="GPKG", layer="Existing bike network")
                edges_ranked.iloc[1:-1].to_file("./results/"+export_data_filename, driver="GPKG", layer="Grown bike network", append=True)
            else:
                edges_ranked.to_file("./results/"+export_data_filename, driver="GPKG", layer="Grown bike network")
            seed_points_snapped_filtered.to_file("./results/"+export_data_filename, driver="GPKG", layer="Seed points", append=True)
            if city_boundary_exists: city_boundary_gdf.to_file("./results/"+export_data_filename, driver="GPKG", layer="City boundary", append=True)
        progress_bar.update(1)
        progress_bar.close()

    if export_plots or export_video:
        ### Visualize

        # Read in file to plot
        routed_edges_gdf = gpd.read_file("./results/"+export_data_filename, layer="Grown bike network")

        # Viz/plot settings (move to config file later)
        # Define color palette (from Michael's project: https://github.com/mszell/bikenwgrowth/blob/main/parameters/parameters.py)
        streetcolor = "#999999"
        edgecolor = "#0EB6D2"
        seedcolor = "#ff7338"
        # Define linewidths
        lws = {"street": 0.75, "bike": 2}

        os.makedirs("./results/plots/ordering_"+ranking+"/", exist_ok=True)
        create_plots(
            routed_edges_gdf,
            seed_points_snapped_filtered,
            streetcolor,
            edgecolor,
            seedcolor,
            lws,
            ranking,
        )

        if export_video:
            os.makedirs("./results/plots/ordering_"+ranking+"/video/", exist_ok=True)
            make_video(img_folder_name="./results/plots/ordering_"+ranking+"/", fps=5)

    print("----------------------------------------------╯")
    if export_data:
        print("Data exported to results/")
    if export_plots:
        print("Plots exported to results/plots/")
    if export_video:
        print("Video exported to results/plots/")
    if export_data or export_plots or export_video:
        print("----------------------------------------------")

    endtime = time.time()
    print("FINISHED IN " + str(datetime.timedelta(seconds = round(endtime - starttime))))
    print("==============================================")

    return edges_ranked
