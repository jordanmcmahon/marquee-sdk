from .config import *

import  jinja2
import  os
import  shutil

template_loader = jinja2.FileSystemLoader(TEMPLATE_DIR)
template_env    = jinja2.Environment(loader=template_loader)

def copy_template(src, dest, **kwargs):
    skip = ['.png', '.swp']
    if src[-4:] in skip:
        shutil.copyfile(os.path.join(TEMPLATE_DIR, src), dest)

    else:
        template = template_env.get_template(src)
        contents = template.render(**kwargs)

        with open(dest, 'w') as f:
            f.write(contents)

