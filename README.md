# PepFoundry

PepFoundry is a Python package designed to streamline peptide modeling beyond natural amino acids and linear topologies. It allows the incorporation of synthetic amino acids, the generation of cyclic peptides, and the creation of peptide graphs. The package also produces RDKit molecule objects, which are particularly useful for handling peptides in ML applications.

![Demo](https://github.com/BilodeauGroup/PepFoundry/blob/master/fig/PepFoundry.gif)

## 1. Installation Guide

### 1.1. Creating an Anaconda Environment with PepFoundry

To create the environment with all required packages, simply download the file: **`setup_pepfoundry.sh`** and run the following script in your terminal:

```sh
bash setup_pepfoundry.sh 
```

### 1.2. Creating an Anaconda Environment Manually
Alternatively, you can create the environment manually by running the following commands manually in the terminal:

#### 1.2.1. Creating the Environment

```sh
conda create --name pepfoundry python=3.7.16
```

#### 1.2.2. Activating the Environment

```sh
conda activate pepfoundry
```

#### 1.2.3.  Installing Dependencies

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
#### 1.2.4.  Installing PepFoundry from GitHub
```sh
pip install git+https://github.com/BilodeauGroup/PepFoundry.git
```

## 2. Usage

Once installed, you can import and use the package in your Python scripts:

```python
from pepfoundry.interface import PepFoundry
```

### 2.1. PepFoundry Class
PepFoundry is the central interface for building peptide `RDKit Mol` objects. It combines the functionalities of peptide construction and amino acid processing through internal modules.

**Before using it, you need to create an instance of the class:**

```python
pepfoundry = PepFoundry()
```

The class use the [default database](pepfoundry/project/core/amino_acids_library.xlsx).

- **Default:**  
  Loads the standard amino acid database included with the package.
[amino_acids_library](pepfoundry/project/core/amino_acids_library.xlsx)

- **Custom Database**  
Optionally, you can provide a custom amino acid database for each class instance by passing the path to an Excel file:
```python
pepfoundry = PepFoundry(custom_dict_path="path/to/custom_amino_acids.xlsx")
```
**Important:** 
The Excel file should adhere to the format and conventions defined in the default database, with amino acids defined in the CHUCKLES format, including Map Numbers. Following this structure ensures that the peptide builder can correctly interpret the amino acids and construct molecules without errors.

### 2.2. Amino Acid Convention

- **Canonical Amino Acids:**  
  - **L-amino acids** are represented with **uppercase letters** (e.g., `A` for **L**-Alanine).  
  - **D-amino acids** are represented with **lowercase letters** (e.g., `a` for **D**-Alanine).  

- **Non-Canonical amino acids** are enclosed in curly braces `{Xyz}`.

- **Modifications** such as acetylation and amidation are also enclosed in `{}`, e.g.:  
  - `{ac}` for acetylation  
  - `{am}` for amidation  


## 3. Examples:

### 3.1. PepFoundry Implementation
Full usage examples are provided in:
[examples_PepFoundry](examples.ipynb) 
### 3.2. CHUCKLES Construction
**SMILES construction or rewriting (CHUCKLES format):**  
Examples of how to construct or rewrite SMILES for amino acids in **CHUCKLES format** are provided in:  
[examples_CHUCKLES.ipynb](examples_CHUCKLES.ipynb)

### 3.3. ML Implementation 
Examples of how PepFoudry can be implemented for ML application is provided in:  
[ML example](Example_ML)

## 4. How to cite this work:


