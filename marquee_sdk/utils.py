from    .config     import *
import  jinja2

template_loader = jinja2.FileSystemLoader(TEMPLATE_DIR)
template_env    = jinja2.Environment(loader=template_loader)

def copy_template(src, dest, **kwargs):
    template = template_env.get_template(src)
    contents = template.render(**kwargs)
    with open(dest, 'w') as f:
        f.write(contents)
