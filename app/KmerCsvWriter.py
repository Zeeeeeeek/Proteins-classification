from typing import Dict, List
import os
import itertools


class KmerCsvWriter:
    def __init__(self, output_path: str, non_kmer_columns: List[str], k: int, separator: str = ","):
        """
        This class is used to write kmer counts to a csv file.
        By using this class, the kmer counts are written to the
        csv file in the correct order, and the columns are added dynamically as new kmers are encountered.
        It is also possible to write non-kmer columns to the csv file, for instance, the label or the sequence columns.
        :param output_path: The path of the output csv
        :param non_kmer_columns: The columns that are not kmer counts,
        for instance, the label column
        :param separator: The cell separator to use in the csv
        :param k: The kmer length
        """
        self.output_path = output_path
        self.kmer_column_indexes: Dict[str, int] = dict()
        alphabet = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                    'W', 'X', 'Y']
        last_index = 0
        for i in range(1, k + 1):
            for kmer in itertools.product(alphabet, repeat=i):
                kmer = "".join(kmer)
                self.kmer_column_indexes[kmer] = last_index
                last_index += 1
        self.separator = separator
        self.non_kmer_columns = non_kmer_columns
        if os.path.exists("./rows.tmp"):
            os.remove("./rows.tmp")

    def write_kmer_count(self, kmers: Dict[str, int], not_kmers: List[str]):
        if len(not_kmers) != len(self.non_kmer_columns):
            raise ValueError(f"Expected {len(self.non_kmer_columns)} non-kmer columns, but got {len(not_kmers)}")
        with open("rows.tmp", "a") as file:
            for non_kmer in not_kmers:
                file.write(f"{non_kmer}")
                if non_kmer != not_kmers[-1]:
                    file.write(f"{self.separator}")
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

    def close(self):
        """
        This method has to be called at the very end of the writing process.
        By calling this method, the temporary
        files are used to write the final csv file.
        """
        with open(self.output_path, "w") as file:
            for non_kmer in self.non_kmer_columns:
                file.write(f"{non_kmer}")
                if non_kmer != self.non_kmer_columns[-1]:
                    file.write(f"{self.separator}")
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
