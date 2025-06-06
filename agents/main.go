package main

import "fmt"

func main() {
	fmt.Println("Hello Maze")

	// Here we are calling out maze solver to solve a maze
	SolveMaze()

}

func CreateMaze() *Maze {
	size := 19
	maze := NewMaze(size)

	// Generate the maze
	maze.generate()

	// Ensure maze is solvable, regenerate if not
	for !maze.isSolvable() {
		maze = NewMaze(size)
		maze.generate()
	}
	return maze
}
