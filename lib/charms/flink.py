import jujuresources
from jujubigdata import utils
from charmhelpers.core import unitdata, hookenv
import os.path
import sys

class Flink(object):
    def __init__(self, dist_config):
        self.dist_config = dist_config
        self.resources = {
            'flink': 'flink-%s' % utils.cpu_arch(),
        }
        self.verify_resources = utils.verify_resources(*self.resources.values())

    def is_installed(self):
        return unitdata.kv().get('flink.installed')

    def install(self, force=False):
        if not force and self.is_installed():
            return
        self.dist_config.add_users()
        self.dist_config.add_dirs()
        jujuresources.install(self.resources['flink'],
                              destination=self.dist_config.path('flink'),
                              skip_top_level=True)
        #self.setup_flink_config()
        unitdata.kv().set('flink.installed', True)

    def setup_flink(self):
        '''
        copy the default configuration files to flink_conf property
        defined in dist.yaml
        '''
        default_conf = self.dist_config.path('flink') / 'conf'
        flink_conf = self.dist_config.path('flink_conf')
        if os.path.islink(default_conf):
            return
        flink_conf.rmtree_p()
        default_conf.copytree(flink_conf)
        # Now remove the conf included in the tarball and symlink our real conf
        default_conf.rmtree_p()
        flink_conf.symlink(default_conf)

        # Configure immutable bits
        flink_bin = self.dist_config.path('flink') / 'bin'
        with utils.environment_edit_in_place('/etc/environment') as env:
            if flink_bin not in env['PATH']:
                env['PATH'] = ':'.join([env['PATH'], flink_bin])
            env['FLINK_CLASSPATH'] = env['HADOOP_CONF_DIR']
            env['FLINK_CONF_DIR'] = self.dist_config.path('flink_conf')
            env['FLINK_HOME'] = self.dist_config.path('flink')

    def start(self):
        flink_home = self.dist_config.path('flink')
        self.stop()
        containers = hookenv.config()['containers']
        containermem = hookenv.config()['containermem']
        utils.run_as('flink', '{}/bin/yarn-session.sh'.format(flink_home),
                     'start', '-n', containers, '-tm', containermem, '-d', '>',
                     '/home/flink/flink_startup.log')
        try:
            output = utils.run_as('flink', 'grep', 'kill', '/home/flink/flink_startup.log')
            flink_appID = output.split(" ")[3]
            unitdata.kv().set('flink.ID', flink_appID)
        except: 
            hookenv.log("Error getting flink yarn application ID - is flink running? is YARN reachable?")

    def stop(self):
        flink_appID = unitdata.kv().get('flink.ID')
        if flink_appID:
            utils.run_as('yarn', 'application', '-kill', flink_appID)
        return 

    def cleanup(self):
        self.dist_config.remove_users()
        self.dist_config.remove_dirs()
