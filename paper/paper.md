---
title: 'GrowBikeNet: A Python package to grow urban bicycle networks'
tags:
  - Python
  - cycling
  - urban planning
  - geospatial analysis
  - network analysis
  - urban mobility
  - urban data
  - data science
authors:
  - given-names: Michael
    surname: Szell
    orcid: 0000-0003-3022-2483
    corresponding: true
    affiliation: "1, 2"
  - given-names: Manuel
    surname: Knepper
    affiliation: 1
  - given-names: Anastassia
    surname: Vybornova
    orcid: 0000-0001-6915-2561
    affiliation: 1
  - given-names: Mariana
    surname: Pessoa
    affiliation: 1

affiliations:
  - name: Networks, Data, and Society (NERDS), Data Science Section, IT University of Copenhagen, 2300 Copenhagen, Denmark
    index: 1
  - name: Complexity Science Hub Vienna, 1080 Vienna, Austria
    index: 2
date: 24 September 2026
bibliography: paper.bib
---

# Summary

GrowBikeNet is a Python package that grows an urban bicycle network from scratch or from an existing bicycle network, as a decision support tool for urban planners or to create a compelling vision for urban cycling. A bicycle network is a connected set of protected bicycle infrastructure elements that span a large part of a city, providing safe and direct travel for cyclists. The software downloads and pre-processes street and bicycle network data and points of interests from OpenStreetMap via OSMnx or from custom local data, prepares seed points to which the network should connect, grows a network and routes it on the streets, orders the edges, exports results and plots. The software is available at \url{https://github.com/BikeNetKit/GrowBikeNet}, functionality is interactively explorable at \url{https://bikenetkit.org/growbikenet}.

# Statement of need

Networks of well-connected, protected bicycle tracks are recognized as fundamental urban infrastructure that spurs cycling. More cycling and less cars makes cities more livable and sustainable, providing massive public health and environmental benefits [@brandClimateChangeMitigation2021;@reynolds_impact_2009;@gosslingSocialCostAutomobility2019a;@minerCarHarmGlobal2024]. However, the planning and implementation of a bicycle network is a tedious political and technical process, requiring extensive stakeholder involvement and careful consideration of various factors [@degrootDesignManualBicycle2016a]. New computational tools and data sets, such as the OSMnx Python library [@boeingOSMnxNewMethods2017] and OpenStreetMap [@haklay_openstreetmap_2008], respectively, provide the opportunity to boost this process by allowing to easily process and visualize urban street networks computationally, and to run simulations of growing subnetworks on top of them. These opportunities have led to several recent computational studies on bicycle networks [@szell_growing_2022;@vybornova_automated_2023;@olmos_data_2020]. Yet, despite ample individual efforts and a beginning consolidation of the field [@diogopintoFrameworksPrioritizingCycling2026], none of these research projects have led to an open-source, general-use software package for simulated bicycle network growth and planning, visualization, and analysis. GrowBikeNet fills this gap.

The software provides benefits for at least two use cases. First, in urban planning, it provides urban planners and cycling advocates with a quick way to generate city-spanning bicycle network blueprints for their cities and general statistics relevant to the planning process. As GrowBikeNet allows local data imports and has ample settings to configure, it can simulate various scenarios adapted to local contexts. These blueprints can serve as a vision for potential future city development or they can be further refined. After exporting the generated networks to a geographic information system (GIS), detailed modifications could be made, for example with open tools like QGIS [@graser_qgis_2025] or A/B Streets which also allows traffic simulations [@abstreet]. This quick feedback reduces the time and resources required to manually plan bicycle networks which in turn can accelerate sustainable urban development. Second, GrowBikeNet enables researchers to conduct large-scale studies across multiple cities or regions, providing valuable insights into the potential impacts of bicycle networks at a broader scale. In both cases, GrowBikeNet can help to identify best practices, algorithmic approaches, and strategies for bicycle network implementation.

# State of the field 

The field of computational bicycle network design is still small, but has grown in the last few years with several new papers per year, and some dozen papers in total, warranting a literature review [@diogopintoFrameworksPrioritizingCycling2026]. Summarizing @diogopintoFrameworksPrioritizingCycling2026, the field can be categorized in different ways. On one hand is the methodological distinction between graph-based and GIS-based approaches. On the other hand are the different field-specific approaches ranging from network science to transport planning, which often correspond to the first categorization, but not always. GrowBikeNet falls into the graph-based, network science approach, but it aims to bridge the gap from originally exclusive network-structural considerations [@szell_growing_2022] to real applicability for city planning.

When it comes to the openness of data and algorithms, unfortunately many existing projects are closed source and thus not reproducible nor extendable by the community. Notable exceptions are, for example, @lovelacePropensityCycleTool2017a, or our own efforts like @lonardi_cohesive_2025, @vybornovaBikeNodePlannerDatadrivenDecision2025, or @sebastiao_trade-off_2026. Another problem is the one-off nature of raw, unmaintained research algorithms which makes their further development difficult even when they are open-source, including the original predecessor algorithm to GrowBikeNet [@szell_growing_2022]. To this suboptimal state of the field GrowBikeNet aspires to be a counterpoint: Packaged via pypi and conda, and using the AGPL license which forces openness and reproducibility.

![Example results of GrowBikeNet. Left: Growing a full bicycle network (green) for Athens, Greece, with default settings, incorporating existing bicycle infrastructure (purple). Seed points (black) are snapped to both substantial elements of the existing bicycle network and to a grid. The interactive version of this map is available at \url{https://bikenetkit.org/growbikenet/athens_gr}. Right: The first 40km of a growing bicycle network (green) for Turin, Italy, reprioritized by traffic crash data (red) to first develop through crash hotspots. The existing bicycle network is ignored and seed points are not shown for illustration purposes, the street network is shown in grey. Map data from OpenStreetMap. Top: BikeNetKit logo with GrowBikeNet wordmark.\label{fig:results}](fig1.png)

# Software design

## Operationalizing bicycle network planning concepts

The concept of a bicycle network has no agreed upon definition [@schonScopingReviewCycling2024]. GrowBikeNet defines it as the set of infrastructure elements (implemented by physical and/or legal means) which allows people of all ages and demographics to safely cycle - both subjectively and objectively. This definition is broad and somewhat vague on purpose, as the microscopic implementation details (raised curbs, bollards, bicycle streets, etc.) should be up to the local context and informed by local domain knowledge. Thus, GrowBikeNet concerns itself first and foremost with the topological foundation of a bicycle network, which is its network structure.

GrowBikeNet's bicycle network design philosophy was developed by  @szell_growing_2022 and is based on the idea of linking seed points, inspired by the Dutch CROW Design manual for bicycle traffic [@degrootDesignManualBicycle2016a]. These are points in a city that shall be connected by protected bicycle infrastructure, yielding edges in a bicycle network, see Fig. \ref{fig:results} (left) for an example. The choice and placement of seed points is crucial. To build a well-covering bicycle network, seed points should cover most of the city. By default, in GrowBikeNet seed points are arbitrary, city-spanning points on a grid, snapped to the street network, but GrowBikeNet also allows to assign actual preset points of interests such as railway stations or schools, or arbitrary OpenStreetMap tags or custom points of interest, going beyond @szell_growing_2022. Another important extension to @szell_growing_2022 is the option to not start growing from scratch but to account for the existing bicycle network following @folco_data-driven_2023, by placing seed points on the existing bicycle network first.

Once seed points are set and snapped to the street network, they need to be linked. By default, GrowBikeNet triangulates or quadrangulates the seed points automatically depending on street network structure [@boeingUrbanSpatialOrder2019], which is another extension of @szell_growing_2022, building a triangle or square-shaped link structure between the seed points. Once the linking process is finished, an abstract, unrouted network between the seed points is established. GrowBikeNet then builds a bicycle network on this network’s edges, routed on the street network. All network handling is done by NetworkX [@hagbergExploringNetworkStructure2008].

After routing, GrowBikeNet orders the edges in this potential bicycle network. The ordering is important, as it informs a city which edges to implement first to arrive at a functional network early. The default ordering is via betweenness centrality which is a network centrality measure approximating flow. By ordering edges like this, the first built edge is the one with highest expected flow of cyclists. The current package version provides the additional ordering options by closeness centrality or randomly. As was shown by @szell_growing_2022, ordering by betweenness centrality is superior to random ordering, and usually also more adequate than ordering by closeness centrality. 

Finally, edges are rerouted with weights to account for edges proposed in earlier steps, and edge overlaps between different steps are removed. These two postprocessing steps get rid of many artefacts observed from the raw algorithm of @szell_growing_2022 and lead to a more realistic network structure.

## Custom data for re-prioritizing growth and city definition

Additionally to its default mode of operation, GrowBikeNet implements the weighted ordering of @folco_data-driven_2023, which enables to re-prioritize the growth order of edges through an imported point and/or trip data set, making the simulation more data-driven and realistic. Example data sets include traffic crashes or empirical mobility flows, demonstrated for the city of Turin, Italy in Fig. \ref{fig:results} (right).

While GrowBikeNet builds heavily on OpenStreetMap and uses OpenStreetMap data in its default mode of operation, its data loading options allow operating with any data source as long as it follows the same data structure as OpenStreetMap data. This flexibility allows to define a street or existing bicycle network with network data other than from OpenStreetMap, or to limit or extend the specific street types on which the bicycle network is allowed to grow.

## Software implementation

GrowBikeNet's software design is based on three core principles: (1) to provide a user-friendly experience of executing one function with ample progress feedback and usage documentation [@gbnusagedocs], (2) to use community tools and standards, e.g., GeoPandas/shapely [@fleischmann_geopandas_2026] for handling spatial aspects, OSMnx/NetworkX for handling networks [@boeingOSMnxNewMethods2017;@hagbergExploringNetworkStructure2008], and (3) high customizability by making most design decisions configurable via settings and constants and by supporting custom data imports (seed points, street and bicycle networks, city boundary, trip or point data). Data can be imported and exported in common geospatial formats such as shape files (`.shp`), GeoJSON (`.geojson`), or GeoPackage (`.gpkg`).

Performance of network algorithms, for example NetworkX's Python implementation of shortest paths, is generally not an issue, as the number of shortest paths to calculate is limited. One performance bottleneck is data download via OSMnx and its underlying Overpass API for the initial data download. This bottleneck is mitigated by OSMnx using JSON caching for subsequent data uses and by GrowBikeNet's option to import local data sets. The step of removing overlapping edges at the end of GrowBikeNet's procedure is computationally complex, therefore it utilizes shapely's highly optimized GEOS library written in C++. For a medium-sized city and an off-the-shelf laptop, one GrowBikeNet run takes below one minute, for large cities not more than a few minutes.


## Embedding in BikeNetKit

GrowBikeNet is part of the BikeNetKit family of bicycle network toolkits and utilities. GrowBikeNet's typical use case is underdeveloped cities (in terms of bicycle network development), making it well usable for most cities on the planet. Other BikeNetKit tools, like superblockify [@buth_superblockify_2024], have complementary use cases. Shared functions between different BikeNetKit tools are planned to be consolidated and imported from the utility package BikeNetLib in the future.

## Visualization
GrowBikeNet allows to plot each step in the simulated network growth using matplotlib. GrowBikeNet also provides a script to use all plots as frames for generating a video via openCV. Visual aspects like colors, line widths, etc., are configurable. Example results are shown in Fig. \ref{fig:results}. Precomputed results of GrowBikeNet for over 400 European cities can be interactively explored at \url{https://bikenetkit.org/growbikenet}.

## License and philosophy

The AGPL license serves two purposes. First, it ensures the essential scientific standard of reproducibility of GrowBikeNet and of all its derived versions. Second, it positions GrowBikeNet as a public good rather than a proprietary consultancy tool for extracting city budgets. GrowBikeNet provides free, open-source software in a community effort that can be extended at will, and which cities and proactive citizens can use directly to explore and revisit different scenarios dynamically and in a data-driven way.

# Research impact statement

The software's underlying method has already been applied in several research projects. Its original version was developed by @szell_growing_2022 who studied 62 cities to identify optimal growth strategies for urban bicycle networks. Follow-up projects include, for example, @folco_data-driven_2023 who extended the approach to point and trip data, @basilone_road-width-aware_2025 who applied the approach to road widths, @sebastiao_trade-off_2026 who followed up on a systematic investigation of link ordering, ongoing research by @larkin_implementing_2026 who incorporate low-traffic neighborhoods, or Master theses like @pessoathesis. With increased focus on reducing car-dependence and the negative impacts of urbanization on climate change [@brandClimateChangeMitigation2021;@satterthwaite2009;@mattioli_political_2020], the need for sustainable urban planning tools like GrowBikeNet will only increase.

# AI usage disclosure

No generative AI tools were used in the development of this software, the writing of this manuscript, or the preparation of supporting materials.

# Acknowledgements

The authors gratefully acknowledge the open source data that this software makes use of: Map data copyrighted by OpenStreetMap contributors and available from \url{https://www.openstreetmap.org}. Further, we acknowledge funding from the Innovation Fund Denmark, the EU Horizon Project JUST STREETS (Grant agreement ID: 101104240), and from the Data Science section of IT University of Copenhagen.


# References