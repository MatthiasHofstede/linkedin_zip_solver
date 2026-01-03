# LinkedIn Zip Game Solver

An automated solver for the LinkedIn Zip puzzle game using Selenium WebDriver and a recursive backtracking algorithm.

## Overview

This tool automatically solves the LinkedIn Zip puzzle by:
1. Navigating to the game page
2. Extracting the grid layout and constraints
3. Finding a valid path through all cells
4. Automating the solution playback

## Requirements

```bash
pip install selenium beautifulsoup4
```

The program can run on four browsers:
- **Chrome**
- **Firefox**
- **Safari**
- **Edge**

## Installation

```bash
git clone [<repository-url>](https://github.com/MatthiasHofstede/linkedin_zip_solver)
cd linkedin_zip_solver
pip install -e . 
```

## Usage

### Basic Usage

```bash
python main.py
```

### Command Line Arguments

```bash
python main.py --browser chrome --headless True
```

**Arguments:**
- `--browser`: Browser to use (default: `safari`)
  - Options: `chrome`, `firefox`, `safari`, `edge`
- `--headless`: Run in headless mode (default: `True`)
  - Options: `True`, `False`
  - Note: Safari doesn't support headless mode

### Examples

**Run with Chrome in visible mode:**
```bash
python main.py --browser chrome --headless False
```

**Run with Firefox in headless mode:**
```bash
python main.py --browser firefox --headless True
```

**Run with Safari (visible only):**
```bash
python main.py --browser safari
```

**Run with Edge in headless mode:**
```bash
python main.py --browser edge --headless True
```

## How It Works

1. **Grid Extraction**: Parses the HTML to extract cell positions, numbers, and wall constraints
2. **Path Finding**: Uses recursive backtracking to find a valid path that:
   - Visits all cells exactly once
   - Hits numbered cells in sequential order (1, 2, 3, ...)
   - Respects wall boundaries between cells
3. **Solution Execution**: Simulates keyboard arrow keys to execute the solution in the browser 

## Code Structure

```
.
├── main.py                 # Entry point
└── src/
    └── linkedin_zip.py    # Main solver class
```

## Output Example

```
Step 1: Navigating to game
Game loaded successfully
Step 2: Extracting grid data
Grid extracted: 5x5
Step 3: Finding solution
Starting at (0, 0), max number: 5
Solution found!

Solution path:
[ 1]  2   3   4  [ 5] 
[ 6]  7   8   9  [10] 
[11] 12  13  14  [15] 
[16] 17  18  19  [20] 
[21] 22  23  24  [25] 

Step 4: Starting game
Step 5: Executing solution
Solution executed successfully!
Puzzle solved successfully!
```

## Disclaimer

This tool is for educational purposes only. Please respect LinkedIn's Terms of Service and use responsibly.
