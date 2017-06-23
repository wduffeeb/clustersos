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
import subprocess

class Profile():


    def __init__(self, config, master):
        self.master = master
        self.config = config
        self.cluster_type = self.__class__.__name__
        self.node_list = None
        sos_options = {}
        sos_plugins = []
        mod_cmd_prefix = ''
        mod_sos_path = ''
        mod_release_string = ''
        self.sos_cmd_mod = ''
        self.sos_container_cmd = ''
        self.node_cmd = ''
        cleanup_cmd = ''

    def exec_node_cmd(self, cmd):
        '''Used to retrieve output from a (master) node in a cluster
        profile.'''
        if self.master:
            stdin, stdout, stderr = self.master.client.exec_command(cmd)
            sout = stdout.read().splitlines()
            return sout
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        rc = proc.returncode
        if proc.returncode == 0:
                return stdout


    def check_enabled(self):
        return False

    def get_nodes(self):
        pass

    def _get_nodes(self):
        try:
            return self.format_node_list()
        except Exception as e:
            print e
            return []

    def modify_sos_cmd(self):
        '''This is used to modify the sosreport command run on the nodes.
        By default, sosreport is run without any options, using this will
        allow the profile to specify what plugins to run or not and what
        options to use.

        This will NOT override user supplied options.
        '''

        if self.sos_plugins:
            for plug in self.sos_plugins:
                if plug not in self.config['sos_cmd']:
                    self.config['sos_cmd'] += '-e %s ' %plug 
        if self.sos_options:
            for opt in self.sos_options:
                if opt not in self.config['sos_cmd']:
                    self.config['sos_cmd'] += '-k %s=%s ' %(opt, self.sos_options[opt])

    def format_node_list(self):
        try:
            nodes = self.get_nodes()
            if isinstance(nodes, list):
                node_list = list(set(nodes))
            if isinstance(nodes, str):
                node_list = [n.split(',').strip() for n in nodes]
                node_list = list(set(nodes))
            return node_list
        except Exception as e:
            print e

    def extra_data_collection(self):
        '''This method is called against the master/local node at the end
        of collection. It is meant to be used to specify additional data
        that should be collected along with sosreports.

        Ideally, anything specified here should eventually make its way
        into sos ideally.

        If a cluster uses this command, it should return a file path or a
        list of file paths.
        '''
        return False
