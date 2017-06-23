import socket


class Configuration(dict):
    """ Dict subclass that is used to handle configuration information
    needed by both ClusterSos and the SosNode classes """

    def __init__(self, parser=None):
        self.parser = parser
        self.set_defaults()
        self.parse_config()

    def set_defaults(self):
        self['sos_mod'] = {}
        self['master'] = ''
        self['strip_sos_path'] = ''
        self['ssh_port'] = '22'
        self['ssh_user'] = 'root'
        self['sos_cmd'] = 'sosreport --batch '
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

    def parse_config(self):
        args = vars(self.parser.parse_args())
        for k in args:
            if args[k]:
                self[k] = args[k]
