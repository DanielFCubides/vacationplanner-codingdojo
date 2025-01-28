package main

import (
	"fmt"
	"math/rand"
	"time"
)

type Position struct {
	x, y int
}

type Maze struct {
	size  int
	grid  [][]rune
	start Position
	end   Position
}

// Create a new maze of given size
func NewMaze(size int) *Maze {
	if size < 5 || size > 20 {
		panic("Maze size must be between 5 and 20")
	}

	m := &Maze{
		size: size,
		grid: make([][]rune, size),
	}

	// Initialize grid with walls
	for i := range m.grid {
		m.grid[i] = make([]rune, size)
		for j := range m.grid[i] {
			m.grid[i][j] = 'X'
		}
	}

	// Set start and end positions
	m.start = Position{1, 1}
	m.end = Position{size - 2, size - 2}

	return m
}

// Get valid neighbors for maze generation
func (m *Maze) getUnvisitedNeighbors(pos Position) []Position {
	directions := []Position{
		{2, 0},  // right
		{-2, 0}, // left
		{0, 2},  // down
		{0, -2}, // up
	}

	var neighbors []Position
	for _, dir := range directions {
		newPos := Position{pos.x + dir.x, pos.y + dir.y}
		if newPos.x > 0 && newPos.x < m.size-1 && newPos.y > 0 && newPos.y < m.size-1 &&
			m.grid[newPos.y][newPos.x] == 'X' {
			neighbors = append(neighbors, newPos)
		}
	}
	return neighbors
}

// Generate the maze using recursive backtracking
func (m *Maze) generate() {
	// Initialize random seed
	rand.NewSource(time.Now().UnixNano())

	// Start with empty path at start position
	m.grid[m.start.y][m.start.x] = 'O'
	m.carveFromPoint(m.start)

	// Set start and end markers
	m.grid[m.start.y][m.start.x] = 'S'
	m.grid[m.end.y][m.end.x] = 'E'

	// Add some random additional paths for multiple solutions
	//m.addExtraPaths()
}

// Recursive function to carve paths
func (m *Maze) carveFromPoint(pos Position) {
	neighbors := m.getUnvisitedNeighbors(pos)
	rand.Shuffle(len(neighbors), func(i, j int) {
		neighbors[i], neighbors[j] = neighbors[j], neighbors[i]
	})

	for _, neighbor := range neighbors {
		if m.grid[neighbor.y][neighbor.x] == 'X' {
			// Carve path between current position and neighbor
			m.grid[neighbor.y][neighbor.x] = 'O'
			m.grid[pos.y+((neighbor.y-pos.y)/2)][pos.x+((neighbor.x-pos.x)/2)] = 'O'
			m.carveFromPoint(neighbor)
		}
	}
}

// Add extra paths to create multiple solutions
func (m *Maze) addExtraPaths() {
	numExtraPaths := m.size / 3
	for i := 0; i < numExtraPaths; i++ {
		// Try to break some walls to create additional paths
		x := rand.Intn(m.size-2) + 1
		y := rand.Intn(m.size-2) + 1

		if m.grid[y][x] == 'X' &&
			(m.grid[y-1][x] == 'O' || m.grid[y+1][x] == 'O') &&
			(m.grid[y][x-1] == 'O' || m.grid[y][x+1] == 'O') {
			m.grid[y][x] = 'O'
		}
	}
}

// Print the maze
func (m *Maze) Print() {
	for _, row := range m.grid {
		for _, cell := range row {
			fmt.Printf("%c ", cell)
		}
		fmt.Println()
	}
}

// Check if maze is solvable
func (m *Maze) isSolvable() bool {
	visited := make([][]bool, m.size)
	for i := range visited {
		visited[i] = make([]bool, m.size)
	}
	return m.dfs(m.start, visited)
}

// Depth-first search to check if end is reachable
func (m *Maze) dfs(pos Position, visited [][]bool) bool {
	if pos == m.end {
		return true
	}

	visited[pos.y][pos.x] = true
	directions := []Position{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}

	for _, dir := range directions {
		newPos := Position{pos.x + dir.x, pos.y + dir.y}
		if newPos.x >= 0 && newPos.x < m.size && newPos.y >= 0 && newPos.y < m.size &&
			!visited[newPos.y][newPos.x] &&
			(m.grid[newPos.y][newPos.x] == 'O' || m.grid[newPos.y][newPos.x] == 'E') {
			if m.dfs(newPos, visited) {
				return true
			}
		}
	}
	return false
}
