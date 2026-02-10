import numpy as np
import geopandas as gpd
from shapely.prepared import prep
from shapely.geometry import Point

# helper function to check whether newly to be added edge intersects with already added edges
def intersects_properly(geom1, geom2):
    '''
    for 2 shapely geometries, check whether they "properly intersect" (i.e. intersect but not touch, i.e. don't share endpoints)
    '''
    return geom1.intersects(geom2) and not geom1.touches(geom2)

def get_correct_edgetuples(edge_gdf, nodelist):
    '''
    helper function that maps a node list (output of nx.shortest_paths)
    to the correct set of edge tuples that can be used for INDEXING THE EDGE GDF
    '''
    edgelist_prelim = zip(nodelist, nodelist[1:])
    edgelist_final = []
    for edge_prelim in edgelist_prelim:
        if edge_prelim in edge_gdf.index:
            edgelist_final.append(edge_prelim)
        else:
            edgelist_final.append(tuple([edge_prelim[1], edge_prelim[0]]))
    return edgelist_final

# create seed points for greedy triangulation
def get_seed_points (edges, proj_crs, seed_point_spacing):
    # get convex hull around edge area
    hull = edges.union_all().convex_hull
    # get bounds of hull
    latmin, lonmin, latmax, lonmax = hull.bounds

    # https://stackoverflow.com/questions/66010964/fastest-way-to-produce-a-grid-of-points-that-fall-within-a-polygon-or-shape
    # populate hull bbox with evenly spaced seeding points
    points = []
    for lat in np.arange(latmin, latmax, seed_point_spacing):
        for lon in np.arange(lonmin, lonmax, seed_point_spacing):
            points.append(Point((round(lat, 4), round(lon, 4))))

    # keep only those seed points that are within the hull polygon
    prep_polygon = prep(hull)
    valid_points = []
    valid_points.extend(filter(prep_polygon.contains, points))

    # store seed points in gdf
    seed_points = gpd.GeoDataFrame(
        {"geometry": valid_points},
        crs=proj_crs
    )
    return seed_points