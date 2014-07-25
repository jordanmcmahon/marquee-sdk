from distutils.core import setup
from pip.req        import parse_requirements

install_reqs    = parse_requirements('requirements.txt')
reqs            = [str(ir.req) for ir in install_reqs]

setup(
    name='marquee-sdk',
    version='0.1.0',
    author='Droptype, Inc.',
    author_email='opensource@marquee.by',
    packages=['marquee_sdk'],
    package_dir={'marquee_sdk': 'marquee_sdk'},
    package_data={'marquee_sdk': ['templates/*']},
    data=['marquee_sdk/templates'],
    scripts=['bin/marquee'],
    url='http://github.com/marquee/marquee-sdk',
    install_requires=reqs,
)
