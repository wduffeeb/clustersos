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
import os
import fnmatch

from clustersos.profiles import Profile
from getpass import getpass


class ovirt(Profile):

    packages = ('ovirt-engine', 'rhevm')
    sos_plugins = ['ovirt']

    option_list = [
                   ('no-database', '', 'Do not collect a database dump'),
                   ('cluster', 'string',
                    'Only collect from hosts in this cluster')
                   ]

    def get_nodes(self):
        if not self.get_option('no-database'):
            self.conf = self.parse_db_conf()
            self.get_db = self.check_db_password()
        else:
            self.get_db = False
        dbcmd = '/usr/share/ovirt-engine/dbscripts/engine-psql.sh -c '
        if not self.get_option('cluster'):
            dbcmd += '"select host_name from vds_static"'
        else:
            dbcmd += ('"select v.host_name from vds_static as v, cluster as c '
                      'where v.cluster_id = (select cluster_id from cluster '
                      'where name = \'%s\') "' % self.get_option('cluster')
                      )
        nodes = self.exec_master_cmd(dbcmd)[2:-2]
        return [n.strip() for n in nodes]

    def run_extra_cmd(self):
        if self.get_db:
            return self.collect_database()
        return False

    def check_db_password(self):
        if not self.conf:
            print('Could not parse database configuration. Will not attempt '
                  'to collect a database dump from the manager'
                  )
            return False
        pg_pass = getpass('Please provide the engine database password: ')
        if pg_pass == self.conf['ENGINE_DB_PASSWORD']:
            return True
        else:
            print('Password does not match configuration password. Will not '
                  'collect database dump from the manager'
                  )
            return False

    def parse_db_conf(self):
        conf = {}
        engconf = '/etc/ovirt-engine/engine.conf.d/10-setup-database.conf'
        config = self.exec_master_cmd('cat %s' % engconf)
        for line in config:
            k = str(line.split('=')[0])
            v = str(line.split('=')[1].replace('"', ''))
            conf[k] = v
        return conf

    def collect_database(self):
        sos_opt = (
                   '-k {plugin}.dbname={db} '
                   '-k {plugin}.dbhost={dbhost} '
                   '-k {plugin}.dbport={dbport} '
                   '-k {plugin}.username={dbuser} '
                   ).format(plugin='postgresql',
                            db=self.conf['ENGINE_DB_DATABASE'],
                            dbhost=self.conf['ENGINE_DB_HOST'],
                            dbport=self.conf['ENGINE_DB_PORT'],
                            dbuser=self.conf['ENGINE_DB_USER']
                            )
        cmd = ('PGPASSWORD={} /usr/sbin/sosreport --name=postgresqldb '
               '--batch -o postgresql {}'
               ).format(self.conf['ENGINE_DB_PASSWORD'], sos_opt)
        db_sos = self.exec_master_cmd(cmd)
        for line in db_sos:
            if fnmatch.fnmatch(line, '*sosreport-*tar*'):
                return line.strip()
        print('Failed to gather database dump')
        return False
