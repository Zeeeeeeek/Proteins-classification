import itertools
import os
import sqlite3
from typing import List


class SQLKmerCsvWriter:
    def __init__(self, output_path: str, non_kmer_columns: List[str], k: int, separator: str = ","):
        """
        :param output_path: str
        :param non_kmer_columns: List[str]
        :param k: int
        :param separator: str
        """
        if not output_path.endswith(".csv"):
            raise ValueError("Output path should end with '.csv'")
        self.output_path = output_path
        alphabet = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V',
                    'W', 'X', 'Y']
        self.last_index = 0
        if os.path.exists("temp.db"):
            os.remove("temp.db")
        self.conn = sqlite3.connect('temp.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE kmers (kmer TEXT PRIMARY KEY, kmer_index INTEGER)")
        with open(output_path, "w") as file:
            for non_kmer in non_kmer_columns:
                file.write(f"{non_kmer}")
                if non_kmer != non_kmer_columns[-1]:
                    file.write(f"{separator}")
            for i in range(1, k + 1):
                for kmer in itertools.product(alphabet, repeat=i):
                    kmer = "".join(kmer)
                    self.cursor.execute("INSERT INTO kmers VALUES (?, ?)", (kmer, self.last_index))
                    file.write(f"{separator}{kmer}")
                    self.last_index += 1
                self.conn.commit()
            file.write("\n")
        self.separator = separator
        self.non_kmer_columns = non_kmer_columns

    def close(self):
        self.conn.close()
        if os.path.exists("temp.db"):
            os.remove("temp.db")

    def write_kmer_count(self, kmers: dict, not_kmers: List[str]):
        if len(not_kmers) != len(self.non_kmer_columns):
            raise ValueError(f"Expected {len(self.non_kmer_columns)} non-kmer columns, but got {len(not_kmers)}")
        with open(self.output_path, "a") as file:
            for non_kmer in not_kmers:
                file.write(f"{non_kmer}")
                if non_kmer != not_kmers[-1]:
                    file.write(f"{self.separator}")
            ordered_kmers = sorted(kmers, key=lambda x:
            self.cursor.execute("SELECT kmer_index FROM kmers WHERE kmer = ?", (x,)).fetchone()[0])
            expected_index = 0
            for kmer in ordered_kmers:
                index = self.cursor.execute("SELECT kmer_index FROM kmers WHERE kmer = ?", (kmer,)).fetchone()[0]
                while expected_index < index:
                    file.write(f"{self.separator}")
                    expected_index += 1
                file.write(f"{self.separator}{kmers[kmer]}")
                expected_index += 1
            # Write missing separators
            while expected_index < self.last_index:
                file.write(f"{self.separator}")
                expected_index += 1
            file.write("\n")


def main():
    w = SQLKmerCsvWriter("output.csv", ["region_id", "class_topology_fold_clan", "sequence"], 1)
    w.write_kmer_count({"A": 1, "C": 2, "E": 3, "X": 4}, ["id", "class", "seq"])
    w.write_kmer_count({"K": 1, "C": 2, "I": 2, "Y": 9}, ["id", "class", "seq"])
    conn = sqlite3.connect('temp.db')
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM kmers").fetchall()
    print("Length of rows:", len(rows))
    conn.close()
    w.close()


if __name__ == "__main__":
    main()
