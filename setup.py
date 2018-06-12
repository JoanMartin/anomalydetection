#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import find_packages, setup

install_require = [
    # Core dependencies
    "rx", "jsonschema", "python-dateutil",
    "numpy", "pandas", "statsmodels", "bokeh",
    # Kafka
    "kafka-python",
    # Google api base
    "oauth2client", "google-auth", "google-auth-httplib2",
    "google-api-python-client",
    # Google cloud base
    "google-cloud", "google-cloud-pubsub",
    # Dashboard
    "tornado", "PyYAML", "python-ldap", "websockets"
]

test_require = [
    "mock",
    "coverage",
    "nose",
    "tox"
]

setup(
    name='anomalydetection',
    version='0.0.0',
    description='Anomaly detection bridge',
    url='',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages('src', exclude=("test", "test.*")),
    package_dir={'': 'src'},
    install_requires=install_require,
    test_suite="nose.collector"
)
