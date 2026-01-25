# Student Team Assignment from Preferences

This repository contains a Python program for forming student teams based on pairwise preferences.
Students may indicate whom they would like to work with (“green”) and whom they would prefer not to work with (“red”).
The program computes team assignments that respect all negative constraints while maximizing overall satisfaction.

In addition to computing teams, the program provides both textual and graphical visualizations of the preference structure.

---

## Features

- Reads student preferences from a delimited text file
- Supports **green** (preferred) and **red** (avoid) preferences
- Represents preferences as a directed graph
- Builds an undirected compatibility graph with weighted edges
- Computes an optimal pairing using **maximum-weight matching**
- Guarantees that **no red-edge pairs** are formed
- Produces:
  - colorized terminal output for team assignments
  - Graphviz-based visualization of preferences (optionally anonymized)

---

## Input File Format

The input file is a delimited text file (TSV by default, though this is configurable).

### Delimiter (important)

Although the default filename is `preferences.csv`, the program currently expects a **tab-separated** file:

```python
DELIMITER = "\t"
```

If your input file is comma-separated instead, you can switch to:

```python
DELIMITER = ","
```

No other changes are required.

---

### Header Row

- The first row is a header.
- Columns containing the substring **`green`** indicate students the row student *wants* to work with.
- Columns containing the substring **`red`** indicate students the row student *does not want* to work with.

Column names beyond this convention are ignored.

---

### Data Rows

Each subsequent row corresponds to one student:

- **Column 0**: the student identifier
- **Column i**: another student identifier (optional / may be blank)

Blank cells are ignored.

---

### Example Input (TSV)

```text
student	green_1	green_2	red_1
Alice	Bob	Charlie	
Bob		Alice	David
Charlie	Alice		
David			Bob
```

Interpretation:
- Alice wants to work with Bob and Charlie
- Bob wants to work with Alice and does not want to work with David
- David does not want to work with Bob

---

## How Teaming Works

1. **Preferences are parsed** into a nested dictionary:

   ```python
   pref[A][B] = True   # A wants to work with B
   pref[A][B] = False  # A does not want to work with B
   ```

2. An **undirected compatibility graph** is constructed:
   - No edge is added if either student has a red preference against the other.
   - Edge weights reflect positive preferences:
     - `0.0` – no green preferences
     - `1.0` – one-sided green preference
     - `1.5` – mutual green preference (intentionally capped)

3. A **maximum-weight matching** is computed using NetworkX:
   - Primary objective: maximize total satisfaction
   - Secondary objective: maximize the number of pairs
     (`maxcardinality=True`)

4. If the number of students is odd, one student may remain unmatched.
   Unmatched students are reported explicitly.

---

## Output

### Terminal Output

- Each team is printed on its own line.
- Student names are colorized (in supported terminals):
  - **Green**: student wants to work with their partner
  - **Red**: student explicitly does not want to work with their partner
  - Default color: no stated preference

---

### Graphical Visualization

The program generates a **directed preference graph** using Graphviz:

- Nodes represent students
- Green arrows represent “wants to work with”
- Red arrows represent “does not want to work with”
- Optional anonymization replaces names with `S01`, `S02`, …

The visualization is saved as a PNG file and automatically opened.

---

## Requirements

- Python 3.10+
- `networkx`
- `graphviz` (system installation)
- Python Graphviz bindings:
  - `graphviz`
- Optional (for colored terminal output):
  - `colorama`

Install Python dependencies:

```bash
pip install networkx graphviz colorama
```

Install Graphviz system-wide:

```bash
# macOS (Homebrew)
brew install graphviz

# Ubuntu / Debian
sudo apt install graphviz
```

---

## Running the Program

```bash
python team_builder.py
```

By default, the program:
- reads `preferences.csv`
- prints team assignments to the terminal
- generates and opens a preference visualization

---

## Customization

Common adjustments include:

- Changing the input delimiter (`DELIMITER`)
- Renaming the input file (`INPUT_FILE`)
- Choosing a different Graphviz layout engine:
  - `dot`, `neato`, `fdp`, `sfdp`, `circo`, `twopi`
- Enabling or disabling anonymization in the visualization
- Modifying the edge-weight scheme

---

## Design Notes

- Red preferences are treated as **hard constraints**
- Green preferences contribute to edge weights
- Mutual green preferences are intentionally capped to prevent a single mutual pair from dominating multiple one-sided satisfactions elsewhere
- Output paths are anchored to the script directory when run as a file, and fall back to the current working directory in interactive sessions (e.g., Emacs inferior Python)

---

## License

This project is intended for educational and academic use.
No license is specified; add one if you plan to distribute or reuse the code broadly.

---

## Author

**Waqar Saleem**  
Associate Professor of Computer Science  
Contact: wsaleem@gmail.com
