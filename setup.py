import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(name="mars",
                 version="0.1.0",
                 # author="Francis Suen",
                 # author_email="francissuen@fs.com",
                 description="A python utils package.",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 # url="",
                 packages=setuptools.find_packages())
