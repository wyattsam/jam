import yaml
import os


environment = os.getenv('ENV','devel')

_here = os.path.dirname(os.path.abspath(__file__))

try:
    path = 'config/{0}.yml'
    pathEnv = os.path.join(_here, '..', path.format(environment))
    _config_file = open(pathEnv, 'r')
    config = yaml.load(_config_file)
except IOError as e:
    errstr = (
        "Unable to find a valid config file at: config/{0}.yml. "
        "Please check README.md for more info.\n"
        "https://github.com/10gen/corp#setting-up-your-development-environment"
    )
    print(errstr.format(environment))
    raise SystemExit

try:
    _private_config_file = open(os.path.join(_here, '..', 'config/private.yml'), 'r')
    _private_config = yaml.load(_private_config_file)
    config.update(_private_config)
except IOError as e:
    pass

print("Using {0} environment configuration".format(environment))

jira_conf = config.get('jira', {})
jira_url = jira_conf['url']

