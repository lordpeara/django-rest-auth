from setuptools import setup, find_packages
import rest_auth


setup(
    name='django-rest-framework-auth',
    version=rest_auth.__version__,
    packages=find_packages(exclude=['*.tests']),
    scripts=[],

    install_requires=[
        'Django<2.0,>=1.11.21;python_version<"3.0"',
        'Django<2.2,>=2.0;python_version>="3.0"',
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
        # 'Framework :: Django',
        # 'Intended Audience :: Developers',
        # 'Intended Audience :: System Administrators',
        # 'Operating System :: OS Independent',
        # 'Topic :: Software Development'
    ],
)
