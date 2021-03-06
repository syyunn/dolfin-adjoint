# -*- coding: utf-8 -*-
#
# dolfin-adjoint documentation build configuration file, created by
# sphinx-quickstart on Wed Apr 25 12:52:09 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

from __future__ import print_function
import sys, os, datetime

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('exts'))

# -- General configuration -----------------------------------------------------

# No need to install 3rd party packages to generate the docs
class Mock(object):

    __all__ = []

    assign = None
    apply = None
    vector = None
    split = None
    interpolate = None
    copy = None
    __add__ = None
    __mul__ = None
    __neg__ = None
    get_gst = None
    SolverType_LU  = None

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return Mock()

    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'
        elif name[0] == name[0].upper():
            mockType = type(name, (Mock, ), {})
            mockType.__module__ = __name__
            return mockType
        else:
            return Mock()

MOCK_MODULES = ['libadjoint', 'libadjoint.exceptions', 'libadjoint.GSTHandle',
                'dolfin', 'ffc', 'backend.fem', 'backend.fem.projection', 'backend.PeriodicBC',
                'backend', 'ufl', 'numpy', 'scipy', 'scipy.optimize', 'ufl.classes',
                'ufl.algorithms', 'ufl.operators', 'Optizelle']
for mod_name in MOCK_MODULES:
    try:
        importlib.import_module(mod_name)
    except:
        print("Generating mock module %s." % mod_name)
        sys.modules[mod_name] = Mock()
import backend
backend.__name__ = "dolfin"

# Add path to dolfin_adjoint module
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('..'))

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.1'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
        'sphinx.ext.coverage', 'sphinx.ext.mathjax', 'sphinxcontrib.bibtex']
#imgmath_image_format = 'svg'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'dolfin-adjoint'
copyright = u'%d, The dolfin-adjoint team' % datetime.date.today().year

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '2017.2'
# The full version, including alpha/beta/rc tags.
release = '2017.2'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#html_theme = 'agogo'
#html_theme = 'basic'
#html_theme = 'default'
#html_theme = 'epub'
#html_theme = 'haiku'
#html_theme = 'nature'
#html_theme = 'scrolls'
#html_theme = 'sphinxdoc'
#html_theme = 'slim-agogo'
#html_theme = 'traditional'
html_theme = 'dolfin-adjoint'
#html_theme = 'classy'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ['_themes']

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = ""

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'dolfin-adjointdoc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letterpaper' or 'a4paper').
latex_elements = {'fontpkg': '\usepackage{mathpazo}',
                  'pointsize': '11pt',
                  'papersize': 'a4paper',
                  'fontenc': '',
                  'preamble': '\usepackage{amssymb} \usepackage{stmaryrd}'}

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('latex_index', 'dolfin-adjoint-all.tex', u'dolfin-adjoint manual',
   u'P. E. Farrell, S. W. Funke, D. A. Ham and M. E. Rognes', 'manual'),
#  ('documentation/index', 'dolfin-adjoint-documentation.tex', u'dolfin-adjoint Documentation',
#   u'The dolfin-adjoint team', 'manual'),
  ]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = "_static/logo.pdf"

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True

# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'dolfin-adjoint', u'dolfin-adjoint Documentation',
     [u'The dolfin-adjoint team'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'dolfin-adjoint', u'dolfin-adjoint Documentation',
   u'The dolfin-adjoint team', 'dolfin-adjoint', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'


# -- Options for Epub output ---------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = u'dolfin-adjoint'
epub_author = u'The dolfin-adjoint team'
epub_publisher = u'The dolfin-adjoint team'
epub_copyright = u'2012, The dolfin-adjoint team'

# The language of the text. It defaults to the language option
# or en if the language is not set.
#epub_language = ''

# The scheme of the identifier. Typical schemes are ISBN or URL.
#epub_scheme = ''

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#epub_identifier = ''

# A unique identification for the text.
#epub_uid = ''

# A tuple containing the cover image and cover page html template filenames.
#epub_cover = ()

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_post_files = []

# A list of files that should not be packed into the epub file.
#epub_exclude_files = []

# The depth of the table of contents in toc.ncx.
#epub_tocdepth = 3

# Allow duplicate toc entries.
#epub_tocdup = True


# Example configuration for intersphinx: refer to the Python standard library.
#intersphinx_mapping = {'python': ('http://docs.python.org/': None),
#                       'dolfin': ('http://fenicsproject.org/', None)}
intersphinx_mapping = {'dolfin': ('http://fenicsproject.org/', None)}

#pngmath_dvipng_args = ['-gamma 1.5', '-D 110', '-bg Transparent']
