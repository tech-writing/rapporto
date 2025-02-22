# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# ruff: noqa: ERA001

project = "Rapporto"
copyright = "2025, The Panodata Developers"  # noqa: A001
author = "The Panodata Developers"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.ifconfig",
    "sphinxcontrib.mermaid",
    "sphinxext.opengraph",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_title = "Rapporto"

# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/announcements.html
# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/layout.html#build-date
# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/header-links.html
# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/source-buttons.html
html_theme_options = {
    "announcement": """
    Rapporto is in its infancy, and needs your support. <br>
    We appreciate any kind of
    <a href="https://github.com/tech-writing/rapporto/issues">bug report</a> and
    <a href="https://github.com/tech-writing/rapporto/issues">feature request</a>,
    or suggestions to improve its
    <a href="https://github.com/tech-writing/rapporto/tree/main/docs">documentation</a>.
    """,
    "content_footer_items": ["last-updated"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/tech-writing/rapporto",
            # Icon class (if "type": "fontawesome"), or path to local image (if "type": "local")
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/rapporto",
            "icon": "fa-custom fa-pypi",
        },
    ],
    "icon_links_label": "Quick Links",
    "navbar_align": "left",
    "show_toc_level": 1,
    "use_edit_page_button": True,
}

# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/source-buttons.html#github
html_context = {
    "github_user": "tech-writing",
    "github_repo": "rapporto",
    "github_version": "main",
    "doc_path": "docs",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False
html_copy_source = False

# -- Intersphinx ----------------------------------------------------------

intersphinx_mapping = {
    # "influxio": ("https://influxio.readthedocs.io/", None),
}
linkcheck_ignore = []

# Disable caching remote inventories completely.
# http://www.sphinx-doc.org/en/stable/ext/intersphinx.html#confval-intersphinx_cache_limit
# intersphinx_cache_limit = 0

language = "en"

# -- Extension configuration -------------------------------------------------

sphinx_tabs_valid_builders = ["linkcheck"]
todo_include_todos = True

# Configure sphinx-copybutton
copybutton_remove_prompts = True
copybutton_line_continuation_character = "\\"
copybutton_prompt_text = (
    r">>> |\.\.\. |\$ |sh\$ |PS> |cr> |mysql> |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
)
copybutton_prompt_is_regexp = True

# Configure sphinxext-opengraph
ogp_site_url = "https://rapporto.readthedocs.io/"
ogp_enable_meta_description = True
# ogp_image = "http://example.org/image.png"
# ogp_description_length = 300


# -- Options for MyST -------------------------------------------------

myst_heading_anchors = 3
myst_enable_extensions = [
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "strikethrough",
    "substitution",
    "tasklist",
]
myst_substitutions = {}

# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#strikethrough
# https://myst-parser.readthedocs.io/en/latest/configuration.html#myst-warnings
suppress_warnings = [
    "myst.strikethrough",
]
