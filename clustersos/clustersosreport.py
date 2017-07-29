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
import fnmatch
import os
import random
import re
import string
import tarfile
import threading
import tempfile
import shutil
import subprocess
import sys

from datetime import datetime
from clustersos.sosnode import SosNode
from distutils.sysconfig import get_python_lib
from getpass import getpass
from six.moves import input


class ClusterSos():
    """ Main clustersos class """

    def __init__(self, config):
        self.config = config
        self.threads = []
        self.workers = []
        self.client_list = []
        self.master = False
        self.retrieved = 0
        if not self.config['list_options']:
            self.prep()
        else:
            self._load_profiles()

    def _exit(self, msg, error=1):
        '''Used to safely terminate if clustersos encounters an error'''
        print(msg)
        try:
            self.close_all_connections()
            self.cleanup()
        except:
            pass
        sys.exit(error)

    def create_tmp_dir(self):
        '''Creates a temp directory to transfer sosreports to'''
        tmpdir = tempfile.mkdtemp()
        self.config['tmp_dir'] = tmpdir
        self.config['tmp_dir_created'] = True

    def list_options(self):
        '''Display options for available profiles'''
        print('\nThe following profile options are available:\n')
        print('{:30} {:<10} {:<}'.format('Option Name', 'Type', 'Description'))

        for prof in self.profiles:
            if hasattr(self.profiles[prof], 'option_list'):
                for opt in self.profiles[prof].option_list:
                    option = '{}.{}'.format(prof, opt[0])
                    optln = '{:30} {:<10} {:<}'.format(option,
                                                       opt[1],
                                                       opt[2]
                                                       )
                    print(optln)
        print('\nOptions with no type listed are simple on/off switches'
              '\n E.G. using \'ovirt.no-database\' enables that option'
              )

    def delete_tmp_dir(self):
        '''Removes the temp directory and all collected sosreports'''
        shutil.rmtree(self.config['tmp_dir'])

    def _load_profiles(self):
        '''Load an instance of each profile so that clustersos can later
        determine what type of cluster is in use
        '''
        if 'clustersos' not in os.listdir(os.getcwd()):
            p = get_python_lib()
            path = p + '/clustersos/profiles/'
        else:
            path = 'clustersos/profiles'
        self.profiles = {}
        sys.path.insert(0, path)
        for f in sorted(os.listdir(path)):
            fname, ext = os.path.splitext(f)
            if ext == '.py' and fname not in ['__init__', 'profile']:
                mod = __import__(fname)
                class_ = getattr(mod, fname)
                self.profiles[fname] = class_(self.config, self.master)
        sys.path.pop(0)

    def _get_archive_name(self):
        '''Generates a name for the tarball archive'''
        nstr = 'clustersos'
        if self.config['name']:
            nstr += '-%s' % self.config['name']
        if self.config['case_id']:
            nstr += '-%s' % self.config['case_id']
        dt = datetime.strftime(datetime.now(), '%Y-%m-%d')

        try:
            string.lowercase = string.ascii_lowercase
        except NameError:
            pass

        rand = ''.join(random.choice(string.lowercase) for x in range(5))
        return '%s-%s-%s' % (nstr, dt, rand)

    def _get_archive_path(self):
        '''Returns the path, including filename, of the tarball we build
        that contains the collected sosreports
        '''
        name = self._get_archive_name()
        compr = 'gz'
        return self.config['out_dir'] + name + '.tar.' + compr

    def load_packages(self):
        '''Loads a listing of all installed packages on localhost.

        This is used by cluster profiles to try and determine what type
        of cluster we're dealing with.

        Only works for rpms currently
        '''
        rpm_cmd = 'rpm -qa --qf "%{NAME} "'
        if not self.master:
            rpms = subprocess.Popen(rpm_cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE
                                    )
            stdout, stderr = rpms.communicate()
        else:
            sin, sout, serr = self.master.client.exec_command(rpm_cmd,
                                                              timeout=30
                                                              )
            stdout = str(sout.readlines())
        if stdout:
            self.config['packages'] = [r for r in stdout.split()]

    def prep(self):
        '''Based on configuration, performs setup for collection'''
        print('This utility is designed to collect sosreports from '
              'multiple nodes simultaneously.\n'
              )
        print('Please note that clustersos REQUIRES key authentication '
              'for SSH to be in place for node sosreport collection\n'
              )
        if self.config['master']:
            self.connect_to_master()
            self.config['no_local'] = True
        self._load_profiles()
        if not self.config['no_pkg_check']:
            self.load_packages()
        if self.config['cluster_type']:
            self.config['profile'] = self.profiles[self.config['cluster_type']]
        else:
            self.determine_cluster()
        print('Cluster type has been set to %s' % self.config['cluster_type'])
        if not self.config['tmp_dir']:
            self.create_tmp_dir()
        self.get_nodes()
        self.intro()
        self.configure_sos_cmd()

    def intro(self):
        '''Prints initial messages and collects user and case if not
        provided already.
        '''
        print('\nThe following is a list of nodes to collect from:')
        if self.master:
            print('\t%-*s' % (self.config['hostlen'], self.config['master']))
        for node in self.node_list:
            print("\t%-*s" % (self.config['hostlen'], node))

        if not self.config['name']:
            msg = '\nPlease enter your first inital and last name: '
            self.config['name'] = input(msg)
        if not self.config['case_id']:
            msg = 'Please enter the case id you are collecting reports for: '
            self.config['case_id'] = input(msg)

    def configure_sos_cmd(self):
        '''Configures the sosreport command that is run on the nodes'''
        if self.config['name']:
            self.config['sos_cmd'] += '--name=%s ' % self.config['name']
        if self.config['case_id']:
            self.config['sos_cmd'] += '--case-id=%s ' % self.config['case_id']
        if self.config['alloptions']:
            self.config['sos_cmd'] += '--alloptions '
        if self.config['cluster_type']:
            self.config['profile'].modify_sos_cmd()
        for opt in ['skip_plugins', 'enable_plugins', 'plugin_option']:
            if opt in self.config and self.config[opt]:
                option = ','.join(o for o in self.config[opt])
                self.config['sos_cmd'] += '--%s=%s ' % (opt.replace('_', '-'),
                                                        option
                                                        )

    def connect_to_master(self):
        '''If run with --master, we will run profile checks again that
        instead of the localhost.
        '''
        self.master = SosNode(self.config['master'], self.config)

    def determine_cluster(self):
        '''This sets the cluster type and loads that cluster's profile.

        If no cluster type is matched and no list of nodes is provided by
        the user, then we abort.

        If a list of nodes is given, this is not run, however the profile
        can still be run if the user sets a --cluster-type manually
        '''

        for prof in self.profiles:
            if self.profiles[prof].check_enabled():
                self.config['profile'] = self.profiles[prof]
                name = str(self.profiles[prof].__class__.__name__).lower()
                self.config['cluster_type'] = name
                break
                msg = ('Could not determine cluster profile and no list of '
                       'nodes was provided.\nAborting...'
                       )
                self._exit(msg)

    def get_nodes_from_cluster(self):
        '''Collects the list of nodes from the determined cluster profile'''
        return self.config['profile']._get_nodes()

    def reduce_node_list(self):
        '''Reduce duplicate entries of the localhost and/or master node
        if applicable'''
        if (self.config['hostname'] in self.node_list and not
                self.config['no_local']):
            self.node_list.remove(self.config['hostname'])
        for i in self.config['ip_addrs']:
            if i in self.node_list:
                self.node_list.remove(i)
        # remove the master node from the list, since we already have
        # an open session to it.
        if self.config['master']:
            for n in self.node_list:
                if n == self.master.hostname or n == self.config['master']:
                    self.node_list.remove(n)

    def get_nodes(self):
        ''' Sets the list of nodes to collect sosreports from '''
        if not self.config['master'] and not self.config['profile']:
            msg = ('Could not determine a cluster profile and no list of '
                   'nodes or master node was provided.\nAborting...'
                   )
            self._exit(msg)
        if self.config['nodes']:
            self.node_list = [n for n in self.config['nodes'].split(',')]
        else:
            self.node_list = self.get_nodes_from_cluster()
        if not self.config['master']:
            self.node_list.append(self.config['hostname'])
        self.reduce_node_list()
        self.report_num = len(self.node_list)
        if self.master:
            self.report_num += 1
        self.config['hostlen'] = len(max(self.node_list, key=len))

    def can_run_local_sos(self):
        '''Check if sosreport can be run as the current user, or if we need
        to invoke sudo'''
        if os.geteuid() != 0:
            self.need_local_sudo = True
            msg = ('\nLocal sosreport requires root. Provide sudo password'
                   'or press ENTER to skip: ')
            self.local_sudopw = getpass(prompt=msg)
            print('\n')
            if not self.local_sudopw:
                return False
        return True

    def local_sosreport(self):
        '''If a local sosreport is needed, collect it without trying to
        SSH from localhost to localhost'''
        try:
            cmd = self.config['sos_cmd']
            cmd += ' --tmp-dir=%s' % self.config['tmp_dir']
            if self.need_local_sudo:
                cmd = 'echo %s | sudo -S %s' % (self.local_sudopw, cmd)
            print("%-*s: %s" % (self.config['hostlen'] + 1,
                                self.config['hostname'],
                                'Generating sosreport...'
                                )
                  )
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            rc = proc.returncode
            if rc == 0:
                self.retrieved += 1
                print("%-*s: %s" % (self.config['hostlen'] + 1,
                                    self.config['hostname'],
                                    'Retrieving sosreport...'
                                    )
                      )
                if self.need_local_sudo:
                    for line in stdout.split('\n'):
                        if fnmatch.fnmatch(line, '*sosreport-*tar*'):
                            self.local_sos_path = line.strip()
                    cmd = 'echo %s | sudo -S chown %s:%s %s' % (
                                            self.local_sudopw,
                                            os.geteuid(),
                                            os.geteuid(),
                                            self.local_sos_path
                                            )
                    proc = subprocess.Popen(cmd,
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE
                                            )
                    stdout, stderr = proc.communicate()
                    del(self.local_sudopw)
            else:
                print("%-*s: %s %s" % (self.config['hostlen'] + 1,
                                       self.config['hostname'],
                                       'Failed to collect sosreport'
                                       )
                      )
        except Exception as e:
            print("%-*s: %s %s" % (self.config['hostlen'] + 1,
                                   self.config['hostname'],
                                   'Error running sosreport: %s' % e
                                   )
                  )

    def collect(self):
        ''' For each node, start a collection thread and then tar all
        collected sosreports '''
        # local sosreport
        if not self.config['no_local']:
            if not self.config['master'] and self.can_run_local_sos():
                worker = threading.Thread(target=self.local_sosreport)
                worker.start()
                self.threads.append(worker)
        if self.master:
            self.client_list.append(self.master)
        for node in self.node_list:
            client = SosNode(node, self.config)
            self.client_list.append(client)
        for client in self.client_list:
            worker = threading.Thread(target=client.sosreport)
            worker.start()
            self.threads.append(worker)
            self.workers.append(client)
        for worker in self.threads:
            worker.join()
        for node in self.workers:
            if node.retrieved:
                self.retrieved += 1
        if hasattr(self.config['profile'], 'run_extra_cmd'):
            print('Collecting additional data from master node...')
            f = self.config['profile'].run_extra_cmd()
            if f:
                self.master.collect_extra_cmd(f)
        print('\nSuccessfully captured %s of %s sosreports' % (self.retrieved,
                                                               self.report_num
                                                               )
              )
        if self.retrieved > 0:
            self.create_cluster_archive()
        else:
            msg = 'No sosreports were collected, nothing to archive...'
            self._exit(msg)
        self.close_all_connections()

    def close_all_connections(self):
        '''Close all ssh sessions for nodes'''
        for client in self.client_list:
            client.close_ssh_session()

    def create_cluster_archive(self):
        '''Calls for creation of tar archive then cleans up the temporary
        files created by clustersos'''
        print('Creating archive of sosreports...')
        self.create_sos_archive()
        if self.archive:
            self.cleanup()
            print('\nThe following archive has been created. Please '
                  'provide it to your support team.'
                  )
            print('    %s' % self.archive)

    def create_sos_archive(self):
        '''Creates a tar archive containing all collected sosreports'''
        try:
            self.archive = self._get_archive_path()
            with tarfile.open(self.archive, "w:gz") as tar:
                for f in os.listdir(self.config['tmp_dir']):
                    tar.add(os.path.join(self.config['tmp_dir'], f), arcname=f)
                tar.close()
        except Exception as e:
            msg = 'Could not create archive: %s' % e
            self._exit(msg)

    def cleanup(self):
        ''' Removes the tmp dir and all sosarchives therein.

            If tmp dir was supplied by user, only the sos archives within
            that dir are removed.
        '''
        if self.config['tmp_dir_created']:
            self.delete_tmp_dir()
        else:
            for f in os.listdir(self.config['tmp_dir']):
                if re.search('*sosreport-*tar*', f):
                    os.remove(os.path.join(self.config['tmp_dir'], f))
