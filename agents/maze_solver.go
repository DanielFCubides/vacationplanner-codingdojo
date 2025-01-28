package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

// QueueNode represents a node in the BFS queue
type QueueNode struct {
	pos  Position
	path []Position
}

// MazeSolver contains the maze and solving logic
type MazeSolver struct {
	maze       [][]string
	size       int
	start, end Position
}

// NewMazeSolver creates a new maze solver from a string representation
func NewMazeSolver(maze [][]string) *MazeSolver {
	var start, end Position

	// Find start and end position
	for i, row := range maze {
		for j := range row {
			if maze[i][j] == "S" {
				start = Position{j, i}
			} else if maze[i][j] == "E" {
				end = Position{j, i}
			}
		}

	}

	return &MazeSolver{
		maze:  maze,
		size:  len(maze),
		start: start,
		end:   end,
	}
}

// SolveBFS finds the shortest path using Breadth-First Search
func (ms *MazeSolver) SolveBFS() []Position {
	// Create queue for BFS
	queue := []QueueNode{{pos: ms.start, path: []Position{ms.start}}}

	// Create visited map
	visited := make(map[Position]bool)
	visited[ms.start] = true

	// Define possible movements: right, down, left, up
	directions := []Position{{0, 1}, {1, 0}, {0, -1}, {-1, 0}}

	// BFS loop
	for len(queue) > 0 {
		// Get current position
		current := queue[0]
		queue = queue[1:]

		// Check if we reached the end
		if current.pos == ms.end {
			return current.path
		}

		// Try all possible directions
		for _, dir := range directions {
			newPos := Position{
				x: current.pos.x + dir.x,
				y: current.pos.y + dir.y,
			}

			// Check if the move is valid and position hasn't been visited
			//fmt.Printf("new posible position %d - %d -> IsValid: %t\n", newPos.x, newPos.y, ms.isValidMove(newPos) && !visited[newPos])
			if ms.isValidMove(newPos) && !visited[newPos] {
				// Create new path by appending new position
				newPath := make([]Position, len(current.path))
				copy(newPath, current.path)
				newPath = append(newPath, newPos)

				// Add to queue and mark as visited
				queue = append(queue, QueueNode{pos: newPos, path: newPath})
				visited[newPos] = true
			}
		}
	}

	return nil // No path found
}

// isValidMove checks if a position is within bounds and not a wall
func (ms *MazeSolver) isValidMove(pos Position) bool {
	return pos.x >= 0 && pos.x < ms.size &&
		pos.y >= 0 && pos.y < ms.size &&
		(ms.maze[pos.y][pos.x] == "O" || ms.maze[pos.y][pos.x] == "E")
}

// PrintSolution prints the maze with the solution path
func (ms *MazeSolver) PrintSolution(path []Position) {
	// Create a copy of the maze
	mazeCopy := make([][]string, len(ms.maze))
	for i := range ms.maze {
		mazeCopy[i] = make([]string, len(ms.maze[i]))
		copy(mazeCopy[i], ms.maze[i])
	}

	// Mark the path with '*'
	for _, pos := range path {
		if ms.maze[pos.y][pos.x] != "S" && ms.maze[pos.y][pos.x] != "E" {
			mazeCopy[pos.y][pos.x] = "*"
		}
	}

	// Print the maze
	for _, row := range mazeCopy {
		for _, cell := range row {
			fmt.Printf("%s ", cell)
		}
		fmt.Println()
	}
}

func SolveMaze() {
	// Example maze
	filename := "mazes/Maze1"
	mazeStr := ReadMazeFile(filename)

	// Create and solve maze
	solver := NewMazeSolver(mazeStr)
	solution := solver.SolveBFS()

	// Print results
	if solution != nil {
		fmt.Printf("Solution found! Path length: %d\n\n", len(solution)-1)
		solver.PrintSolution(solution)
	} else {
		fmt.Println("No solution found!")
	}
}

func ReadMazeFile(filename string) [][]string {
	maze_file, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	defer maze_file.Close()

	r := bufio.NewReader(maze_file)
	mazeStr := make([][]string, 0)
	for {
		line, _, err := r.ReadLine()
		if len(line) > 0 {
			row := string(line)
			mazeStr = append(mazeStr, strings.Split(row, " "))
		}
		if err != nil {
			break
		}
	}
	return mazeStr
}
