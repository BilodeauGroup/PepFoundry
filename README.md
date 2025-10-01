<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PepFoundry</title>
</head>
<body>

<h1 style="font-size: 150%;">PepFoundry</h1>

<div style="text-align: justify;">
    PepFoundry is a Python package designed to streamline peptide modeling beyond natural amino acids and linear topologies. It allows the incorporation of synthetic amino acids, the generation of cyclic peptides, and the creation of peptide graphs. The package also produces RDKit molecule objects, which are particularly useful for handling peptides in ML applications.
</div>

<img src="https://github.com/BilodeauGroup/PepFoundry/blob/master/fig/PepFoundry.gif" alt="Demo">

<h2>Installation Guide</h2>

<p>To create the environment with all required packages, simply download the file: <strong><code>setup_pepfoundry.sh</code></strong> and run the following script in your terminal:</p>

<pre><code>bash setup_pepfoundry.sh</code></pre>

<h3>1. Create a Conda Environment - Manually</h3>
<p>Alternatively, you can create the environment step by step by running the following commands manually in the terminal:</p>

<pre><code>conda create --name pepfoundry python=3.7.16</code></pre>

<h3>2. Activate the Environment</h3>

<pre><code>conda activate pepfoundry</code></pre>

<h3>3. Install Dependencies</h3>

<pre><code>pip install rdkit
pip3 install torch torchvision
pip install openpyxl
pip install scikit-learn
pip install ipykernel
pip install pandas
pip install git+https://github.com/BilodeauGroup/PepFoundry.git
</code></pre>

<h2>Usage</h2>

<p>Once installed, you can import and use the package in your Python scripts:</p>

<pre><code>from pepfoundry.interface import PepFoundry</code></pre>

<h2>About the PepFoundry class</h2>

<p>PepFoundry is the central interface for building peptide molecules and analyzing amino acids using RDKit. It combines the functionalities of peptide construction and amino acid processing through internal modules.</p>

<h2>Instantiating the class</h2>

<p>Before using it, you need to create an instance of the class:</p>

<pre><code>pepfoundry = PepFoundry()</code></pre>

<p>Optionally, you can provide a custom amino acid dictionary by passing the path to an Excel file:</p>

<pre><code>pepfoundry = PepFoundry(custom_dict_path="path/to/custom_amino_acids.xlsx")</code></pre>

<h2>About the Amino Acid Dictionary</h2>

<p>The dictionary contains the definitions of amino acids used for building peptides. It can be provided in two ways:</p>

<ul>
    <li><strong>Default:</strong> Loads the standard amino acid dictionary included with the package: <a href="pepfoundry/project/core/amino_acids_library.xlsx">amino_acids_library</a></li>
    <li><strong>Custom:</strong> You can provide your own Excel file as a custom dictionary.</li>
</ul>

<p><strong>Important:</strong> The custom dictionary must follow the expected structure, with amino acids defined in the <strong>CHUCKLES format</strong>, including <strong>Map Numbers</strong>.</p>

<p>Following this structure ensures that the peptide builder can correctly interpret the amino acids and construct molecules without errors.</p>

<h2>Example usage</h2>

<p>For a full usage example, please see the <a href="examples.ipynb">examples_PepFoundry.ipynb</a> notebook included in this repository.</p>

<h2>Peptide Notation</h2>

<ul>
    <li><strong>Natural amino acids:</strong>
        <ul>
            <li>L-amino acids are represented with <strong>uppercase letters</strong> (e.g., <code>A</code> for L-Alanine).</li>
            <li>D-amino acids are represented with <strong>lowercase letters</strong> (e.g., <code>a</code> for D-Alanine).</li>
        </ul>
    </li>
    <li><strong>Non-natural amino acids</strong> are enclosed in curly braces <code>{Xyz}</code>.</li>
    <li><strong>Modifications</strong> such as acetylation and amidation are also enclosed in <code>{}</code>, e.g.:
        <ul>
            <li><code>{ac}</code> for acetylation</li>
            <li><code>{am}</code> for amidation</li>
        </ul>
    </li>
    <li><strong>Available amino acids:</strong> All supported amino acids can be found in: <a href="pepfoundry/project/core/amino_acids_library.xlsx">amino_acids_library</a></li>
    <li><strong>SMILES construction or rewriting (CHUCKLES format):</strong> Examples of how to construct or rewrite SMILES for amino acids in <strong>CHUCKLES format</strong> are provided in: <a href="examples_CHUCKLES.ipynb">examples_CHUCKLES.ipynb</a></li>
</ul>

<h2>Author</h2>

<p><a href="https://github.com/danielgarzonotero">Daniel Garzón Otero</a></p>

</body>
</html>
