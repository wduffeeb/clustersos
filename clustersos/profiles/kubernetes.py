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


class kubernetes(Profile):

    sos_plugins = ['kubernetes']
    sos_options = {'kubernetes.all': 'on'}
    packages = ('kubernetes-master', 'atomic-openshift-master')

    option_list = [
                ('label', 'Restrict nodes to those with matching label')
                ]

    def get_nodes(self):
        if self.is_installed('atomic-openshift-master'):
            self.cmd = 'oc '
        else:
            self.cmd = 'kubectl '
        self.cmd += 'get nodes '
        if self.get_option('label'):
            self.cmd += '-l %s ' % self.get_option('label')
        n = self.exec_master_cmd(self.cmd)
        nodes = [node.split()[0] for node in n]
        nodes.remove("NAME")
        return nodes

    def set_sos_prefix(self, facts):
        if 'Atomic' in facts['release']:
            cmd = 'atomic run --name=clustersos-tmp '
            img = self.config['image']
            return cmd + img

    def set_sos_path_strip(self, facts):
        if 'Atomic' in facts['release']:
            return '/host'

    def set_cleanup_cmd(self, facts):
        if 'Atomic' in facts['release']:
            return 'docker rm clustersos-tmp'
