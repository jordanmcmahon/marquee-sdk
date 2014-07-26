from click import echo, prompt

from marquee_sdk.utils  import cli_explaination, cli_response, copy_template
from marquee_sdk.config import (
    TEMPLATE_DIR,
    MARQUEE_API_DEFAULTS as DEFAULTS,
)

import click
import json
import os
import re
import shutil
import socket
import textwrap

@click.group()
def cli():
    pass

@cli.command()
def runtime():
    echo("Let's create a new Marquee Runtime")
    RUNTIME_CONFIG = {}

    # Ask for project name
    cli_explaination("""
    First, we'll need to give your project a name. It will be stored
    as a spaceless lowercase string.

    Alphanumeric characters and dashes (-) are allowed.
    """)
    prompt_valid = False
    project_name = None
    while prompt_valid is False:
        project_name = prompt('Project Name')
        project_name = project_name.lower()
        project_path = os.path.join(os.getcwd(), project_name)
        if os.path.exists(project_path):
            echo('A directory named {0} already exists. Try again'.
                    format(project_name))
        else:
            prompt_valid = True
            os.makedirs(project_name)
    RUNTIME_CONFIG['project_name']  = project_name
    RUNTIME_CONFIG['domain']        = '{0}.local'.format(project_name)

    # Ask for private IP
    cli_explaination("""
    Next we'll need to assign a local private IP address to this runtime.

    This will allow you to access your local development environment
    through a browser by visiting http://{0}.local.

    You should check /etc/hosts for conflicts before choosing an IP.

    Sticking to the 10.0.1.2 - 10.0.1.255 range is generally safe.
    """.format(project_name))
    private_ip          = None
    prompt_valid        = False
    while prompt_valid is False:
        private_ip = prompt('Private IP')
        try:
            socket.inet_aton(private_ip)
            prompt_valid = True
        except socket.error:
            echo('{0} is an invalid IP. Try again')

    # Ask for Marquee Publication ID
    cli_explaination("""
    Please enter your Marquee Publication ID. This is sometimes called the
    *slug* or *short name* of your publication.

    If using the Marquee Editorial Tools, you can easily determine this by
    looking at the URL. Your publication name will be the *foo* in *foo.marquee.by*
    or the *bar* in *marquee.by/bar*. You can also find this ID in your
    Publication's Settings module.

    If you skip this step, we'll use the project name you just created.
    """)
    publication_slug = None
    prompt_valid     = False
    while prompt_valid is False:
        publication_slug = click.prompt('Marquee Publication ID', default=DEFAULTS['publication_slug'])
        prompt_valid = True # TODO validate this against API
    RUNTIME_CONFIG['plublication_slug'] = publication_slug

    # Ask for Marquee Access Token
    cli_explaination("""
    In order to access content on Marquee, you'll need the publication's
    Marquee Access Token.

    If you've been given an access token, enter it here.

    Otherwise, you can just skip this step and we'll use generic
    content we host for demo purpose consisting of short stories
    from Project Gutenberg (http://gutenberg.org).
    """)
    marquee_token = None
    prompt_valid  = False
    while prompt_valid is False:
        marquee_token = click.prompt('Marquee Access Token',
                            default=DEFAULTS['marquee_token'])
        prompt_valid  = True # TODO validate this against API
    RUNTIME_CONFIG['marquee_token'] = marquee_token

    # Write config file
    env_filepath = os.path.join(project_path, '.marquee-runtime')
    cli_explaination("""
    Ok, now we'll save write thse settings (along with a few
    defaults) to a config file which will be used by the Marquee Runtime.
    """)
    click.confirm('Do you want to continue?', default=True)

    with open(env_filepath, 'w') as env_file:
        json_config = {}
        for key, value in RUNTIME_CONFIG.iteritems():
            json_config[key] = value
        json.dump(json_config, env_file)

    cli_response('Marquee Runtime configuration written to {0}'.
            format(env_filepath))

    # Copy runtime project structure
    cli_explaination("""
    The Marquee Runtime provides a basic interface to a publication's
    content.

    The code that powers this interface is a distillation of patterns
    that we've found work well when building a web publication. Feel
    free to poke through the generated code to see how things work,
    make modifications to suit your own purposes, or rip everything
    out and start from scratch.

    By continuing, you will copy our default project structure
    """)
    click.confirm('Do you want to continue?', default=True)
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        pattern = re.compile('^.+\/scaffolding\/(.+)$')
        try:
            relative_path = pattern.findall(root)[0]
        except IndexError:
            relative_path = '.'
        for d in dirs:
            os.makedirs(os.path.join(project_path, relative_path, d))
        for f in files:
            src  = os.path.join(relative_path, f)
            dest = os.path.join(project_path, relative_path, f)
            copy_template(
                src             = src,
                dest            = dest,
                project_name    = project_name,
                host_ip         = private_ip,
                runtime_domain  = '{0}.local'.format(project_name),
            )
            cli_response(src)

    cli_explaination("""
    # Marquee Runtime Generated!

    Make sure you have an entry for this project in `/etc/hosts`.

        {private_ip}    {project_name}.local

    This is a handy one-liner for adding projects to /etc/hosts:

        $ echo "{private_ip} {project_name}.local" | sudo tee -a /etc/hosts

    Next change into your new project directory and fire up the
    development environment

        $ cd {project_name}
        $ vagrant up

    """.format(**locals()))
