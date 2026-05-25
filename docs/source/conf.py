# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "GrowBikeNet"
copyright = "2026, GrowBikeNet developers"
author = "Szell, Vybornova, Knepper"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os  # noqa
import sys  # noqa
from pathlib import Path  # noqa
from tomllib import load as toml_load  # noqa

sys.path.insert(0, os.path.abspath(".."))
import growbikenet  # noqa

# dynamically load version
with Path("../../pyproject.toml").open("rb") as f:
    pyproject = toml_load(f)
version = release = pyproject["project"]["version"]

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

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# path to bib file with references
bibtex_bibfiles = ["_static/references.bib"]
bibtex_reference_style = "author_year"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_static_path = ["_static"]

### select html theme
html_theme = "furo"

html_theme_options = {
    "pygment_light_style": "tango",
    "logo": {
        "image_light": "logo.png",
        "image_dark": "logo.png",
    },
    "light_css_variables": {
        "color-brand-primary": "#096a51",
        "color-brand-content": "#096a51",
        "color-brand-visited": "#5b8b75",
    },
    "dark_css_variables": {
        "color-brand-primary": "#3cd71d",
        "color-brand-content": "#3cd71d",
        "color-brand-visited": "#5b8b75",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/BikeNetKit/GrowBikeNet",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

# Generate the API documentation when building
autosummary_generate = True
autosummary_imported_members = True
numpydoc_show_class_members = False
class_members_toctree = False
numpydoc_show_inherited_class_members = False
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

        __ https://github.com/BikeNetKit/GrowBikeNet/blob/main/docs/source/{{ docname }}
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
        fn = os.path.relpath(fn, start=os.path.dirname(growbikenet.__file__))
        source, lineno = inspect.getsourcelines(obj)
        return fn, lineno, lineno + len(source) - 1

    if domain != "py" or not info["module"]:
        return None
    try:
        filename = "growbikenet/%s#L%d-L%d" % find_source()  # noqa: UP031
    except Exception:
        filename = info["module"].replace(".", "/") + ".py"
    tag = "main" if "+" in release else ("v" + release)
    return f"https://github.com/BikeNetKit/GrowBikeNet/blob/{tag}/{filename}"
