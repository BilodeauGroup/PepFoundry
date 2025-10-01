from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = (
        "This library is used to obtain RDKit molecule objects from amino acid sequences, "
        "including non-natural amino acids present in the library."
    )

setup(
    name="pepfoundry",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.5",
        "rdkit>=2023.3.2",
        "torch>=1.13.1",
        "torchvision>=0.14.1",
        "openpyxl>=3.1.3",
        "scikit-learn>=1.0.2"
    ],
    include_package_data=True,
    package_data={
        "pepfoundry": ["project/core/amino_acids_library.xlsx"]
    },
    author="Daniel Garzon Otero",
    author_email="vvd9fd@virginia.edu",
    description="A module to obtain peptide RDKit molecule objects from amino acid sequences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BilodeauGroup/PepFoundry",
    python_requires='>=3.7.16',
)


