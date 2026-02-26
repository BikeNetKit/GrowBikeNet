# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GrowBikeNet'
copyright = '2026, Szell, Vybornova, Knepper'
author = 'Szell, Vybornova, Knepper'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
import GrowBikeNet  # noqa
# sys.path.insert(0, os.path.abspath("../"))

version = GrowBikeNet.__version__
release = version

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.linkcode",
    "sphinxcontrib.bibtex",
    "sphinx.ext.mathjax",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "nbsphinx",
    "matplotlib.sphinxext.plot_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_gallery.load_style",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# path to bib file with references
bibtex_bibfiles = ["_static/references.bib"]
bibtex_reference_style = "author_year"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_static_path = ['_static']

### select html theme
# html_theme = 'alabaster'
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/BikeNetKit/GrowBikeNet",
    "twitter_url": "notwitter.com",
    "pygment_light_style": "tango",
    "logo": {
        "image_light": "logo.png",
        "image_dark": "logo.png",
    },
}

# Generate the API documentation when building
autosummary_generate = True
autosummary_imported_members = True
numpydoc_show_class_members = True
class_members_toctree = True
numpydoc_show_inherited_class_members = True
numpydoc_class_members_toctree = False
numpydoc_use_plots = True
autodoc_typehints = "none"

# -- Extension configuration -------------------------------------------------
nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base=None) %}

.. only:: html

    .. role:: raw-html(raw)
        :format: html

    .. note::

        | This page was generated from `{{ docname }}`__.
        | Interactive online version: :raw-html:`<a href="https://mybinder.org/GrowBikeNet/master?urlpath=lab/tree/docs/{{ docname }}"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>`

        __ https://github.com/BikeNetKit/GrowBikeNet/blob/master/docs/{{ docname }}
"""  # noqa: E501

def linkcode_resolve(domain, info):
    def find_source():
        # try to find the file and line number, based on code from numpy:
        # https://github.com/numpy/numpy/blob/master/doc/source/conf.py#L286
        obj = sys.modules[info["module"]]
        for part in info["fullname"].split("."):
            obj = getattr(obj, part)
        import inspect
        import os

        fn = inspect.getsourcefile(obj)
        fn = os.path.relpath(fn, start=os.path.dirname(GrowBikeNet.__file__))
        source, lineno = inspect.getsourcelines(obj)
        return fn, lineno, lineno + len(source) - 1

    if domain != "py" or not info["module"]:
        return None
    try:
        filename = "GrowBikeNet/%s#L%d-L%d" % find_source()  # noqa: UP031
    except Exception:
        filename = info["module"].replace(".", "/") + ".py"
    tag = "main" if "+" in release else ("v" + release)
    return f"https://github.com/BikeNetKit/GrowBikeNet/blob/{tag}/{filename}"