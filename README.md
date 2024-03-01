# Protein classification 
A protein classification tool. Retrieves protein sequences from RepeatsDB, collects their sequences and stores them in a 
csv file. Then, perform k-mer counting and use the k-mer counts to train a Machine Learning model to classify the 
proteins.
## Installation
```bash
git clone https://github.com/Zeeeeeeek/Proteins-classification.git
cd Proteins-classification
pip install -r requirements.txt
```
## Command line usage
```bash
python main.py -c
```
Running the command above will start a Command Line Interface (CLI). Follow the possible commands.
### Query
```
query <query_classes> [-o --output] [-m --merge_regions] [-t --threads]
```
Performs a query using RepeatsDB API storing all the proteins and their sequences in a csv file.

#### Parameters:
- `query_classes`: Query string for the RepeatsDB API. Accepts one or more of the following options: '2', '3', '4', '5'.
- `-o, --output`: Output file name (default: 'output').
- `-m, --merge_regions`: Merge units in regions (default: false).
- `-t, --threads`: Number of threads (default: 5).

#### Example:
```
query 2 3 4 5 -o proteins -m -t 10
```

### Kmer counting
```
kmer <input_file> <kmer_size> [-o OUTPUT] [-t THREADS]
```
Performs k-mer counting on the input file and stores the results in a csv file.

#### Parameters:
- `input_file`: Input file name.
- `kmer_size`: Size of the k-mer. Must be an integer greater than 0.
- `-o, --output`: Output file name (default: 'input_file_name'_'specified_k'_mer).

#### Example:
```
kmer proteins.csv 3 -o kmer_counts
```

### Model training
```
models <input_file> <level> <method> <max_sample_size_per_level> [-r --random_state]
```
Trains Machine Learning models using the input file and prints the results.

#### Parameters:
- `input_file`: Input file name.
- `level`: Level of the classification. Options are: 'class', 'topology', 'fold', 'clan'.
- `method`: Method to use. Options are: classifiers, clustering.
- `k`: Size of the k-mer. Must be an integer greater than 0.
- `max_sample_size_per_level`: Maximum sample size per level. Must be an integer greater than 0.
- `-r, --random_state`: Random state for the models and samples (default: 42).

#### Example:
```
models kmer_counts.csv fold classifiers 30 -r 42
```

### Exit
```
exit
```
Exits the CLI.

### Command queue
Cli commands can be chained together with `&&`, the CLI will execute them in the order they were inputted.

#### Example:
```
query 2 3 -o p -m && kmer p 3 && models p_3_mer fold classifiers 10 -r 42 && exit
```


## GUI usage
```bash
python main.py
```
Running the command above will start a Graphical User Interface (GUI).
All the commands available in the CLI are also available in the GUI with the same parameters.