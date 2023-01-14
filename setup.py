from setuptools import setup, find_packages

setup(
    name='bibtex-filter',
    version='dev',

    url='',
    author='',
    author_email='',
    license='MIT',
    classifiers=[
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],

    py_modules=[
        'bibtexfilter',
    ],
    include_package_data=True,
    data_files=[
        ('.', ['i18n.json'])
    ],
    install_requires=[
        'textual',
        'rich',
        'bibtexparser',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'bibtex-filter = bibtexfilter:main',
        ],
    },
)
