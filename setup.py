from setuptools import setup, find_packages


setup(
    name='django-rest-framework-auth',
    version='0.1.0dev',
    packages=find_packages(exclude=['*.tests']),
    scripts=[],

    install_requires=[
        'Django<2.2,>=1.11.21',
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
