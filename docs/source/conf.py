# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "GrowBikeNet"
copyright = "2026, GrowBikeNet contributors"
author = "GrowBikeNet contributors"

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
bibtex_default_style = 'plain'

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
            "name": "Mastodon",
            "url": "https://fosstodon.org/@bikenetkit",
            "html": """
                <svg stroke="currentColor" stroke-width="0" viewBox="0 0 14.9245 16">
                    <path fill="currentColor" fill-rule="evenodd" transform="scale(0.06896262)" d="M211.80734 139.0875c-3.18125 16.36625-28.4925 34.2775-57.5625 37.74875-15.15875 1.80875-30.08375 3.47125-45.99875 2.74125-26.0275-1.1925-46.565-6.2125-46.565-6.2125 0 2.53375.15625 4.94625.46875 7.2025 3.38375 25.68625 25.47 27.225 46.39125 27.9425 21.11625.7225 39.91875-5.20625 39.91875-5.20625l.8675 19.09s-14.77 7.93125-41.08125 9.39c-14.50875.7975-32.52375-.365-53.50625-5.91875C9.23234 213.82 1.40609 165.31125.20859 116.09125c-.365-14.61375-.14-28.39375-.14-39.91875 0-50.33 32.97625-65.0825 32.97625-65.0825C49.67234 3.45375 78.20359.2425 107.86484 0h.72875c29.66125.2425 58.21125 3.45375 74.8375 11.09 0 0 32.975 14.7525 32.975 65.0825 0 0 .41375 37.13375-4.59875 62.915"/>
                    <path fill="#fff" transform="scale(0.06896262)" d="M177.50984 80.077v60.94125h-24.14375v-59.15c0-12.46875-5.24625-18.7975-15.74-18.7975-11.6025 0-17.4175 7.5075-17.4175 22.3525v32.37625H96.20734V85.42325c0-14.845-5.81625-22.3525-17.41875-22.3525-10.49375 0-15.74 6.32875-15.74 18.7975v59.15H38.90484V80.077c0-12.455 3.17125-22.3525 9.54125-29.675 6.56875-7.3225 15.17125-11.07625 25.85-11.07625 12.355 0 21.71125 4.74875 27.8975 14.2475l6.01375 10.08125 6.015-10.08125c6.185-9.49875 15.54125-14.2475 27.8975-14.2475 10.6775 0 19.28 3.75375 25.85 11.07625 6.36875 7.3225 9.54 17.22 9.54 29.675"/>
                </svg>
            """,
            "class": "",
        },
        {
            "name": "Bluesky",
            "url": "https://bsky.app/profile/bikenetkit.bsky.social",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 18 16">
                    <path fill-rule="evenodd" transform="scale(0.03018)" d="m135.72 44.03c66.496 49.921 138.02 151.14 164.28 205.46 26.262-54.316 97.782-155.54 164.28-205.46 47.98-36.021 125.72-63.892 125.72 24.795 0 17.712-10.155 148.79-16.111 170.07-20.703 73.984-96.144 92.854-163.25 81.433 117.3 19.964 147.14 86.092 82.697 152.22-122.39 125.59-175.91-31.511-189.63-71.766-2.514-7.3797-3.6904-10.832-3.7077-7.8964-0.0174-2.9357-1.1937 0.51669-3.7077 7.8964-13.714 40.255-67.233 197.36-189.63 71.766-64.444-66.128-34.605-132.26 82.697-152.22-67.108 11.421-142.55-7.4491-163.25-81.433-5.9562-21.282-16.111-152.36-16.111-170.07 0-88.687 77.742-60.816 125.72-24.795z"></path>
                </svg>
            """,
            "class": "",
        },
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
