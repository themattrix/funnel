from setuptools import setup, find_packages


setup(
    name="funnel",
    version="0.1.0",
    packages=find_packages(),

    # Tests run under nose.
    tests_require=['nose>=1.0'],

    # metadata for upload to PyPI
    author="Matthew Tardiff",
    author_email="mattrix@gmail.com",
    description="Capture or redirect stdout and stderr.",
    license="MIT",
    keywords="funnel capture redirect stdout stderr",
    url="https://github.com/themattrix/funnel",

    # could also include long_description, download_url, classifiers, etc.
)