from setuptools import setup, find_packages

setup(
    name='homomorphic-ml',
    description='Python implementations of CKKS and BFV cryptosystems with their application in ML',
    author='Dellwyn Tennison',
    author_email='dellwyntennison@gmal.com',
    license='MIT',
    install_requires=[
        'joblib',
        'numpy',
    ],
    packages=['BFV_Scheme', 'CKKS_Scheme', 'utils']
)