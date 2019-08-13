import configparser


CONF_FILE = "/etc/jserver.conf"

gconfig = configparser.ConfigParser()
gconfig.read(CONF_FILE)


def get_qts():
    return gconfig['qts']

def get_build_server():
    return gconfig['build_server']

def get_local():
    return gconfig['local']

