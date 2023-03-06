from setuptools import find_packages, setup, Command
from shutil import rmtree
import codecs, os, sys

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

required = []


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel distribution…")
        os.system("{0} setup.py sdist bdist_wheel".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v0.0.3")
        os.system("git push --tags")

        sys.exit()

setup(
    name='yusholib',
    packages=find_packages(include=['yusholib']),
    version='0.0.3',
    description='Python Library that includes some utils',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='yusho',
    license='MIT',
    url="https://github.com/yushodev/yusholib",
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==7.2.2'],
    test_suite='tests',
)