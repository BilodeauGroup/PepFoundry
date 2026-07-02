from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = (
        "PepFoundry: RDKit-based peptide construction toolkit "
        "supporting natural and non-natural amino acids."
    )

setup(
    name="pepfoundry",
    version="2.0.0",
    packages=find_packages(),

    install_requires=[
        "pandas>=2.0",
        "numpy>=1.26",
        "scikit-learn>=1.4",
        "torch>=2.0",
        "torchvision>=0.15",
        "openpyxl>=3.1",
    ],

    include_package_data=True,
    package_data={
        "pepfoundry": [
            "project/core/amino_acids_library.xlsx"
        ]
    },

    python_requires=">=3.11",

    author="Daniel Garzon Otero",
    author_email="vvd9fd@virginia.edu",
    description="A module to obtain peptide RDKit molecule objects from amino acid sequences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BilodeauGroup/PepFoundry",

    license="AGPL-3.0",
    license_files=["LICENSE"],
)