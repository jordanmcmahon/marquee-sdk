from distutils.core import setup

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
    install_requires=[
        'click >= 1.1',
        'ansible >= 1.6',
    ]
)
