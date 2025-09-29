from setuptools import find_packages, setup

package_name = 'moma_pickplace'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='kalanaratnayake95@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'demo = omron_moma.demo:main',
            'teach_setup = omron_moma.teach_setup:main',
            'view_publisher = omron_moma.view_transform_publisher:main'
        ],
    },
)
