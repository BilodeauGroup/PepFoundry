#%%
from pepfoundry.project.core.peptide_builder import PeptideBuilder
from pepfoundry.project.core.amino_acid_builder import AminoAcidBuilder
from pepfoundry.project.core.library import AminoAcidDictionary

class PepFoundry():
    """
    Central interface for peptide construction and amino acid analysis using RDKit.
    Combines functionality from PeptideBuilder and AminoAcidBuilder.
    """
    
    def __init__(self, custom_dict_path=None):
        """
        Initializes the Smiles2Peptide class with optional dictionary path.
        If no path is provided, it defaults to loading the standard amino acid dictionary.
        Args:
            custom_dict_path (str, optional): Path to the amino acid dictionary Excel file.
        """
        self.peptide_builder = PeptideBuilder
        self.amino_acid_builder = AminoAcidBuilder
        
        # Initialize the amino acid dictionary
        self._init_amino_acid_dictionary(custom_dict_path)
        
        # Build the amino acids molecules from the dictionary
        self.amino_acids_mol = self._build_amino_acids_mol()
        
        # Precompute atomic features 'without' chiralities
        atomic_nodes_features, atomic_edge_features = self.peptide_builder.builder_atomic_features(self.amino_acids_mol, chiralities=False)
        self.library_atomic_nodes_features = atomic_nodes_features
        self.library_atomic_edge_features = atomic_edge_features
        
        # Precompute atomic features with chiralities
        atomic_nodes_features_chirals, atomic_edge_features_chirals = self.peptide_builder.builder_atomic_features(self.amino_acids_mol, chiralities=True)
        self.library_atomic_nodes_features_chirals = atomic_nodes_features_chirals
        self.library_atomic_edge_features_chirals = atomic_edge_features_chirals
    
    def _init_amino_acid_dictionary(self, custom_dict_path):
        """ Initializes the amino acid dictionary from a specified path or defaults to a standard file.
        Args:
            custom_dict_path (str, optional): Path to the amino acid dictionary Excel file.
        """
        aa_dict_instance = AminoAcidDictionary(custom_dict_path) if custom_dict_path else AminoAcidDictionary()
        self.dictionary = aa_dict_instance.as_dict()
        
        self.amino_acids = aa_dict_instance.get_all_amino_acids_notations()
        
    def _build_amino_acids_mol(self):
        """ 
        Constructs RDKit molecule objects for each amino acid in the dictionary.
        Returns:
            list: List of RDKit molecule objects for each amino acid.
        """ 
        amino_acids_mol = []
        for aa in (self.amino_acids):
            mol = self.peptide_builder.builder_peptide(
                                                        sequence=aa,
                                                        show_display=False,
                                                        peptide_type='linear',
                                                        amino_acid_library=self.dictionary
                                                    )
            amino_acids_mol.append(mol)
        return amino_acids_mol
    
    def get_library_atomic_nodes_features(self, chiralities=False):
        """
        Retrieve atomic node features from the library.
        
        This method returns the atomic node features computed from the amino acid molecules.
        Features are stored in a dictionary, where each key is a feature identifier and the 
        corresponding value is the feature vector.
        
        Args:
            chiralities (bool, optional): If True, return features that include chirality information.
                                        Default is False.
        
        Returns:
            dict: Dictionary containing atomic node features. Keys are feature identifiers and
                values are feature vectors.
        """
        if chiralities:
            return self.library_atomic_nodes_features_chirals
        else:
            return self.library_atomic_nodes_features
    
    def get_library_atomic_edge_features(self):
        """
        Prints the dimensions of the atomic node and edge feature vectors.
        
        Retrieves the atomic node and edge features from the library and prints
        the length (number of elements) of a single feature vector for each type.
        
        Args:
            chiralities (bool, optional): If True, use features that include chirality information.
                                        Default is False.
        """
        return self.library_atomic_edge_features
    
    def get_description_library_atomic_features(self,chiralities=False):
        """
        Prints the dimensions of the atomic node and edge feature vectors.
        
        This method retrieves the library of atomic node and edge features and
        reports the length of each feature vector. Optionally, chirality information
        can be included if `chiralities=True`.
        
        Args:
            chiralities (bool, optional): If True, include chirality in the feature
                                        definitions. Default is False.
        """
        node_features = self.get_library_atomic_nodes_features(chiralities=chiralities)
        edge_features = self.get_library_atomic_edge_features()
        
        node_dim = len(next(iter(node_features.values())))
        edge_dim = len(next(iter(edge_features.values())))
        print(f"Node feature vector length: {node_dim}")
        print(f"Edge feature vector length: {edge_dim}")
    
    
    def get_peptide_tensor_atomic_features(self, mol, chiralities= False, device ='cpu'):
        """
        Constructs atomic feature tensors for a given peptide molecule.
        
        This method extracts atomic and bond features from the RDKit molecule `mol`
        and converts them into PyTorch tensors suitable for machine learning models
        or graph neural networks. Atomic and bond features can optionally include
        chirality information.
        
        Args:
            mol (rdkit.Chem.Mol): RDKit molecule object representing the peptide.
            chiralities (bool, optional): If True, include chirality in the atomic
                                        features. Default is False.
            device (str, optional): Device to place the tensors on ('cpu' or 'cuda').
                                    Default is 'cpu'.
        
        Returns:
            tuple: A tuple containing two tensors:
                - atom_features_tensors (torch.Tensor): Shape [num_atoms, feature_dim], 
                containing atomic features.
                - edge_features_tensors (torch.Tensor): Shape [num_edges, feature_dim], 
                containing bond features.
        """
        node_keys_features, edge_key_features = self.peptide_builder.builder_peptide_atomic_features(mol,chiralities=chiralities)
        
        if chiralities:
            node_ft_dict = self.library_atomic_nodes_features_chirals
            edge_ft_dict= self.library_atomic_edge_features_chirals
        else:
            node_ft_dict = self.library_atomic_nodes_features
            edge_ft_dict= self.library_atomic_edge_features
        
        atom_features_tensors, edge_features_tensors = self.peptide_builder.builder_atomic_features_tensors(
                                                                                                            node_keys_features,
                                                                                                            edge_key_features,
                                                                                                            node_ft_dict,
                                                                                                            edge_ft_dict,
                                                                                                            device
                                                                                                            )
        
        return atom_features_tensors, edge_features_tensors
    
    def describe_peptide_atomic_features(self, mol, device='cpu'):
        """
        Prints the shape and a preview of the atomic and bond feature tensors for a given molecule.
        
        Args:
            mol (rdkit.Chem.Mol): RDKit molecule object.
            device (str, optional): Device to place the tensors on. Default is 'cpu'. Default is 'cpu'.
        """
        atom_features, bond_features = self.get_peptide_tensor_atomic_features(mol, device=device)
        
        print("Atom Features:")
        print(f"  - Shape: {atom_features.shape} (atoms × feature dimensions)")
        print(f"  - Number of atoms: {atom_features.shape[0]}")
        print(f"  - Feature dimension: {atom_features.shape[1]}")
        print("\nBond Features:")
        print(f"  - Shape: {bond_features.shape} (bonds × feature dimensions)")
        print(f"  - Number of bonds: {bond_features.shape[0]}")
        print(f"  - Feature dimension: {bond_features.shape[1]}")
    
    
    def get_peptide(self, sequence, plot_peptide=False, peptide_type='linear'):
        """
        Build a peptide molecule from a sequence.
        This method constructs an RDKit molecule from a peptide sequence, allowing for visualization if desired.
        It uses the peptide builder to create the molecule and can optionally display it.   
        
        Args:
            sequence (str): Peptide sequence.
            show_display (bool): Whether to visualize the molecule.
            peptide_type (str): Type of peptide ('linear' or 'cycle'). Default is 'linear'.
        
        Returns:
            Chem.Mol: RDKit molecule.
        """
        return self.peptide_builder.builder_peptide(sequence, plot_peptide, peptide_type, amino_acid_library=self.dictionary)
    
    
    def get_peptide_atomic_adjacency_matrix(self, mol, device='cpu'):
        """
        Constructs an adjacency matrix for the atoms in a peptide molecule.
        
        Args:
            mol (rdkit.Chem.Mol): RDKit molecule object.
            device (str or torch.device): Device to place the tensor on ('cpu' or 'cuda'). Default is 'cpu'.
        
        Returns:
            torch.Tensor: Adjacency matrix of shape [num_atoms, num_atoms].
        """
        return self.peptide_builder.builder_atomic_adjacency_matrix(mol, device)
    
    def get_plot_aminoacids(self, mol, highlight_bonds=False, obtain_amino_acids=False):
        """
        Visualize or fragment the peptide molecule.\
        
        Args:
            mol (Chem.Mol): RDKit molecule.
            highlight_bonds (bool): Highlight peptide bonds.
            obtain_amino_acids (bool): Display amino acid fragments.
        """
        return self.amino_acid_builder.builder_amino_acid_plotting(mol, highlight_bonds, obtain_amino_acids)
    
    def get_amino_acid_atom_mapping(self, mol, device='cpu'):
        """
        Get a tensor mapping each atom to its amino acid fragment.
        
        Args:
            mol (Chem.Mol): RDKit molecule.
        
        Returns:
            torch.Tensor: Mapping vector.
        """
        return self.amino_acid_builder.builder_amino_acid_mapping_vector(mol, device)
    
    def get_amino_acid_adjacency_matrix(self, sequence, device, peptide_type):
        """
        Get an adjacency matrix for the peptide sequence.
        
        Args:
            sequence (str): Peptide sequence.
            device (torch.device): Device for the resulting tensor. Default is 'cpu'.
            architecture (str): Type of adjacency matrix ('linear' or 'cycle').
        
        Returns:
            torch.Tensor: Adjacency matrix.
        """
        return self.amino_acid_builder.builder_amino_acid_adjacency_matrix(sequence, device, peptide_type, amino_acid_library=self.dictionary)
    
    def get_amino_acid_features(self, sequence, device='cpu'):
        """
        Constructs a tensor representing the features of each amino acid in a peptide sequence.
        Args:
            sequence (str): Peptide sequence string.
            device (str or torch.device): Device to store the resulting tensor (e.g., 'cpu' or 'cuda'). Default is 'cpu'.
        """
        return self.amino_acid_builder.builder_amino_acid_features(sequence, self.dictionary, device)
    
    

