#!/usr/bin/env python3

import time
from bs4 import BeautifulSoup
import math

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import tempfile
import shutil

class ZipSolver:

    def __init__(self, url: str = "https://www.linkedin.com/games/view/zip/desktop", 
    browser:str = "chrome", headless:bool = False):
        
        self.browser = browser.lower()
        self.headless = headless
        self.url = url
        
        self.driver = self._init_driver()

        self.grid = {}
        self.size = None
        self.path = []
        self.cell_elements = {}
        self.max_number = None

    def _init_driver(self):
        """Setup driver based on passed driver. """
        self.temp_profile_dir = None  # track temporary profile folder for cleanup

        if self.browser == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            # fresh temporary profile
            self.temp_profile_dir = tempfile.mkdtemp()
            options.add_argument(f"--user-data-dir={self.temp_profile_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=options)

        elif self.browser == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            # fresh temporary profile
            self.temp_profile_dir = tempfile.mkdtemp()

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

        
            driver = webdriver.Firefox( options=options)

        elif self.browser == "safari":
            if self.headless:
                print("Safari does not support headless mode. Running visible.")
            options = webdriver.SafariOptions()
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Safari(options = options)

        elif self.browser == "edge":
            options = webdriver.EdgeOptions()

            if self.headless:
                options.add_argument("--headless=new")
            else:
                options.add_argument("--start-maximized")
            # fresh temporary profile
            self.temp_profile_dir = tempfile.mkdtemp()
            options.add_argument(f"--user-data-dir={self.temp_profile_dir}")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Edge(options=options)

        else:
            raise ValueError(f"Unsupported browser: {self.browser}")

        return driver

    def navigate_and_wait(self):
        """Navigate to the game and wait for it to load"""
        print("Navigating to game...")
        self.driver.get(self.url)
        
        # Wait for the game to load
        element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "trail-cell"))
        )
        print("Game loaded successfully")

    def get_grid(self):
        """Extract grid information from the page"""
        print("Extracting grid data...")
        
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        cells = soup.find_all("div", class_="trail-cell")

        if not cells:
            raise Exception("No trail cells found. Game may not have loaded properly.")

        grid_shape = int(math.sqrt(len(cells))) # calculate shape of grid

        # Create dictionary with coordinate as key, and value as (number, [walls])
        grid = {}
        cell_elements = {}
        i, j = 0, 0
        
        for cell in cells:
            idx = int(cell.get("data-cell-idx"))

            # Check if value, else None
            content_div = cell.find("div", class_="trail-cell-content")
            value = content_div.get_text(strip=True) if content_div else None

            # Add walls
            wall_divs = cell.find_all("div", class_="trail-cell-wall")
            walls = []
            for w in wall_divs:
                if "trail-cell-wall--left" in w["class"]:
                    walls.append("left")
                if "trail-cell-wall--right" in w["class"]:
                    walls.append("right")
                if "trail-cell-wall--up" in w["class"]:
                    walls.append("top")
                if "trail-cell-wall--down" in w["class"]:
                    walls.append("bottom")
                    
            grid[(i, j)] = (value, walls)
            
            # Store reference to actual web element for clicking later
            web_element = self.driver.find_element(By.CSS_SELECTOR, f"div.trail-cell[data-cell-idx='{idx}']")
            cell_elements[(i, j)] = web_element
            
            if j + 1 == grid_shape:
                i += 1
                j = 0
            else:
                j += 1

        self.grid = grid
        self.size = grid_shape
        self.cell_elements = cell_elements
        print(f"Grid extracted: {grid_shape}x{grid_shape}")

    def neighbors(self, coord):
        """Get all possible moves from a coordinate"""
        r, c = coord
        moves = []
        value, walls = self.grid[coord]
        
        # Check each direction (and the walls in that direction)
        directions = [
            (-1, 0, "top", "bottom"),  # up
            (1, 0, "bottom", "top"),   # down
            (0, -1, "left", "right"),  # left
            (0, 1, "right", "left")    # right
        ]
        
        for dr, dc, wall_from, wall_to in directions:
            new_r, new_c = r + dr, c + dc
            
            # Check bounds of board
            if 0 <= new_r < self.size and 0 <= new_c < self.size:
                # Check if current cell has wall blocking direction
                if wall_from not in walls:
                    # Double check if target cell has wall blocking entry
                    _, target_walls = self.grid[(new_r, new_c)]
                    # Legal move => append as possible moves
                    if wall_to not in target_walls:
                        moves.append((new_r, new_c))
        
        return moves

    def solve(self, coord, current_target, visited=None, path=None):
        """Simple recursive backtracking algorithm"""
        if visited is None:
            visited = set()
        if path is None:
            path = []

        # Current value
        value, _ = self.grid[coord]
        
        # Convert to int, or None
        cell_value = int(value) if value is not None else None
        
        # Add current position to path and visited
        new_path = path + [coord]
        visited.add(coord)

        new_target = current_target
        if cell_value is not None:
            # Currently in a correct numbered cell => update target cell
            if cell_value == current_target:
                new_target = current_target + 1
            else:
                # Can't hit this number yet => not a valid path
                visited.remove(coord)
                return None
        
        # Hit everything on the board
        if len(new_path) == self.size * self.size:
            # Finished the game
            if new_target > self.max_number:
                self.path = new_path
                visited.remove(coord)
                return new_path
            # Something is wrong, path invalid
            else:
                visited.remove(coord)
                return None
        
        # Explore all possible moves
        for next_coord in self.neighbors(coord):
            # Not already visited
            if next_coord not in visited:
                result = self.solve(next_coord, new_target, visited, new_path)
                # Valid result
                if result is not None:
                    visited.remove(coord)
                    return result
        
        visited.remove(coord)
        return None

    def print_solution(self):
        """Print the solution path"""
        step_grid = {}
        for i, coord in enumerate(self.path):
            step_grid[coord] = i + 1
        
        print("\nSolution path:")
        for r in range(self.size):
            for c in range(self.size):
                step = step_grid.get((r, c), 0)
                value, _ = self.grid[(r, c)]
                if value is not None:
                    print(f"[{step:2}]", end=" ")  # Numbered cells in brackets
                else:
                    print(f" {step:2} ", end=" ")   # Empty cells
            print()

    def start_game(self):
        """Start the game by clicking the start button"""
        print("Starting game...")
        
        # Wait for start button and click it
        try:
            start_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "launch-footer-start-button"))
            )
            start_button.click()
            print("Start button clicked")
            
            # Wait for the first cell to be visible (game started)
            first_cell = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.trail-cell[data-cell-idx='0']"))
            )
            print("Game started successfully")
            
        except Exception as e:
            print(f"Error starting game: {e}")
            raise

    def execute_solution(self):
        """Execute the solution using Selenium ActionChains"""
        print("Executing solution...")
        
        if not self.path:
            print("No solution path available")
            return
            
        try:
            dir_map = {
                (-1, 0): Keys.ARROW_UP,
                (1, 0): Keys.ARROW_DOWN,
                (0, -1): Keys.ARROW_LEFT,
                (0, 1): Keys.ARROW_RIGHT,
            }

            # Compute directions from path
            directions = []
            for (r1, c1), (r2, c2) in zip(self.path, self.path[1:]):
                dr, dc = r2 - r1, c2 - c1
                directions.append(dir_map[(dr, dc)])

            # click first cell (start outputting solution) 
            first_cell = self.cell_elements[self.path[0]]
            first_cell.click()

            # go through solution by using the arrow keys 
            body = self.driver.find_element(By.TAG_NAME, "body")
            for key in directions:
                body.send_keys(key)
            
            print("Solution executed successfully!")
            time.sleep(5)  # Wait to see results
            
        except Exception as e:
            print(f"Error executing solution: {e}")
            raise

    def run(self):
        """Main execution method"""
        try:
            print("Step 1: Navigating to game")
            self.navigate_and_wait()

            print("Step 2: Extracting grid data")
            self.get_grid()

            print("Step 3: Finding solution")
            # Find starting position (cell with "1")
            start = next(key for key, val in self.grid.items() if val[0] == "1")
            self.max_number = max(int(val[0]) for key, val in self.grid.items() if val[0] is not None)
            
            print(f"Starting at {start}, max number: {self.max_number}")
            
            solution = self.solve(start, 1)  # Start looking for "2" next
            
            if solution:
                print("Solution found!")
                self.print_solution()
            else:
                print("No solution exists")
                return

            print("Step 4: Starting game")
            self.start_game()

            print("Step 5: Executing solution")
            self.execute_solution()
            
            print("Puzzle solved successfully!")
            
        except Exception as e:
            print(f"Error during execution: {e}")
            raise
        finally:
            print("Closing browser...")
            self.driver.quit()
            if hasattr(self, "temp_profile_dir") and self.temp_profile_dir:
                shutil.rmtree(self.temp_profile_dir, ignore_errors=True)