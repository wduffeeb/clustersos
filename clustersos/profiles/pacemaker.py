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


class pacemaker(Profile):

    sos_plugins = ['pacemaker']
    packages = ('pacemaker',)

    def get_nodes(self):
        cmd = 'pcs status'
        n = self.exec_master_cmd(cmd)
        node_list = self.parse_pcs_output(n)
        return node_list

    def parse_pcs_output(self, pcs):
        nodes = []
        warn = ('WARNING: corosync and pacemaker node names do not match '
                '(IPs used in setup?)'
                )
        if warn in pcs:
            print('NOTE: pacemaker is reporting a node name mismatch. '
                  'Attempts to connect to some of these nodes may fail\n'
                  )
        for s in ["Online", "Offline"]:
            for i in pcs:
                if i.startswith(s):
                    nlist = i.split('[')[1].split(']')[0]
                    node = [n for n in nlist.split(' ') if n]
                    nodes += node
        return nodes
