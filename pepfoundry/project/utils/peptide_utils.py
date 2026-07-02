import os
import pandas as pd
from rdkit import Chem  
from rdkit.Chem import rdPartialCharges
from rdkit.Chem import Draw  
from IPython.display import display 
import re
from openbabel import openbabel, pybel

import numpy as np
import torch
from IPython.display import Image, display
from collections import defaultdict
from sklearn.preprocessing import OneHotEncoder

class PeptideUtils:
    """
    Utility class for processing peptide sequences and SMILES strings.
    Includes methods for reading amino acid data, parsing sequences, and modifying SMILES.
    """
    
    @staticmethod
    def util_extract_characters(sequence):
        """
        Extracts characters or residue blocks from a sequence.
        Groups inside `{}` are treated as single units.
        
        Args:
            sequence (str): Input sequence string.
        
        Returns:
            list: List of characters and grouped residues.
        """
        pattern = r'\{[^}]*\}|[a-zA-Z]'
        return re.findall(pattern, sequence)
    
    @staticmethod
    def util_removing_O_and_H(smile, index, characters, character=None):
        """
        Adjusts the SMILES string by removing terminal oxygen and modifying nitrogen groups.
        
        Args:
            smile (str): Input SMILES string.
            index (int): Position in the sequence.
            characters (list): List of characters in the sequence.
            character (str, optional): Current residue (used for warnings).
        
        Returns:
            str: Modified SMILES string.
        """
        if index < len(characters) and smile.endswith("O"):
            smile = smile[:-1]
        
        if index > 1:
            if smile.startswith("[N:1]") and character is not None:
                print(f"Warning: The amino acid '{character}' cannot form a peptide bond because the nitrogen's bonds are already saturated.")
            if smile.startswith("[NH2:1]"):
                smile = smile.replace("[NH2:1]", "[NH1:1]", 1)
            elif smile.startswith("[NH2]"):
                smile = smile.replace("[NH2]", "[NH1]", 1)
            elif smile.startswith("[NH1:1]"):
                smile = smile.replace("[NH1:1]", "[N:1]", 1)
            elif smile.startswith("[NH3:1]"):
                smile = smile.replace("[NH3:1]", "[NH2:1]", 1)

        return smile
    
    @staticmethod
    def util_handle_modifications(character, index, characters, special_smile, dictionary):
        """
        Handles special SMILES modifications (e.g., PEG, acetyl groups) at N-terminus or mid-chain.
        
        Args:
            character (str): Current character in sequence.
            index (int): Position in sequence.
            characters (list): Entire character list.
            special_smile (str): SMILES fragment to insert.
            dictionary (dict): Amino acid dictionary.
        
        Returns:
            tuple: (Modified SMILES, updated index)
        """
        if character not in dictionary:
            raise ValueError(f"The character '{character}' is not found in the dictionary.")
        
        n_pattern = r"^\[(NH2|NH1|N|NH3):1\]|\[NH2\]"
        
        if index == 0:
            if index + 1 < len(characters) and characters[index + 1] in dictionary:
                next_smile = dictionary[characters[index + 1]][1]
                match = re.match(n_pattern, next_smile)
                if match:
                    prefix = match.group(0)
                    rest = next_smile[len(prefix):]
                    next_smile = prefix + special_smile + rest
                    next_smile = PeptideUtils.util_removing_O_and_H(next_smile, index + 2, characters)
                    return next_smile, index + 1
                else:
                    raise ValueError(
                        f"The SMILE of the character '{characters[index + 1]}' does not start with a valid N-terminus group.")
            else:
                raise ValueError(f"There is no valid character after '{character}'.")
        else:
            prev_smile = dictionary[characters[index - 1]][1]
            if re.match(n_pattern, prev_smile):
                prev_smile = prev_smile[:1] + special_smile + prev_smile[1:]
                prev_smile = PeptideUtils.util_removing_O_and_H(prev_smile, index, characters)
                return prev_smile, index
            else:
                raise ValueError(
                    f"The SMILE of the character '{characters[index - 1]}' does not start with a valid N-terminus group.")
    
    @staticmethod
    def util_forming_cycle(smile, characters):
        """
        Adjusts the SMILES string for cyclic peptides by ensuring proper nitrogen and oxygen handling.
        Args:
            smile (str): Input SMILES string.
            characters (list): List of characters in the sequence.
        Returns:
            str: Modified SMILES string for cyclic peptides.    
        
        """
        if smile.startswith("[N:1]") and characters[0] is not None:
            print(f"Warning: The amino acidS '{characters[0]}' and '{characters[-1]}' cannot form a peptide bond please check the Hidrogens saturation.")
            
        if smile.startswith("[NH2:1]"):
            smile = smile.replace("[NH2:1]", "[NH1:1]9", 1)
        elif smile.startswith("[NH2]"):
            smile = smile.replace("[NH2]", "[NH1]9", 1)
        elif smile.startswith("[NH1:1]"):
            smile = smile.replace("[NH1:1]", "[N:1]9", 1)
        elif smile.startswith("[NH3:1]"):
            smile = smile.replace("[NH3:1]", "[NH2:1]9", 1)
        
        if smile.endswith("O"):
            smile = smile.rsplit("O", 1)[0] + "9"
        
        else:
            print(f"Warning: The amino acid '{characters[-1]}'does not end with an oxygen atom, please check the structure.")
        
        return smile
    
    @staticmethod
    def util_show_molecule(mol):
        drawer = Draw.MolDraw2DCairo(800, 800)
        options = drawer.drawOptions()
        options.addAtomIndices = False
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        img = drawer.GetDrawingText()
        display(Image(data=img))
    
    @staticmethod
    def util_validate_exception_position(character, exception_value, position, last_position):
        if exception_value == 1 and position != 0:
            raise ValueError(f"Error: {character} can only be at the beginning.")
        if exception_value == 2 and position != last_position:
            raise ValueError(f"Error: {character} can only be at the end.")
        if exception_value == 3 and position != 0:
            raise ValueError(f"Error: The modification {character} can only be placed at the beginning.")
        if exception_value == 4 and position != last_position:
            raise ValueError(f"Error: The modification {character} must be the last element.")
    
    @staticmethod
    def util_atomic_features(amino_acids_mol):
        # Extracts atomic and bond features from a list of RDKit molecules.
        atom_features = {
            "atomic_number": [],
            "aromaticity": [],
            "num_bonds": [],
            "bonded_hydrogens": [],
            "hybridization": [],
            "implicit_valence": [],
        }
        bond_features = {
            "bond_type": [],
            "in_ring": [],
            "conjugated": [],
            "bond_aromatic": [],
            "valence_contribution_i": [],
            "valence_contribution_f": [],
        }
        # Accumulate features from all amino acid molecules
        for aa_mol in amino_acids_mol:
            Chem.SanitizeMol(aa_mol)
            Chem.AssignStereochemistry(aa_mol, cleanIt=True, force=True)
            rdPartialCharges.ComputeGasteigerCharges(aa_mol)
            
            atom_features["atomic_number"].extend([atom.GetAtomicNum() for atom in aa_mol.GetAtoms()])
            atom_features["aromaticity"].extend([int(atom.GetIsAromatic()) for atom in aa_mol.GetAtoms()])
            atom_features["num_bonds"].extend([atom.GetDegree() for atom in aa_mol.GetAtoms()])
            atom_features["bonded_hydrogens"].extend([atom.GetTotalNumHs() for atom in aa_mol.GetAtoms()])
            atom_features["hybridization"].extend([str(atom.GetHybridization()) for atom in aa_mol.GetAtoms()])
            atom_features["implicit_valence"].extend([atom.GetValence(Chem.ValenceType.IMPLICIT) for atom in aa_mol.GetAtoms()])
            # Bond features
            for bond in aa_mol.GetBonds():
                bond_features["bond_type"].append(bond.GetBondTypeAsDouble())
                bond_features["in_ring"].append(int(bond.IsInRing()))
                bond_features["conjugated"].append(int(bond.GetIsConjugated()))
                bond_features["bond_aromatic"].append(int(bond.GetIsAromatic()))
                bond_features["valence_contribution_i"].append(int(bond.GetValenceContrib(bond.GetBeginAtom())))
                bond_features["valence_contribution_f"].append(int(bond.GetValenceContrib(bond.GetEndAtom())))
        
        # Fit OneHotEncoders for each feature type
        def fit_encoder(values):
            encoder = OneHotEncoder()
            encoder.fit(np.array(list(set(values))).reshape(-1, 1))
            return encoder
        
        encoders = {
            "atomic_number": fit_encoder(atom_features["atomic_number"]),
            "aromaticity": fit_encoder(atom_features["aromaticity"]),
            "num_bonds": fit_encoder(atom_features["num_bonds"]),
            "bonded_hydrogens": fit_encoder(atom_features["bonded_hydrogens"]),
            "hybridization": fit_encoder(atom_features["hybridization"]),
            "implicit_valence": fit_encoder(atom_features["implicit_valence"]),
            "bond_type": fit_encoder(bond_features["bond_type"]),
            "in_ring": fit_encoder(bond_features["in_ring"]),
            "conjugated": fit_encoder(bond_features["conjugated"]),
            "bond_aromatic": fit_encoder(bond_features["bond_aromatic"]),
            "valence_contribution_i": fit_encoder(bond_features["valence_contribution_i"]),
            "valence_contribution_f": fit_encoder(bond_features["valence_contribution_f"]),
        }
        
        # Create node features dictionary
        node_features_dict = defaultdict(list)
        for atom, aromatic, bonds, hydrogen, hybrid, impli_vale in zip(
                                                                        atom_features["atomic_number"],
                                                                        atom_features["aromaticity"],
                                                                        atom_features["num_bonds"],
                                                                        atom_features["bonded_hydrogens"],
                                                                        atom_features["hybridization"],
                                                                        atom_features["implicit_valence"]
                                                                    ):
            
            node_key = f"{atom}_{aromatic}_{bonds}_{hydrogen}_{hybrid}_{impli_vale}"
            
            feature_node = np.concatenate([
                                            encoders["atomic_number"].transform([[atom]]).toarray()[0],
                                            encoders["aromaticity"].transform([[aromatic]]).toarray()[0],
                                            encoders["num_bonds"].transform([[bonds]]).toarray()[0],
                                            encoders["bonded_hydrogens"].transform([[hydrogen]]).toarray()[0],
                                            encoders["hybridization"].transform([[hybrid]]).toarray()[0],
                                            encoders["implicit_valence"].transform([[impli_vale]]).toarray()[0],
                                        ])
            
            # Store the feature vector in the dictionary
            node_features_dict[node_key] = feature_node
            
        # Create edge features dictionary
        edge_features_dict = defaultdict(list)
        for bond, ring, conjugat, aroma, valence_i, valence_f in zip(
                                                                    bond_features["bond_type"],
                                                                    bond_features["in_ring"],
                                                                    bond_features["conjugated"],
                                                                    bond_features["bond_aromatic"],
                                                                    bond_features["valence_contribution_i"],
                                                                    bond_features["valence_contribution_f"]
                                                                ):
            edge_key = f"{bond:.1f}_{ring:.1f}_{conjugat:.1f}_{aroma:.1f}_{valence_i:.1f}_{valence_f:.1f}"
            
            feature_edge = np.concatenate([
                                            encoders["bond_type"].transform([[bond]]).toarray()[0],
                                            encoders["in_ring"].transform([[ring]]).toarray()[0],
                                            encoders["conjugated"].transform([[conjugat]]).toarray()[0],
                                            encoders["bond_aromatic"].transform([[aroma]]).toarray()[0],
                                            encoders["valence_contribution_i"].transform([[valence_i]]).toarray()[0],
                                            encoders["valence_contribution_f"].transform([[valence_f]]).toarray()[0],
                                        ])
            
            # Store the feature vector in the dictionary
            edge_features_dict[edge_key] = feature_edge
        
        return node_features_dict, edge_features_dict
    
    @staticmethod
    def util_atomic_features_chirality(amino_acids_mol):
        # Extracts atomic and bond features from a list of RDKit molecules.
        atom_features = {
            "atomic_number": [],
            "aromaticity": [],
            "num_bonds": [],
            "bonded_hydrogens": [],
            "hybridization": [],
            "implicit_valence": [],
            "chirality": []
        }
        bond_features = {
            "bond_type": [],
            "in_ring": [],
            "conjugated": [],
            "bond_aromatic": [],
            "valence_contribution_i": [],
            "valence_contribution_f": [],
        }
        # Accumulate features from all amino acid molecules
        for aa_mol in amino_acids_mol:
            Chem.SanitizeMol(aa_mol)
            Chem.AssignStereochemistry(aa_mol, cleanIt=True, force=True)
            rdPartialCharges.ComputeGasteigerCharges(aa_mol)
            
            atom_features["atomic_number"].extend([atom.GetAtomicNum() for atom in aa_mol.GetAtoms()])
            atom_features["aromaticity"].extend([int(atom.GetIsAromatic()) for atom in aa_mol.GetAtoms()])
            atom_features["num_bonds"].extend([atom.GetDegree() for atom in aa_mol.GetAtoms()])
            atom_features["bonded_hydrogens"].extend([atom.GetTotalNumHs() for atom in aa_mol.GetAtoms()])
            atom_features["hybridization"].extend([str(atom.GetHybridization()) for atom in aa_mol.GetAtoms()])
            atom_features["implicit_valence"].extend([atom.GetValence(Chem.ValenceType.IMPLICIT) for atom in aa_mol.GetAtoms()])
            # Chirality feature: 
            """
            It reflects how chirality is encoded in the SMILES string.
            Possible values:
            CHI_UNSPECIFIED → no chirality specified.
            CHI_TETRAHEDRAL_CW → tetrahedral center marked as clockwise.
            CHI_TETRAHEDRAL_CCW → tetrahedral center marked as counterclockwise.
            Important: this is not necessarily the real R/S configuration; it just stores what the SMILES said (@ vs @@).
            """
            atom_features["chirality"].extend([str(atom.GetChiralTag()) for atom in aa_mol.GetAtoms()])
            
            # Bond features
            for bond in aa_mol.GetBonds():
                bond_features["bond_type"].append(bond.GetBondTypeAsDouble())
                bond_features["in_ring"].append(int(bond.IsInRing()))
                bond_features["conjugated"].append(int(bond.GetIsConjugated()))
                bond_features["bond_aromatic"].append(int(bond.GetIsAromatic()))
                bond_features["valence_contribution_i"].append(int(bond.GetValenceContrib(bond.GetBeginAtom())))
                bond_features["valence_contribution_f"].append(int(bond.GetValenceContrib(bond.GetEndAtom())))
        
        # Fit OneHotEncoders for each feature type
        def fit_encoder(values):
            encoder = OneHotEncoder()
            encoder.fit(np.array(list(set(values))).reshape(-1, 1))
            return encoder
        
        encoders = {
            "atomic_number": fit_encoder(atom_features["atomic_number"]),
            "aromaticity": fit_encoder(atom_features["aromaticity"]),
            "num_bonds": fit_encoder(atom_features["num_bonds"]),
            "bonded_hydrogens": fit_encoder(atom_features["bonded_hydrogens"]),
            "hybridization": fit_encoder(atom_features["hybridization"]),
            "implicit_valence": fit_encoder(atom_features["implicit_valence"]),
            "chirality": fit_encoder(atom_features["chirality"]),
            "bond_type": fit_encoder(bond_features["bond_type"]),
            "in_ring": fit_encoder(bond_features["in_ring"]),
            "conjugated": fit_encoder(bond_features["conjugated"]),
            "bond_aromatic": fit_encoder(bond_features["bond_aromatic"]),
            "valence_contribution_i": fit_encoder(bond_features["valence_contribution_i"]),
            "valence_contribution_f": fit_encoder(bond_features["valence_contribution_f"]),
        }
        
        # Create node features dictionary
        node_features_dict = defaultdict(list)
        for atom, aromatic, bonds, hydrogen, hybrid, impli_vale, chiral in zip(
                atom_features["atomic_number"],
                atom_features["aromaticity"],
                atom_features["num_bonds"],
                atom_features["bonded_hydrogens"],
                atom_features["hybridization"],
                atom_features["implicit_valence"],
                atom_features["chirality"],
            ):
            
            node_key = f"{atom}_{aromatic}_{bonds}_{hydrogen}_{hybrid}_{impli_vale}_{chiral}"
            
            feature_node = np.concatenate([
                                        encoders["atomic_number"].transform([[atom]]).toarray()[0],
                                        encoders["aromaticity"].transform([[aromatic]]).toarray()[0],
                                        encoders["num_bonds"].transform([[bonds]]).toarray()[0],
                                        encoders["bonded_hydrogens"].transform([[hydrogen]]).toarray()[0],
                                        encoders["hybridization"].transform([[hybrid]]).toarray()[0],
                                        encoders["implicit_valence"].transform([[impli_vale]]).toarray()[0],
                                        encoders["chirality"].transform([[chiral]]).toarray()[0]
                                    ])
            
            # Store the feature vector in the dictionary
            node_features_dict[node_key] = feature_node
        
        # Create edge features dictionary
        edge_features_dict = defaultdict(list)
        for bond, ring, conjugat, aroma, valence_i, valence_f in zip(
                                                                    bond_features["bond_type"],
                                                                    bond_features["in_ring"],
                                                                    bond_features["conjugated"],
                                                                    bond_features["bond_aromatic"],
                                                                    bond_features["valence_contribution_i"],
                                                                    bond_features["valence_contribution_f"]
                                                                ):
            edge_key = f"{bond:.1f}_{ring:.1f}_{conjugat:.1f}_{aroma:.1f}_{valence_i:.1f}_{valence_f:.1f}"
            
            feature_edge = np.concatenate([
                                            encoders["bond_type"].transform([[bond]]).toarray()[0],
                                            encoders["in_ring"].transform([[ring]]).toarray()[0],
                                            encoders["conjugated"].transform([[conjugat]]).toarray()[0],
                                            encoders["bond_aromatic"].transform([[aroma]]).toarray()[0],
                                            encoders["valence_contribution_i"].transform([[valence_i]]).toarray()[0],
                                            encoders["valence_contribution_f"].transform([[valence_f]]).toarray()[0],
                                        ])
            
            # Store the feature vector in the dictionary
            edge_features_dict[edge_key] = feature_edge
            
        return node_features_dict, edge_features_dict
    
    @staticmethod
    def util_extract_node_and_edge_keys(mol):
        """
        Extracts node and edge key features from an RDKit molecule.
        
        Parameters:
            mol (rdkit.Chem.Mol): An RDKit molecule object.\
        
        Returns:
            node_keys_features (list of str): Encoded string keys for atom-level features.
            edge_key_features (list of str): Encoded string keys for bond-level features.
        """
        # Atom-level (node) features
        Chem.SanitizeMol(mol)
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        rdPartialCharges.ComputeGasteigerCharges(mol)
        
        atomic_number = [atom.GetAtomicNum() for atom in mol.GetAtoms()]
        aromaticity = [int(atom.GetIsAromatic()) for atom in mol.GetAtoms()]
        num_bonds = [atom.GetDegree() for atom in mol.GetAtoms()]
        bonded_hydrogens = [atom.GetTotalNumHs() for atom in mol.GetAtoms()]
        hybridization = [str(atom.GetHybridization()) for atom in mol.GetAtoms()]
        implicit_valence = [atom.GetValence(Chem.ValenceType.IMPLICIT) for atom in mol.GetAtoms()]
        
        node_keys_features = [
                            f"{atomic}_{aromatic}_{bonds}_{hydrogen}_{hybrid}_{impli_vale}"
                            for atomic, aromatic, bonds, hydrogen, hybrid, impli_vale in zip(
                                                                                            atomic_number,
                                                                                            aromaticity,
                                                                                            num_bonds,
                                                                                            bonded_hydrogens,
                                                                                            hybridization,
                                                                                            implicit_valence
                                                                                        )
                            ]
        
        # Bond-level (edge) features
        edge_keys_features = []
        for bond in mol.GetBonds():
            bond_type = bond.GetBondTypeAsDouble()
            in_ring = int(bond.IsInRing())
            conjugated = int(bond.GetIsConjugated())
            bond_aromatic = int(bond.GetIsAromatic())
            valence_contribution_i = int(bond.GetValenceContrib(bond.GetBeginAtom()))
            valence_contribution_f = int(bond.GetValenceContrib(bond.GetEndAtom()))
            
            edge_key = f"{bond_type:.1f}_{in_ring:.1f}_{conjugated:.1f}_{bond_aromatic:.1f}_{valence_contribution_i:.1f}_{valence_contribution_f:.1f}"
            edge_keys_features.append(edge_key)
        
        return node_keys_features, edge_keys_features
    
    @staticmethod
    def util_extract_node_and_edge_keys_chirality(mol):
        """
        Extracts node and edge key features from an RDKit molecule.
        
        Parameters:
            mol (rdkit.Chem.Mol): An RDKit molecule object.
        
        Returns:
            node_keys_features (list of str): Encoded string keys for atom-level features.
            edge_key_features (list of str): Encoded string keys for bond-level features.
        """
        # Atom-level (node) features
        Chem.SanitizeMol(mol)
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        rdPartialCharges.ComputeGasteigerCharges(mol)

        atomic_number = [atom.GetAtomicNum() for atom in mol.GetAtoms()]
        aromaticity = [int(atom.GetIsAromatic()) for atom in mol.GetAtoms()]
        num_bonds = [atom.GetDegree() for atom in mol.GetAtoms()]
        bonded_hydrogens = [atom.GetTotalNumHs(includeNeighbors=True) for atom in mol.GetAtoms()]
        hybridization = [str(atom.GetHybridization()) for atom in mol.GetAtoms()]
        implicit_valence = [atom.GetValence(Chem.ValenceType.IMPLICIT) for atom in mol.GetAtoms()]
        chirality = [str(atom.GetChiralTag()) for atom in mol.GetAtoms()]
        
        # Node key features with chirality
        node_keys_features = [
            f"{atomic}_{aromatic}_{bonds}_{hydrogen}_{hybrid}_{impli_vale}_{chiral}"
            for atomic, aromatic, bonds, hydrogen, hybrid, impli_vale, chiral in zip(
                atomic_number,
                aromaticity,
                num_bonds,
                bonded_hydrogens,
                hybridization,
                implicit_valence,
                chirality,
            )
        ]
        
        # Bond-level (edge) features
        edge_keys_features = []
        for bond in mol.GetBonds():
            bond_type = bond.GetBondTypeAsDouble()
            in_ring = int(bond.IsInRing())
            conjugated = int(bond.GetIsConjugated())
            bond_aromatic = int(bond.GetIsAromatic())
            valence_contribution_i = int(bond.GetValenceContrib(bond.GetBeginAtom()))
            valence_contribution_f = int(bond.GetValenceContrib(bond.GetEndAtom()))
            
            edge_key = f"{bond_type:.1f}_{in_ring:.1f}_{conjugated:.1f}_{bond_aromatic:.1f}_{valence_contribution_i:.1f}_{valence_contribution_f:.1f}"
            edge_keys_features.append(edge_key)
        
        
        return node_keys_features, edge_keys_features
    
    
    @staticmethod
    def util_atomic_features_tensors(node_keys_features, edge_key_features, node_ft_dict, edge_ft_dict, device):
        """
        Builds PyTorch tensors for node and edge features using provided feature dictionaries and keys.
        
        Parameters:
            node_keys_features (list of str): Keys for node features.
            edge_key_features (list of str): Keys for edge features.
            node_ft_dict (dict): Dictionary mapping node keys to feature arrays.
            edge_ft_dict (dict): Dictionary mapping edge keys to feature arrays.
            device (str or torch.device): Device to place the tensors on ('cpu' or 'cuda').
        
        Returns:
            nodes_features (torch.Tensor): Tensor of shape [num_nodes, node_feature_dim].
            edges_features (torch.Tensor): Tensor of shape [num_edges, edge_feature_dim].
        """
        
        
        missing_node_keys = [key for key in node_keys_features if key not in node_ft_dict]
        missing_edge_keys = [key for key in edge_key_features if key not in edge_ft_dict]
        
        if missing_node_keys:
            raise KeyError(
                f"Missing node keys: {missing_node_keys}. "
                "Node features not found in the library. "
                "Format: "
                "{atomic_number}_{aromatic_atom_flag}_{number_of_bonds}_{number_of_hydrogens}_{hybridization}_{implicit_valence}. "
                "or with chiralities:"
                "{atomic_number}_{aromatic_atom_flag}_{number_of_bonds}_{number_of_hydrogens}_{hybridization}_{implicit_valence}_{chirality}. "
                "Please add examples for the missing keys."
            )

        if missing_edge_keys:
            raise KeyError(
                f"Missing edge keys: {missing_edge_keys}. "
                "Edge features not found in the library follow this format: "
                "{bond_type}_{in_ring_flag}_{conjugated}_{aromatic_flag}_{valence_contribution_to_atom_i}_{valence_contribution_to_atom_f}. "
                "Please add examples for the missing keys."
            )

        
        nodes_features = torch.tensor(
                                        np.array([node_ft_dict[key] for key in node_keys_features]),
                                        dtype=torch.float32,
                                        device=device
                                    )
        edges_features = torch.tensor(
                                        np.array([edge_ft_dict[key] for key in edge_key_features]),
                                        dtype=torch.float32,
                                        device=device
                                    )
        
        return nodes_features, edges_features
    
    @staticmethod
    def util_atomic_adjacency_matrix(mol, device):
        """
        Constructs an adjacency matrix for the atoms in an RDKit molecule.
        Parameters:
            mol (rdkit.Chem.Mol): An RDKit molecule object.
            device (str or torch.device): Device to place the tensor on ('cpu' or 'cuda').
        Returns:
            torch.Tensor: Adjacency matrix of shape [num_atoms, num_atoms]. 
        """
        edges=[]
        for bond in mol.GetBonds():
            edges.append((bond.GetBeginAtomIdx(),bond.GetEndAtomIdx()))
        
        graph_edges = [[x[0] for x in edges],[x[1] for x in edges]]
        
        return torch.tensor(graph_edges, dtype=torch.long, device=device)
    
    @staticmethod
    def util_plot_smiles_pair(original_smiles, converted_smiles):
        """
        Plot two molecules side by side using RDKit.
        """
        mol1 = Chem.MolFromSmiles(original_smiles)
        mol2 = Chem.MolFromSmiles(converted_smiles)

        if mol1 is None or mol2 is None:
            print("[WARNING] RDKit failed to parse one of the SMILES.")
            return

        img = Draw.MolsToImage([mol1, mol2], legends=["Canonical", "CHUCKLES"], subImgSize=(300, 300))
        display(img)
    
    @staticmethod
    def util_smiles_chuckles_format(peptide_smiles, plot):
        """
        This code was adapted from the work:

        CycloPs: Generating Virtual Libraries of Cyclized and Constrained Peptides 
        Including Nonnatural Amino Acids
        Fergal J. Duffy, Mélanie Verniere, Marc Devocelle, Elise Bernard, 
        Denis C. Shields, and Anthony J. Chubb
        Journal of Chemical Information and Modeling 2011 51 (4), 829-836
        DOI: 10.1021/ci100431r
        
        The original implementation can be found at:
        https://github.com/fergaljd/cyclops/blob/master/CycloPs/aa_converter.py
        
        Important notes about this adaptation:
        - Converted from Python 2 to Python 3 syntax
        - Integrated RDKit to canonicalize the input SMILES before any processing with OpenBabel.
        - Added atom mapping for terminal residues:
            N-terminal nitrogen is mapped as [NHX:1], where X is determined by implicit hydrogen count.
            C-terminal carbon is mapped as [C:2].
        - Optional plotting of canonical vs. CHUCKLES SMILES using RDKit for verification.
        - Uses OpenBabel/pybel for detecting N- and C-terminal patterns in amino-acid SMILES.
        - Maintains the original purpose: to reorder SMILES from N-terminus to C-terminus using CHUCKLES formatting.
        
        CHUCKLES reference:
        CHUCKLES: A method for representing and searching peptide and peptoid sequences on both monomer and atomic levels
        Michael A. Siani, David Weininger, and Jeffrey M. Blaney
        Journal of Chemical Information and Computer Sciences 1994 34 (3), 588-593
        DOI: 10.1021/ci00019a017
        """
        # --- Canonicalize the input SMILES using RDKit ---
        mol_rd = Chem.MolFromSmiles(peptide_smiles)
        Chem.SanitizeMol(mol_rd)
        Chem.AssignStereochemistry(mol_rd, force=True, cleanIt=True)
        Chem.Kekulize(mol_rd, clearAromaticFlags=True)
        mol_rd.UpdatePropertyCache(strict=False)
        
        if mol_rd is None:
            raise ValueError("RDKit failed to parse the SMILES: " + peptide_smiles)
        canonical_smiles = Chem.MolToSmiles(mol_rd, canonical=True)
        
        # --- Load the canonical SMILES into OpenBabel ---
        conv = openbabel.OBConversion()
        conv.SetInAndOutFormats("smi", "smi")
        mol = openbabel.OBMol()
        conv.ReadString(mol, canonical_smiles)
        pbmol = pybel.Molecule(mol)
        
        # --- Define SMARTS patterns for N-terminal and C-terminal ---
        n_term_pat = pybel.Smarts('[$(NCC(O)=O)]')
        c_term_pat = pybel.Smarts('[$(OC(=O)CN)]')
        
        # --- Find matches for N-term and C-term ---
        n_term_matches = n_term_pat.findall(pbmol)
        c_term_matches = c_term_pat.findall(pbmol)
        
        if not n_term_matches or not c_term_matches:
            raise ValueError("Could not find N-term or C-term in SMILES: " + peptide_smiles)
        
        # --- Get the indices of N-term and C-term atoms ---
        n_idx = n_term_matches[0][0]
        c_idx = c_term_matches[0][0]
        
        # --- Count implicit hydrogens on N-terminal atom ---
        atomN = mol.GetAtom(n_idx)
        H_terminusN = atomN.GetImplicitHCount()
        #print('Number of hydrogens on N-terminal:', H_terminusN)
        
        # --- Reorder SMILES so that it starts at N-term and ends at C-term ---
        conv.AddOption("f", openbabel.OBConversion.OUTOPTIONS, str(n_idx))
        conv.AddOption("l", openbabel.OBConversion.OUTOPTIONS, str(c_idx))
        smiles = conv.WriteString(mol).strip()
        
        # --- Replace terminal atoms with mapped versions ---
        if H_terminusN != 0:
            # If N-terminal has implicit hydrogens, include them in the mapping
            smiles_mod = smiles.replace("N", f"[NH{H_terminusN}:1]", 1)
        else:
            smiles_mod = smiles.replace("N", f"[N:1]", 1)
        
        # Replace the last carbon with C-terminal mapping
        last_idx = smiles_mod.rfind("C")
        smiles_mod = smiles_mod[:last_idx] + "[C:2]" + smiles_mod[last_idx + 1:]
        
        # --- Optionally plot the original vs modified SMILES ---
        if plot:
            PeptideUtils.util_plot_smiles_pair(peptide_smiles, smiles_mod)
        
        return smiles_mod
