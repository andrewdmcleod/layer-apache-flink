import jujuresources
from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv, unitdata
from jujubigdata import utils
from charmhelpers.fetch import apt_install
from subprocess import check_call
from charms.flink import Flink

DIST_KEYS = ['vendor', 'hadoop_version', 'groups', 'users', 'dirs']

def get_dist_config(keys):
    from jujubigdata.utils import DistConfig

    if not getattr(get_dist_config, 'value', None):
        get_dist_config.value = DistConfig(filename='dist.yaml', required_keys=keys)
    return get_dist_config.value

flink = Flink(get_dist_config(DIST_KEYS))

#@when('hadoop.installed')
@when_not('flink.installed')
def install_flink():
    if flink.verify_resources():
        hookenv.status_set('maintenance', 'Installing Flink')
        flink.install()
        set_state('flink.installed')


@when('flink.installed')
@when_not('hadoop.related')
def missing_hadoop():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop')


@when('flink.installed', 'hadoop.ready')
@when_not('flink.started')
def configure_flink(*args):
    hookenv.status_set('maintenance', 'Setting up flink')
    flink.setup_flink()
    flink.start()
    flink.open_ports()
    set_state('flink.started')
    flink_appID = unitdata.kv().get('flink.ID')
    hookenv.status_set('active', 'Ready ({})'.format(flink_appID))


@when('flink.started')
@when_not('hadoop.ready')
def stop_flink():
    remove_state('flink.started')
    flink.stop()
    flink.close_ports()
    hookenv.status_set('blocked', 'Waiting for Hadoop connection')


@when('flink.started', 'client.related')
def client_present(client):
    client.set_installed()


@when('client.related')
@when_not('flink.started')
def client_should_stop(client):
    client.clear_installed()
