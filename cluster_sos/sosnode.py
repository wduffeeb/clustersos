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
import fnmatch
import paramiko
import subprocess
import sys

from socket import timeout


class SosNode():

    def __init__(self, hostname, config):
        self.hostname = hostname
        self.config = config
        self.sos_path = None
        self.retrieved = False
        self.open_ssh_session()
        self.load_host_facts()

    def info(self, msg):
        '''Used to print and log info messages'''
        print "%-*s: %s" % (self.config['hostlen']+1, self.hostname, msg)

    @property
    def scp_cmd(self):
        '''Configure to scp command to retrieve sosreports'''
        cmd = 'scp -P %s ' % self.config['ssh_port']
        cmd += '%s@%s:%s* %s' % (self.config['ssh_user'],
                                 self.hostname,
                                 self.sos_path,
                                 self.config['tmp_dir']
                                 )
        return cmd

    def sosreport(self):
        '''Run a sosreport on the node, then collect it'''
        self.finalize_sos_cmd()
        self.execute_sos_command()
        self.retrieved = self.retrieve_sosreport()
        self.cleanup()

    def open_ssh_session(self):
        '''Create the persistent ssh session we use on the node'''
        try:
            msg = ''
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.load_system_host_keys()
            self.client.connect(self.hostname,
                                username=self.config['ssh_user'],
                                timeout=15
                                )
        except paramiko.AuthenticationException:
            msg = ("Authentication failed. Have you installed SSH keys?")
        except paramiko.BadAuthenticationType:
            msg = ("Bad authentication type. The node rejected authentication"
                   " attempt")
        except paramiko.BadHostKeyException:
            msg = ("Host key received was rejected by local SSH client."
                   " Check ~/.ssh/known_hosts.")
        except Exception as e:
            msg = '%s' % e
        if msg:
            self.info(msg)
            sys.exit()

    def close_ssh_session(self):
        '''Handle closing the SSH session'''
        try:
            self.client.close()
            return True
        except Exception as e:
            self.info('Error closing SSH session: %s' % e)
            return False

    def load_host_facts(self):
        '''Obtain information about the node which can be referneced by
        cluster profiles to change the sosreport command'''
        sin, sout, serr = self.client.exec_command('cat /etc/redhat-release')
        self.release = sout.read()

    def finalize_sos_cmd(self):
        '''Use host fact and compare to cluster profile to modify the sos
        command if needed'''
        self.sos_cmd = self.config['sos_cmd']
        if self.config['profile'].mod_release_string in self.release:
            self.sos_cmd = '%s %s' % (self.config['profile'].mod_cmd_prefix,
                                      self.config['sos_cmd']
                                      )

    def execute_sos_command(self):
        '''Run sosreport and capture the resulting file path'''
        self.info('Generating sosreport...')
        try:
            stdin, self.stdout, self.stderr = self.client.exec_command(
                                                self.sos_cmd,
                                                timeout=self.config['timeout'],
                                                get_pty=True
                                            )
            while not self.stdout.channel.exit_status_ready():
                if self.stdout.channel.recv_ready():
                    for line in iter(lambda: self.stdout.readline(1024), ""):
                        if fnmatch.fnmatch(line, '*sosreport-*tar*'):
                            self.sos_path = line.strip().replace(
                                self.config['profile'].mod_sos_path,
                                ''
                                )
            if self.stdout.channel.recv_exit_status() == 0:
                pass
            else:
                print stout.read()
                self.info('Error running sosreport: %s' % self.stderr.read())
        except timeout:
            self.info('Timeout exceeded')
            sys.exit()
        except Exception as e:
            self.info(e)

    def retrieve_sosreport(self):
        '''Collect the sosreport archive from the node'''
        if self.sos_path:
            self.info('Retrieving sosreport...')
            proc = subprocess.Popen(self.scp_cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE
                                    )
            stdout, stderr = proc.communicate()
            rc = proc.returncode
            if rc == 0:
                return True
            else:
                self.info('Failed to retrieve sosreport. %s' % stderr)
                return False
        else:
            # sos sometimes fails but still returns a 0 exit code
            self.info('Failed to run sosreport. %s' % self.stderr.read())
            return False

    def remove_sos_archive(self):
        '''Remove the sosreport archive from the node, since we have
        collected it and it would be wasted space otherwise'''
        try:
            self.client.exec_command('rm -f %s' % self.sos_path)
        except Exception as e:
            self.info('Failed to remove sosreport on host: %s' % e)

    def cleanup(self):
        self.remove_sos_archive()
        sin, sout, serr = self.client.exec_command(
                                self.config['profile'].cleanup_cmd,
                                timeout=15
                            )
