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


class kubernetes(Profile):

    sos_plugins = ['kubernetes']
    sos_options = {'kubernetes.all': 'on'}
    cleanup_cmd = 'docker rm clustersos-tmp'

    option_list = [
                ('label', 'Restrict nodes to those with matching label')
                ]

    mod_release_string = 'Atomic'
    mod_cmd_prefix = ('atomic run --name=clustersos-tmp '
                      'registry.access.redhat.com/rhel7/rhel-tools ')
    mod_sos_path = '/host'

    def check_enabled(self):
        for k in self.config['packages']:
            if 'kubernetes' in k:
                return True
        return False

    def get_nodes(self):
        nodes = []
        cmd = 'kubectl get nodes'
        if self.get_option('label'):
            cmd += ' -l %s' % self.get_option('label')
        n = self.exec_node_cmd(cmd)
        nodes = [node.split()[0] for node in n]
        nodes.remove("NAME")
        return nodes
