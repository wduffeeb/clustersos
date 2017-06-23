from profile import Profile

class kubernetes(Profile):

    sos_plugins = ['kubernetes']
    sos_options = {'kubernetes.all': 'on'}
    cleanup_cmd = 'docker rm clustersos-tmp'

    mod_release_string = 'Atomic'
    mod_cmd_prefix = 'atomic run --name=clustersos-tmp registry.access.redhat.com/rhel7/rhel-tools '
    mod_sos_path = '/host'

    def check_enabled(self):
        for k in self.config['packages']:
            if 'kubernetes' in k:
                return True
        return False

    def get_nodes(self):
        nodes = []
        n = self.exec_node_cmd('kubectl get nodes')
        nodes = [node.split()[0] for node in n]
        nodes.remove("NAME")
        return nodes
