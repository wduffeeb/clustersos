# clustersos
Collect sosreports from multiple (cluster) nodes simultaneously

# Description
clustersos is a utility designed to collect sosreports from multiple nodes simultaneously and package them in a single archive. It is ideally suited for clustered environments, but can also be used for manually-defined sets of standalone nodes.

# Usage
clustersos leverages paramiko to open SSH sessions to the target nodes from the local system it is run on. At the moment, SSH key authentication is *required*.

**IMPORTANT**: clustersos itself does not need root privileges, however it does need root privileges on the target nodes. By default, SSH session will be opened as root. This can be changed via the `--ssh-user` option. If used, clustersos will prompt for a `sudo` password.

If clustersos is being run on a node that is part of the cluster being investigated, it can be run as simply as:

`$ clustersos`

If it is being run on a workstation, then it can still be used provided that SSH keys for that workstation are installed on the target nodes. To do this, specify a "master" node in the cluster:

`$ clustersos --master=master.example.com`

In this example, `master.example.com` will need to be able to enumerate all other nodes in the cluster. SSH sessions will be opened from the local workstation, NOT from the master node.

# Cluster types/support
clustersos will attempt to identify the type of cluster environment it is being run against through the use of cluster profiles. These are effectively plugins and live under `cluster_sos/profiles`. The most basic type of check is a package check, e.g. if it is a kubernetes cluster then clustersos would at minimum look for the presence of the kubernetes package.

You can also manually force a specific type of cluster using `--cluster-type`, E.G.

`$ clustersos --master=master.example.com --cluster-type=kubernetes`

# Installation

You can run clustersos from the git checkout, E.G.

`$ ./clustersos`

To make an rpm, just run

`# make rpm`
