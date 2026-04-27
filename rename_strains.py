import subprocess
import os
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

# ===== USER INPUT - EDIT THESE =====
input_fasta = "path/to/your_input_genes.fasta"
output_fasta = "path/to/your_output_renamed.fasta"
blast_db_dir = "path/to/blastdb_directory"
blast_db_name = "your_blast_db_name"
species_name = "Species Name"
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
        strain = description.split(" strain ")[1].split(" ")[0]
    else:
        strain = (
            description.replace(species_name + " ", "")
            .split(",")[0]
            .split(" chromosome")[0]
            .strip()
        )
    accession_to_strain[acc] = strain

seen_strain = {}
renamed_records = []
for record in SeqIO.parse(input_fasta, "fasta"):
    acc = record.id.split("|")[0]

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