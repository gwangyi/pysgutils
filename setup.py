from setuptools import setup, find_packages
import sys

setup_requires = [
    ]

if sys.version_info > (3,):
    install_requires = [
        'six'
        ]
else:
    install_requires = [
        "six",
        "enum34"
        ]

dependency_links = [
    ]

package_data = {
    'pysgutils.os.win32': ['libsgutils2-2.dll']
    }


setup(
    name="pysgutils",
    version="2017.1.2",
    description="libsgutils2 wrapper for python",
    author="Sungkwang Lee",
    author_email="gwangyi.kr@gmail.com",
    packages=find_packages(),
    package_data=package_data,
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    )
