from distutils.core import setup

setup(name='CalCalc',
    version='1.0',
    license='LICENSE.txt',
    py_modules=['CalCalc'],
    author="Sean Wahl",
    author_email="swahl@berkeley.edu",
    url="https://github.com/smwahl/ay250_swahl/tree/master/hw_02",
    description="Calculator module for AY-250 python class",
    long_description=open('README.txt').read(),
    install_requires=[
        "lxml >= 3.1.0" ]
    )
