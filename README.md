# RenamingGeneStrains
A Python script that takes FASTA files and a BLAST database to transform accession numbers into proper strain + gene names.


[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)

## Features
- Extracts strain names from BLAST DB descriptions
- Handles duplicate strains (appends accession)
- Fully configurable via USER INPUT section
- Works with any species/gene/dataset

## Requirements

- BLAST+ tools (`blastdbcmd`)

## Quick Start
1. **Download** `strain_renamer.py`
2. **Edit USER INPUT** section with your paths
3. **Run**: `python strain_renamer.py`

## Complete Script (Copy Button ⤴)
```python
import subprocess
import os
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

# ===== USER INPUT - EDIT THESE =====
input_fasta = "path/to/your_input_genes.fasta"
output_fasta = "path/to/your_output_renamed.fasta"
blast_db_dir = "path/to/blastdb_directory"
blast_db_name = "your_blast_db_name"
species_name = "Proteus mirabilis"
gene_name = "GENE"
# ==================================

cmd = (
    f'cd "{blast_db_dir}" && '
    f'blastdbcmd -db {blast_db_name} -entry all -outfmt "%a %t"'
)
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

accession_to_strain = {}
for line in result.stdout.strip().split("\\n"):
    if not line:
        continue
    parts = line.split(" ", 1)
    if len(parts) != 2:
        continue
    acc, description = parts
    if " strain " in description:
        strain = description.split(" strain ").split(" ")[1]
    else:
        strain = (
            description.replace(species_name + " ", "")
            .split(",")
            .split(" chromosome")
            .strip()
        )
    accession_to_strain[acc] = strain

seen_strain = {}
renamed_records = []
for record in SeqIO.parse(input_fasta, "fasta"):
    acc = record.id.split("|")

    if acc in accession_to_strain:
        strain_name = accession_to_strain[acc]
    else:
        strain_name = acc

    if strain_name in seen_strain:
        new_id = f"{strain_name}_{acc}|{gene_name}"
    else:
        new_id = f"{strain_name}|{gene_name}"
        seen_strain[strain_name] = acc

    renamed_records.append(SeqRecord(record.seq, id=new_id, description=""))

os.makedirs(os.path.dirname(output_fasta) or ".", exist_ok=True)
SeqIO.write(renamed_records, output_fasta, "fasta")
print(f"Output: {output_fasta}")
```
