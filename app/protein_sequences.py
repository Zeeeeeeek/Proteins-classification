import collections
from io import StringIO

from Bio.PDB import PDBParser, MMCIFParser

from app.api import pdb_get, mmCIF_get


def three_residue_to_one(residue):
    match residue:
        case "ALA":
            return "A"
        case "CYS":
            return "C"
        case "ASP":
            return "D"
        case "GLU":
            return "E"
        case "PHE":
            return "F"
        case "GLY":
            return "G"
        case "HIS":
            return "H"
        case "ILE":
            return "I"
        case "LYS":
            return "K"
        case "LEU":
            return "L"
        case "MET":
            return "M"
        case "ASN":
            return "N"
        case "PRO":
            return "P"
        case "GLN":
            return "Q"
        case "ARG":
            return "R"
        case "SER":
            return "S"
        case "THR":
            return "T"
        case "VAL":
            return "V"
        case "TRP":
            return "W"
        case "TYR":
            return "Y"
        case "HOH":
            return ""
        case _:
            return "X"


def get_sequence_from_mmcif(file_mmcif, id_chain, start, end):
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure('structure', file_mmcif)
    residues = extract_res_dict(structure, id_chain, start, end)
    sequence = ""
    sorted_res_dict = collections.OrderedDict(sorted(residues.items(), key=lambda item: custom_key(item[0])))
    for value in sorted_res_dict.values():
        sequence += three_residue_to_one(value)
    return sequence


def extract_res_dict(structure, chain_id, start, end):
    res_dict = {}
    for model in structure:
        for chain in model:
            if chain.id != chain_id:
                continue
            for residue in chain:
                if start <= residue.get_full_id()[3][1] <= end:
                    if str(residue.get_full_id()[3][1]) not in res_dict.keys():
                        res_dict[str(residue.get_full_id()[3][1])] = residue.get_resname()
                    else:
                        res_dict[str(residue.get_full_id()[3][1]) + residue.get_full_id()[3][2]] = residue.get_resname()
        if len(res_dict) > 0:
            # A model has been found and used, finding other models with the same chain may lead to errors
            return res_dict
    return res_dict


def custom_key(key):
    parts = []
    current_part = ""
    is_negative = False

    for char in key:
        if char.isdigit() or (char == '-' and not current_part):
            # Check for the negative sign at the beginning of the part
            if char == '-' and not current_part:
                is_negative = True
            else:
                current_part += char
        else:
            if current_part:
                parts.append(int(current_part) * (-1 if is_negative else 1))
                current_part = ""
                is_negative = False
            parts.append(char)

    if current_part:
        parts.append(int(current_part) * (-1 if is_negative else 1))

    return parts


def get_missing_residues(structure, chain_id, start, end):
    missing_residues = {}
    for res in structure.header["missing_residues"]:
        if res['chain'] == chain_id and start <= res['ssseq'] <= end:
            if res['insertion'] is not None:
                identifier = str(res['ssseq']) + res['insertion']
            else:
                identifier = str(res['ssseq'])
            missing_residues[identifier] = res['res_name']
    return missing_residues


def get_sequence(pdb_id, chain_id, start, end):
    """
    Get the sequence of a protein from Protein Data Bank (PDB).
    :param pdb_id: The PDB ID of the protein.
    :param chain_id: The chain ID of the protein.
    :param start: The start index of the residues.
    :param end: The end index of the residues.
    :return: The sequence of the protein.
    """
    pdb = pdb_get(pdb_id)
    if pdb is None:
        return get_sequence_from_mmcif(StringIO(mmCIF_get(pdb_id)), chain_id, start, end)
    pdb_io = StringIO(pdb)
    pdb_parser = PDBParser(QUIET=True)
    structure = pdb_parser.get_structure(pdb_id, pdb_io)
    res_dict = extract_res_dict(structure, chain_id, start, end)
    if len(res_dict) != (end - start + 1):
        remarks = get_missing_residues(structure, chain_id, start, end)
        res_dict.update(remarks)
    sequence = ""
    sorted_res_dict = collections.OrderedDict(sorted(res_dict.items(), key=lambda item: custom_key(item[0])))
    for value in sorted_res_dict.values():
        sequence += three_residue_to_one(value)
    return sequence
