#!/usr/bin/env python
import re

from distutils.core import setup
from distutils.command.install_data import install_data


class InstallData(install_data):

    # Workaround https://bugs.python.org/issue644744
    # Shamelessly borrowed from sosreport's setup.py
    def copy_file(self, filename, dirname):
        (out, _) = install_data.copy_file(self, filename, dirname)
        # match for man pages
        if re.search(r'/man/man\d/.+\.\d$', out):
            return (out+".gz", _)
        return (out, _)

setup(
    name='clustersos',
    version='1.1',
    description='Capture sosreports from multiple nodes simultaneously',
    long_description=("Clustersos is a utility designed to capture "
                      "sosreports from multiple nodes at once and "
                      "collect them into a single archive. If the nodes"
                      " are part of a cluster, profiles can be used to "
                      "configure how the sosreport command is run on "
                      "the nodes."),
    author='Jake Hunsaker',
    author_email='jhunsake@redhat.com',
    maintainer='Jake Hunsaker',
    maintainer_email='jhunsake@redhat.com',
    license='GPLv2',
    url='https://github.com/TurboTurtle/clustersos',
    packages=['clustersosreport', 'clustersosreport/profiles'],
    scripts=['clustersos'],
    cmdclass={'install_data': InstallData},
    data_files=[
                ('share/man/man1', ['man/en/clustersos.1'])
                ]
    )
