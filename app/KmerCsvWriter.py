from typing import Dict, List
import os


class KmerCsvWriter:
    def __init__(self, output_path: str, non_kmer_columns: List[str], separator: str = ","):
        """
        This class is used to write kmer counts to a csv file.
        By using this class, the kmer counts are written to the
        csv file in the correct order, and the columns are added dynamically as new kmers are encountered.
        It is also possible to write non-kmer columns to the csv file, for instance, the label or the sequence columns.
        :param output_path: The path of the output csv
        :param non_kmer_columns: The columns that are not kmer counts,
        for instance, the label column
        :param separator: The cell separator to use in the csv
        """
        self.output_path = output_path
        self.kmer_column_indexes: Dict[str, int] = dict()
        self.separator = separator
        self.last_index = 0
        self.non_kmer_columns = non_kmer_columns
        if os.path.exists("./rows.tmp"):
            os.remove("./rows.tmp")

    def write_kmer_count(self, kmers: Dict[str, int], not_kmers: List[str]):
        if len(not_kmers) != len(self.non_kmer_columns):
            raise ValueError(f"Expected {len(self.non_kmer_columns)} non-kmer columns, but got {len(not_kmers)}")
        if not all(kmer in self.kmer_column_indexes for kmer in kmers):
            # Add the new kmers to the column indexes
            for column in [c for c in kmers.keys() if c not in self.kmer_column_indexes]:
                self.kmer_column_indexes[column] = self.last_index
                self.last_index += 1
        with open("rows.tmp", "a") as file:
            # file.write(f"{region_id}{self.separator}{class_topology_fold_clan}{self.separator}{sequence}") old way
            for non_kmer in not_kmers:
                file.write(f"{non_kmer}{self.separator}")
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
        """
        This method has to be called at the very end of the writing process.
        By calling this method, the temporary
        files are used to write the final csv file.
        """
        with open(self.output_path, "w") as file:
            # file.write(f"region_id{self.separator}class_topology_fold_clan{self.separator}sequence") old way
            for non_kmer in self.non_kmer_columns:
                file.write(f"{non_kmer}{self.separator}")
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
                        if cells_count != len(self.kmer_column_indexes) + len(self.non_kmer_columns):
                            # Fill the row with empty cells if the number of cells is less than the expected
                            for _ in range(len(self.kmer_column_indexes) - cells_count + len(self.non_kmer_columns)):
                                file.write(f"{self.separator}")
                        file.write("\n")
        os.remove("rows.tmp")
