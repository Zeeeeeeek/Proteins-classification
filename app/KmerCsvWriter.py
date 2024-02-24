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
        if os.path.exists("./columns.tmp"):
            os.remove("./columns.tmp")

    def write_kmer_count(self, kmers: Dict[str, int], region_id: str, class_topology_fold_clan: str, sequence: str):
        # If all the given kmers are not in the kmer_column_indexes, update the first row of the file
        # and add the new kmers to the kmer_column_indexes
        if not all(kmer in self.kmer_column_indexes for kmer in kmers):
            self.write_columns_row(kmers.keys())
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

    def write_columns_row(self, new_columns):
        if len(new_columns) == 0:
            return
        with open("columns.tmp", "w") as file:
            file.write(f"region_id{self.separator}class_topology_fold_clan{self.separator}sequence")
            if len(self.kmer_column_indexes) > 0:
                sorted_columns = sorted(self.kmer_column_indexes, key=lambda x: self.kmer_column_indexes[x])
                for column in sorted_columns:
                    file.write(f"{self.separator}{column}")
            for column in [c for c in new_columns if c not in self.kmer_column_indexes]:
                file.write(f"{self.separator}{column}")
                self.kmer_column_indexes[column] = self.last_index
                self.last_index += 1

    def close(self):
        with open("columns.tmp", "r") as columns_file:
            columns = columns_file.read()
        with open("rows.tmp", "r") as rows_file:
            rows = rows_file.read()
        with open(self.output_path, "w") as file:
            file.write(columns)
            file.write("\n")
            file.write(rows)
        os.remove("columns.tmp")
        os.remove("rows.tmp")

