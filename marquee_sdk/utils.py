from .config import *

import  ConfigParser
import  click
import  jinja2
import  os
import  shutil

template_loader = jinja2.FileSystemLoader(TEMPLATE_DIR)
template_env    = jinja2.Environment(loader=template_loader)

def copy_template(src, dest, **kwargs):
    skip = ['png', 'swp']
    if src[-3:] in skip or src.find('templates') != -1:
        shutil.copyfile(os.path.join(TEMPLATE_DIR, src), dest)
    else:
        template = template_env.get_template(src)
        contents = template.render(**kwargs)

        with open(dest, 'w') as f:
            f.write(contents)

def load_config(filepath, simple=True, section='config'):
    """
    Returns a dictionary

    Requires a path to a config file. By default, we will
    fake section heads required by ConfigParser. To turn this
    off, pass `simple=False` when calling this function.
    """
    if not os.path.isfile(filepath):
        print '{0} does not exist'.format(filepath)
        raise IOError

    if simple:
        fp = FakeSectionHead(open(filepath))
    else:
        fp = open(filepath)

    config = ConfigParser.SafeConfigParser()
    try:
        config.readfp(fp)
    except IOError:
        print '{0} is not a valid config file'.format(filepath)
        raise IOError

    return dict(config.items(section))

def cli_response(msg):
    click.echo(' - {0}'.format(msg))
