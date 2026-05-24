===============
Getting started
===============

Get Started in 4 Steps
----------------------

1. Install GrowBikeNet by following the :doc:`installation` guide.

2. Read the :ref:`introducing-growbikenet` section below.

3. Run the :doc:`mwe`.

4. Consult the :doc:`./reference_user` for complete details on using the package.

Finally, if you're not already familiar with `NetworkX`_ and `GeoPandas`_, make sure you read their user guides as GrowBikeNet uses their data structures.

.. _introducing-growbikenet:

Introducing GrowBikeNet
-----------------------

GrowBikeNet is built on top of `OSMnx`_/`NetworkX`_ and `GeoPandas`_. It takes one mandatory parameter, the city name, which it passes via `Nominatim`_ to `OSMnx`_, to download a city's street network. GrowBikeNet then runs the following operations:

* Optional, also download the city's existing bicycle network.
* Create seed points following :cite:t:`szell2022gub`. By default this is a grid, but it can also be set to the city's rail stations. If the city's existing bicycle network is used, the seed points are first selected on the bicycle network following :cite:t:`folco2023dmn`.
* The seed points are triangulated, by default via Delaunay triangulation (different to the original minimum weight triangulation of :cite:t:`szell2022gub`, but results are in practice identical). The triangulation is calculated for the abstract network with seed point nodes for which egde lengths are taken from the routed network.
* The triangulated edges are routed on the street network.
* A metric is computed for all edges. By default this is betweenness centrality. 
* The edges are ranked by this metric, denoting the importance and order of links to build.
* By default, overlaps between successive edges are removed, including overlaps with the existing bicycle network, if it was used. This operation ensures that added length of new edges, and cumulative lengths, are correct.
* Data is exported to a resuts folder, by default to geojson files. Exported files are the city boundary, the seed points, and the grown edges (and the existing bicycle network, if used).
* Optional, plots are generated in the results folder for each edge.
* Optional, a video is generated in the results folder, using the plots as frames.


To try it out, run the:

.. toctree::
   :maxdepth: 1

   Minimum working example <mwe>


.. _GeoPandas: https://geopandas.org
.. _NetworkX: https://networkx.org
.. _OSMnx: https://osmnx.readthedocs.io
.. _Nominatim: https://nominatim.openstreetmap.org