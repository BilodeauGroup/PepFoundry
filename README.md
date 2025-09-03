# PepFoundry

PepFoundry is a Python package designed to streamline peptide modeling beyond natural amino acids and linear topologies. With PepFoundry, you can incorporate synthetic amino acids, generate cyclic peptides, and create peptide graphs. The package also produces RDKit molecule objects, which are highly useful for handling peptides in ML/AI Python applications.

![Demo](https://github.com/BilodeauGroup/PepFoundry/blob/master/fig/PepFoundry.gif)

## Installation Guide

To create the environment with all required packages, simply download the file: **`setup_pepfoundry.sh`** and run the following script in your terminal:

```sh
bash setup_pepfoundry.sh 
```

### 1. Create a Conda Environment - Manually
Alternatively, you can create the environment step by step by running the following commands manually in the terminal:

```sh
conda create --name pepfoundry python=3.7.16
```

### 2. Activate the Environment

```sh
conda activate pepfoundry
```

### 3. Install Dependencies

```sh
pip install rdkit
```
```sh
pip3 install torch torchvision
```
```sh
pip install openpyxl
```
```sh
pip install scikit-learn
```
```sh
pip install ipykernel
```
```sh
pip install pandas
```
```sh
pip install git+https://github.com/BilodeauGroup/PepFoundry.git
```

## Usage

Once installed, you can import and use the package in your Python scripts:

```python
from pepfoundry.interface import PepFoundry
```

## About the PepFoundry class
PepFoundry is the central interface for building peptide molecules and analyzing amino acids using RDKit. It combines the functionalities of peptide construction and amino acid processing through internal modules.

## Instantiating the class
Before using it, you need to create an instance of the class:

```python
pepfoundry = PepFoundry()
```
Optionally, you can provide a custom amino acid dictionary by passing the path to an Excel file:
```python
pepfoundry = PepFoundry(custom_dict_path="path/to/custom_amino_acids.xlsx")
```

## About the amino acid dictionary
The dictionary contains the amino acids definitions used for building peptides. It can be:

Default: Loads the standard amino acid dictionary included with the package.

Custom: You can provide your own Excel file as a custom dictionary.

Important: The custom dictionary must follow the expected structure, with amino acids defined in the CHUCKLES format, including Map Numbers

This structure ensures the peptide builder can interpret and construct molecules correctly.

## Example usage:

For a full usage example, please see the [examples_PepFoundry.ipynb](examples.ipynb) notebook included in this repository.


## Peptide Notation

- **Natural amino acids:**  
  - L-amino acids are represented with **uppercase letters** (e.g., `A` for L-Alanine).  
  - D-amino acids are represented with **lowercase letters** (e.g., `a` for D-Alanine).  

- **Non-natural amino acids** are enclosed in curly braces `{Xyz}`.

- **Modifications** such as acetylation and amidation are also enclosed in `{}`, e.g.:  
  - `{ac}` for acetylation  
  - `{am}` for amidation  

- **Available amino acids:**  
  All supported amino acids can be found in:  


- **SMILES construction or rewriting (CHUCKLES format):**  
  Examples of how to construct or rewrite SMILES for amino acids in **CHUCKLES format** are provided in:  
[examples_CHUCKLES.ipynb](examples_CHUCKLES.ipynb)


## Author

[Daniel Garzón Otero](https://github.com/danielgarzonotero)
