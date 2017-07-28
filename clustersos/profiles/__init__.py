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
import subprocess


class Profile():

    def __init__(self, config, master):
        self.master = master
        self.config = config
        self.cluster_type = self.__class__.__name__
        self.node_list = None
        sos_plugins = []
        if not getattr(self, 'packages', False):
            self.packages = ('',)
        if not getattr(self, 'sos_options', False):
            self.sos_options = {}
        if not getattr(self, "option_list", False):
            self.option_list = []
        self.options = []
        self._get_options()

    def _get_options(self):
        for opt in self.config['cluster_options']:
            if self.cluster_type in opt:
                self.options.append((opt.split('.')[1],
                                     self.config['cluster_options'][opt]
                                     )
                                    )

    def get_option(self, option):
        '''This is used to by profiles to check if a cluster option was
        supplied to clustersos.'''
        for opt in self.options:
            if option == opt[0]:
                return opt[1]
        return False

    def is_installed(self, pkg):
        return pkg in self.config['packages']

    def exec_master_cmd(self, cmd):
        '''Used to retrieve output from a (master) node in a cluster
        profile.'''
        if self.master:
            stdin, stdout, stderr = self.master.client.exec_command(cmd)
            rc = stdout.channel.recv_exit_status()
            sout = stdout.read().splitlines()
            if rc == 0:
                return ([s.decode('utf-8') for s in sout] or True)
            else:
                return False
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                                )
        stdout, stderr = proc.communicate()
        rc = proc.returncode
        if proc.returncode == 0:
            return str(stdout, 'utf-8')
        return False

    def get_sos_prefix(self, facts):
        '''This wraps set_sos_prefix used by cluster profiles.
        It is called by sosnode.finalize_sos_cmd() for each node'''
        try:
            return self.set_sos_prefix(facts)
        except:
            return ''

    def set_sos_prefix(self, facts):
        '''This should be overridden by cluster profiles when needed.

        In a profile this should return a string that is placed immediately
        before the 'sosreport' command, but will be after sudo if needed
        '''
        return ''

    def get_sos_path_strip(self, facts):
        '''This calls set_sos_path_strip that is used by cluster profiles
        to determine if we need to remove a particular string from a
        returned sos path for any reason'''
        try:
            return self.set_sos_path_strip(facts)
        except:
            return ''

    def set_sos_path_strip(self, facts):
        '''This should be overriden by a cluster profile and used to set
        a string to be stripped from the return sos path if needed.

        For example, on Atomic Host, the sosreport gets written under
        /host/var/tmp in the container, but is available to scp under the
        standard /var/tmp after the container exits.'''
        return ''

    def get_cleanup_cmd(self, facts):
        '''This calls set_cleanup_cmd that is used by cluser profiles to
        determine if clustersos needs to do additional cleanup on a node'''
        try:
            return self.set_cleanup_cmd(facts)
        except:
            return False

    def set_cleanup_cmd(self, facts):
        '''This should be overridden by a cluster profile and used to set
        an additional command to run during cleanup.

        The profile should return a string containing the full cleanup
        command to run'''
        return ''

    def check_enabled(self):
        '''This may be overridden by cluster profiles

        This is called by clustersos on each profile that exists, and is
        meant to return True when the cluster profile matches a criteria
        that indicates that cluster type is in use.

        Only the first cluster type to determine a match is run'''
        for pkg in self.packages:
            if pkg in self.config['packages']:
                return True
        return False

    def get_nodes(self):
        pass

    def _get_nodes(self):
        try:
            return self.format_node_list()
        except Exception as e:
            print('Failed to get node list: %s' % e)
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
                    self.config['sos_cmd'] += '-e %s ' % plug
        if self.sos_options:
            for opt in self.sos_options:
                if opt not in self.config['sos_cmd']:
                    cmd = '-k %s=%s ' % (opt, self.sos_options[opt])
                    self.config['sos_cmd'] += cmd

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
            print('Failed to format node list: %s' % e)

    def run_extra_cmd(self):
        '''This method is called against the master/local node at the end
        of collection. It is meant to be used to specify additional data
        that should be collected along with sosreports.

        Ideally, anything specified here should eventually make its way
        into sos.

        If a cluster uses this command, it should return a file path or a
        list of file paths.
        '''
        return False
