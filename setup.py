from setuptools import setup, find_packages

setup(
    name='duplocli',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click', 'requests'
    ],
    entry_points='''
        [console_scripts]
        duplocli=duplocli.components.core:cli        
    ''',
)
