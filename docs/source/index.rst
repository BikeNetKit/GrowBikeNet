.. GrowBikeNet documentation master file, created by
   sphinx-quickstart on Thu Feb 12 15:01:19 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GrowBikeNet |version| documentation
===================================

The Python package ``growbikenet`` grows an urban bicycle network from scratch or from an existing bicycle network. You can download street and bike network data with a single line of code, simulate different bicycle network growth scenarios, and export and plot the resulting prioritized growth steps. It is hosted on `Github <https://github.com/BikeNetKit/GrowBikeNet>`__, part of `BikeNetKit <https://bikenetkit.org>`__.

|Example Paris|

GrowBikeNet is a decision support tool for urban planners based on the Dutch CROW Design manual for bicycle traffic. It is also useful for proactive citizens to create a compelling vision for urban cycling in their city, and it aims to foster research on bicycle networks. 

GrowBikeNet is fully customizable and data-driven allowing to explore different scenarios - for example, you can import and make use of your own custom data sets like points of interest or traffic flows, or limit network development to specific streets to adapt the software to your local needs.

When to use
-----------

GrowBikeNet works well for most cities on the planet. It can grow a bicycle network from scratch which makes most sense for cities that have only negligible bicycle infrastructure. It can also extend an existing bicycle network, which works best if it is not too developed already.

Recommended example cities to grow from scratch: Athens, Kyiv, Naples

Recommended example cities to extend the existing net: Berlin, Prague, Rome

For alternative approaches, or for cities with more developed bicycle networks, consider using `LinkBikeNet <https://github.com/BikeNetKit/LinkBikeNet>`__ or `FixBikeNet <https://github.com/BikeNetKit/FixBikeNet>`__.

Setup and use
-------------

To set up GrowBikeNet, see the :doc:`installation` page.
To use GrowBikeNet, the :doc:`getting_started` page
is a good place to start. Various usage examples are walked through on the :doc:`usage` page. For technical documentation, consult the :doc:`reference_user`.

.. Statement of need
.. =================

.. TBA

Source
------

The source code builds on `the code from the
research paper <https://github.com/mszell/bikenwgrowth>`__ *Growing
Urban Bicycle Networks* and on `the code from the research
paper <https://github.com/pietrofolco/Data-driven_bicycle_network_planning_for_demand_and_safety>`__
*Data-driven micromobility network planning for demand and safety*.

How to cite
-----------

If you use GrowBikeNet in your research, please cite `the paper <https://doi.org/10.1038/s41598-022-10783-y>`__:

    M. Szell, S. Mimar, T. Perlman, G. Ghoshal, R. Sinatra. Growing urban bicycle networks. Scientific Reports 12, 6765 (2022). https://doi.org/10.1038/s41598-022-10783-y

Contributing
------------

If you want to contribute to the development of GrowBikeNet, please read the
`CONTRIBUTING.md <https://github.com/BikeNetKit/GrowBikeNet?tab=contributing-ov-file#contributing-to-bikenetkit>`__
file.

Supported by
------------

Development of BikeNetKit/GrowBikeNet is supported by the Innovation Fund Denmark, the EU HORIZON grant JUST STREETS, and the Data Science Section of IT University of Copenhagen.

|Innovation Fund Denmark|    |European Union|   |JUST STREETS|

.. |Example Paris| image:: _static/growbikenet-paris.gif
   :target: https://bikenetkit.org/growbikenet
.. |Innovation Fund Denmark| image:: _static/logo_innovationfund.png
   :target: https://innovationsfonden.dk/en
.. |European Union| image:: _static/logo_eu.png
   :target: https://commission.europa.eu/index_en
.. |JUST STREETS| image:: _static/logo_juststreets.png
   :target: https://www.just-streets.eu/


Documentation contents
----------------------

.. toctree::
   :maxdepth: 1

   Home <self>
   installation
   getting_started
   usage
   reference_user
   reference_developer
   changelog
