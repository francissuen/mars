import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(name="mars",
                 version="0.0.1",
                 author="Francis Sun",
                 author_email="francisjsun@outlook.com",
                 description="A python utils package.",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 # url="",
                 packages=setuptools.find_packages())
