from typing import Dict
import os


class KmerCsvWriter:
    def __init__(self, output_path: str, separator: str = ","):
        self.output_path = output_path
        self.kmer_column_indexes: Dict[str, int] = dict()
        self.separator = separator
        self.last_index = 0
        if os.path.exists("./rows.tmp"):
            os.remove("./rows.tmp")

    def write_kmer_count(self, kmers: Dict[str, int], region_id: str, class_topology_fold_clan: str, sequence: str):
        if not all(kmer in self.kmer_column_indexes for kmer in kmers):
            self.add_columns(kmers.keys())
        with open("rows.tmp", "a") as file:
            file.write(f"{region_id}{self.separator}{class_topology_fold_clan}{self.separator}{sequence}")
            ordered_kmers = sorted(kmers, key=lambda x: self.kmer_column_indexes[x])
            expected_index = 0
            for kmer in ordered_kmers:
                index = self.kmer_column_indexes[kmer]
                while expected_index < index:
                    file.write(f"{self.separator}")
                    expected_index += 1
                file.write(f"{self.separator}{kmers[kmer]}")
                expected_index += 1
            file.write("\n")

    def add_columns(self, new_columns):
        if len(new_columns) == 0:
            return
        for column in [c for c in new_columns if c not in self.kmer_column_indexes]:
            self.kmer_column_indexes[column] = self.last_index
            self.last_index += 1

    def close(self):
        with open(self.output_path, "w") as file:
            file.write(f"region_id{self.separator}class_topology_fold_clan{self.separator}sequence")
            sorted_columns = sorted(self.kmer_column_indexes, key=lambda x: self.kmer_column_indexes[x])
            for column in sorted_columns:
                file.write(f"{self.separator}{column}")
            file.write("\n")
        with open("rows.tmp", "r") as rows_file:
            for row in rows_file:
                with open(self.output_path, "a") as file:
                    stripped_row = row.strip()
                    if stripped_row != "":
                        file.write(stripped_row)
                        cells_count = stripped_row.count(
                            self.separator) + 1  # +1 because the last cell doesn't have a separator
                        if cells_count != len(self.kmer_column_indexes) + 3: # +3 because of the first 3 columns
                            for _ in range(len(self.kmer_column_indexes) - cells_count + 3):
                                file.write(f"{self.separator}")
                        file.write("\n")
        os.remove("rows.tmp")
