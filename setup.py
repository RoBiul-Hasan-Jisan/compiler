from setuptools import setup, find_packages

setup(
    name="mcpp-compiler",
    version="1.0.0",
    description="A small compiler/interpreter for a C++-like teaching language, written in Python.",
    packages=find_packages(include=["mcpp", "mcpp.*"]),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "mcpp=mcpp.cli:main",
        ],
    },
)
