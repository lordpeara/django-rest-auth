import rest_auth
from setuptools import find_packages, setup


setup(
    name='django-rest-framework-auth',
    version=rest_auth.__version__,
    packages=find_packages(exclude=['*.tests']),
    scripts=[],

    install_requires=[
        'Django>=1.11.23,<2.0;python_version<"3.0"',
        'Django>=2.2.13,<3.0;python_version>="3.0"',
        'djangorestframework>=3.7',
    ],

    author='lordpeara',
    author_email='lordpeara@gmail.com',
    description='django authentication meets rest framework',
    license='MIT',
    keywords='django rest auth rest-framework authentication api',
    url='http://github.com/lordpeara/django-rest-auth',

    zip_safe=False,
    include_package_data=True,

    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
)
