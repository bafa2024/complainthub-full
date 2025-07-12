from setuptools import setup, find_packages

setup(
    name="complainthub",
    version="0.1.0",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    install_requires=[
        # List your project's dependencies here
        # They should match the ones in requirements.txt
    ],
    python_requires=">=3.7",
)
