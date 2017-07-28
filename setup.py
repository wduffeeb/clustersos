from setuptools import setup, find_packages

setup(
    name='clustersos',
    version='1.1.1',
    description='Capture sosreports from multiple nodes simultaneously',
    long_description=("Clustersos is a utility designed to capture "
                      "sosreports from multiple nodes at once and "
                      "collect them into a single archive. If the nodes"
                      " are part of a cluster, profiles can be used to "
                      "configure how the sosreport command is run on "
                      "the nodes."),
    author='Jake Hunsaker',
    author_email='jhunsake@redhat.com',
    license='GPLv2',
    url='https://github.com/TurboTurtle/clustersos',
    classifiers=[
                'Intended Audience :: System Administrators',
                'Topic :: System :: Systems Administration',
                ('License :: OSI Approved :: GNU General Public License v2 '
                 "(GPLv2)"),
                'Programming Language :: Python :: 2',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.2',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5'
                ],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, <4',
    packages=find_packages(),
    scripts=['clustersosreport'],
    data_files=[
                ('share/man/man1/', ['man/en/clustersosreport.1'])
                ] 
    )
