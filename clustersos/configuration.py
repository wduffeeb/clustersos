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
import socket


class Configuration(dict):
    """ Dict subclass that is used to handle configuration information
    needed by both ClusterSos and the SosNode classes """

    def __init__(self, args=None):
        self.args = args
        self.set_defaults()
        self.parse_config()
        self.parse_options()

    def set_defaults(self):
        self['sos_mod'] = {}
        self['master'] = ''
        self['strip_sos_path'] = ''
        self['ssh_port'] = '22'
        self['ssh_user'] = 'root'
        self['sos_cmd'] = '/usr/sbin/sosreport --batch '
        self['no_local'] = False
        self['tmp_dir'] = ''
        self['out_dir'] = '/var/tmp/'
        self['nodes'] = None
        self['debug'] = False
        self['tmp_dir_created'] = False
        self['cluster_type'] = None
        self['packages'] = ''
        self['profile'] = None
        self['name'] = None
        self['case_id'] = None
        self['timeout'] = 180
        self['all_logs'] = False
        self['alloptions'] = False
        self['no_pkg_check'] = False
        self['hostname'] = socket.gethostname()
        ips = [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]
        self['ip_addrs'] = list(set(ips))
        self['cluster_options'] = ''
        self['image'] = 'rhel7/rhel-tools '
        self['skip_plugins'] = []
        self['enable_plugins'] = []
        self['plugin_option'] = []
        self['list_options'] = False

    def parse_config(self):
        for k in self.args:
            if self.args[k]:
                self[k] = self.args[k]

    def parse_options(self):
        if self['cluster_options']:
            if isinstance(self['cluster_options'], str):
                self['cluster_options'] = [o for o in
                                           self['cluster_options'].split(',')
                                           ]
            opts = {}
            for opt in self['cluster_options']:
                try:
                    k, v = opt.split('=', 1)
                    opts[k] = v
                except:
                    opts[opt] = True
            self['cluster_options'] = opts
        for opt in ['skip_plugins', 'enable_plugins', 'plugin_option']:
            if self[opt]:
                self[opt] = [o for o in self[opt].split(',')]
