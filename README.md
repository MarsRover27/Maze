# Maze Generator
## Description
This project is a console-based 2D maze generator. The program generates a maze represented as a 2D matrix with guaranteed playability and optional gameplay elements such as traps and treasure. The maze always contains:
* exactly one entrance;
* exactly one exit;
* at least one valid path from entrance to exit.
  
Optional elements are added only if they do not break the rules.

## Cell types
Each cell in the maze belongs to one of the following types:

|     Type      |  Description  |  Designation  |
| ------------- | ------------- | ------------- |
|Wall|Impassable cell|█|
|Road|Passable cell| | 
|Entrance|Starting point, always on the outer border|S| 
|Exit|Ending point, always on the outer border|E| 
|Trap (optional)|Passable cell, but stepping on 3 traps kills the player (0–5 per level)|T| 
|Treasure (optional)|Passable cell with treasure (0–1 per level)|G| 

## How to Run
Requirements
* Python 3.8+
* colorama (for colored output)
  
Check if Python is installed:
```bash
python --version
```
✔ If version 3.8 or higher, you're all set.</br>
❌ If there's no command, install Python from the [official website](https://www.python.org/downloads/)
> [!WARNING]
> When installing on Windows, be sure to check the “Add Python to PATH” box.

Download the project:
```bash
git clone https://github.com/MarsRover23/Maze.git
cd Maze
```
Install dependencies:
```bash
pip install colorama
```
Basic usage:
```bash
python main.py HEIGHT WIDTH
```
Example:
```bash
python main.py 21 41
```
## Command-Line Options
| Option  | Description |
| ------------- | ------------- |
| --seed N  | Use a fixed random seed (reproducible mazes)  |
| --numbers | Output maze as numbers instead of symbols |
|--no-color| Disable colored output |
| --no-traps | Disable trap generation |
| --no-treasure | Disable treasure generation |

## Numeric Representation
When using --numbers, the maze is printed as a matrix of integers:
|Number|Cell Type|
| ------------- | ------------- |
| 0 |Wall| 
| 1 | 	Road| 
| 2| 	Entrance| 
| 3| 	Exit| 
| 4| Trap| 
| 5| 	Treasure| 

This format is suitable for:
* game engines
* file storage
* automated testing
  
## Algorithm Explanation
### Maze Generation
The maze is generated using an iterative depth-first search (DFS), also known as the recursive backtracker algorithm:
1. The maze is initialized as a grid of walls.
2. Logical cells are placed at odd coordinates.
3. DFS visits each cell exactly once and carves passages between them.
4. This guarantees a connected and acyclic maze (perfect maze).

### Entrance & Exit Placement
* Valid border positions adjacent to roads are collected.
* Two distant points are selected using BFS to maximize path length.
* Entrance and exit are placed on the outer border.

### Traps
* Between 0 and 5 traps are placed on road cells.
* After each placement, a BFS is performed that tracks how many traps were used.
* A trap is accepted only if a path to the exit with ≤2 traps still exists.

### Treasure
* At most 1 treasure is placed.
* It is placed only on a road cell.
* A BFS ensures the treasure is reachable from the entrance without exceeding trap limits.
  
If no valid placement is possible, the treasure is simply not placed.

## Time and Space Complexity
Let H × W be the maze size.
|Operation	|Complexity|
| ------------- | ------------- |
|Maze generation (DFS)|	O(H·W)|
|Path validation (BFS)|	O(H·W)|
|Trap & treasure placement|O(H·W) (bounded attempts)|

### Overall complexity
* Time: O(H·W)
* Space: O(H·W)

This makes the algorithm efficient and scalable for large mazes.

A total of 3-5 hours were spent on development.
