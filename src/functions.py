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