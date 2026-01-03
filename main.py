#!/usr/bin/env python3

import argparse
from src.LinkedinZip import ZipSolver 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Linkedin Game Solver')
    parser.add_argument('--headless', type=str, default="True", help="Whether to run headless")
    parser.add_argument('--browser', type = str, default = "safari", help = "what browser to run in " )
    args = parser.parse_args()

    url ="https://www.linkedin.com/games/view/zip/desktop"     
    
    headless = True if args.headless == "True" else False
    game = ZipSolver(url, browser = args.browser, headless = headless)
    game.run()
    