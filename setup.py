from distutils.core import setup

setup(name = 'sdmtoolkit-widgets',
      version = '0.1.1',
      description = 'Orange4WS Widgets for Semantic Data Mining',
      author = 'Anze Vavpetic',
      author_email = 'anze.vavpetic@ijs.si',
      url = 'http://sourceforge.net/p/sdmtoolkit/wiki/Home/',
      download_url = 'https://sourceforge.net/p/sdmtoolkit/wiki/Home/',
      license = "GNU General Public License (GPL) v3",
      keywords = ["data mining", "semantic data mining", "subgroup discovery", "aleph", "inductive logic programming", "relational data mining", "ontologies"],
      classifiers = ["Development Status :: 3 - Alpha",
                     "Programming Language :: Python",
                     "License :: OSI Approved :: GNU General Public License (GPL)",
                     "Operating System :: POSIX",
                     "Operating System :: Microsoft :: Windows",
                     "Intended Audience :: Science/Research"
                     ],
      platforms = ['linux', 'windows', 'mac'],
      packages = ['orange',
                  'orange.OrangeWidgets',
                  'orange.OrangeWidgets.SDM'],
      long_description = '''\
This project aims to be a easy-to-use toolkit of algorithms and utilities for
semantic data mining. So far all algorithms are implemented as web services and
we provide widgets for their use in the Orange4WS data mining platform.

Authors and contributors:
The toolkit was developed at Jozef Stefan Institute, Ljubljana, Slovenia.

Orange was developed at Faculty of Computer Science, Bioinformatics Laboratory,
Ljubljana, Slovenia.
''',
      )
