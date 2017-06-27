# Copyright Red Hat 2017, Jake Hunsaker <jhunsake@redhat.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from profile import Profile

class pacemaker(Profile):

    sos_plugins = {'pacemaker'}

    def check_enabled(self):
        if 'pacemaker' in self.config['packages']:
            return True
        return False

    def get_nodes(self):
        node_list = []
        cmd = 'pcs cluster status'
        n = self.exec_master_cmd(cmd)
        idx = n.index("PCSD Status:")+1
        node_list = [node.split()[0].strip(':') for node in n[idx:]]
        return node_list
