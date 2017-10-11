# Copyright Red Hat 2017, Jake Hunsaker <jhunsake@redhat.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
from clustersos.profiles import Profile

class openshift(Profile):

    sos_plugins = ['kubernetes', 'origin']
    packages = ('atomic-openshift-utils',)

    option_list = [
                ('label', 'string',
                 'Restrict nodes to those with matching label')
                ]

    def get_nodes(self):
        self.cmd = 'oc get nodes'
        if self.get_option('label'):
            self.cmd += '-l %s ' % self.get_option('label')
        n = self.exec_master_cmd(self.cmd)
        nodes = [node.split()[0] for node in n]
        nodes.remove("NAME")
        return nodes
