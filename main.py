import random as ran
import numpy as np
import copy
import time

# returns true if the puzzle is solved
def isGoal(board):
    # check for empty cells
    for row in board:
        for elt in row:
            if elt == 0:
                return False
        
    # check for row or column violations
    for i in range(9):
        col = ([k[0 + i:1 + i][0]
                for k in board[0:9]])
        row = board[i]
            
        if len(set(col)) < len(col) or len(set(row)) < len(row):
            return False
        
    # check for quadrant violations
    for i in range(3):
        for j in range(3):
            quad = getQuadrant([i * 3, j * 3], board)
            quad = sum(quad, [])
                
            if len(set(quad)) < len(quad):
                print("quad")
                return False
        
    return True
    
# takes a cell and retuns a list containing the positions of the cells in the quadrant
def getQuadrantPositions(pos):
    x = pos[0] % 3; y = pos[1] % 3
    output = []
    for i in range(0 - y + pos[1], 3 - y + pos[1]):
        for j in range(0 - x + pos[0], 3 - x + pos[0]):
            output.append((j,i))
    return output
    
# takes a cell and the board and returns the 3x3 grid the cell is in as a 2D list
def getQuadrant(pos, lst):
    x = pos[0] % 3; y = pos[1] % 3
    return [k[0 - y + pos[1]:3 - y + pos[1]] for k in lst[0 - x + pos[0]:3 - x + pos[0]]]

# returns a 9x9 list containing a list of candidates for each space on the board
# filled spaces will contain -1
# spaces with no candidates will contain an empty list
def getBoardCandidates(board):
    # create a 9x9 array to store the number of candidates for each variable
    candidates = [[-1 for i in range(9)] for j in range(9)]
    
    # search through the board and find the number of candidates for each variable
    for i in range(9):
        for j in range(9):
            # only search empty cells
            if board[i][j] == 0:
                domain = []
                for k in range(1, 10):
                    if (isValidVariable(k, i, j, board)): domain.append(k)
                        
                candidates[i][j] = domain
    return candidates

# checks if a given value is valid at a certain place on the board    
def isValidVariable(value, row, column, board):
    # check the row and column
    for i in range(9):
        if board[row][i] == value or board[i][column] == value:
            return False
    
    # check the quadrant
    quadrant = sum(getQuadrant([row, column], board), [])
    for elt in quadrant:
        if elt == value:
            return False     
    
    return True

# checks if a state may have a solution
def isValidState(state):
    stateCandidates = getBoardCandidates(state)    
    
    # check if all cells have > 0 candidates
    for candidatesRow in stateCandidates:
        for elt in candidatesRow:
            if elt == []:
                return False
            
    # check if each row, col and quad have at least 1 of each value in their candidates / actual values
    # check the rows and cols
    for i in range(9):
        setRow = set()
        setCol = set()
        
        row = state[i]
        col = [k[0 + i:1 + i][0] for k in state[0:9]]
        
        # if a cell isn't empty push it's value to the set, if it is empty, add its canddiates
        for j in range(9):
            valRow = row[j]
            valCol = col[j]
            
            # add the elements to the set
            if valRow != 0:
                setRow.add(valRow)
            else:
                for candidate in stateCandidates[i][j]:
                    setRow.add(candidate)                    
            if valCol != 0:
                setCol.add(valCol)
            else:
                for candidate in stateCandidates[j][i]:
                    setCol.add(candidate)
        
        # check if the values 1-9 are contained in the set
        if len(setRow) != 9:
            return False
        if len(setCol) != 9:
            return False
    
    # check the quads
    for i in range(3):
        for j in range(3):
            setQuad = set()            
            quadPos = getQuadrantPositions([i * 3, j * 3])
            
            # if a cell isn't empty push it's value to the set, if it is empty, add its canddiates
            for pos in quadPos:
                valQuad = state[pos[0]][pos[1]]

                if valQuad != 0:
                    setQuad.add(valQuad)
                else :
                    for candidate in stateCandidates[pos[0]][pos[1]]:
                        setQuad.add(candidate)
                        
            # check if the values 1-9 are contained in the set              
            if len(setQuad) != 9:
                return False
    
    return True

# returns a list containing the positions of all the singletons and their value
def getSingletons(board):
    singletons = []
    
    # check the candidates of each cell
    candidates = getBoardCandidates(board)
    for i in range(9):
        for j in range(9):
            candidateList = candidates[i][j]
            
            # ignore already filled spaces
            if candidateList == -1:
                continue
            if len(candidateList) == 1:
                singletons.append([[i,j], candidateList[0]])
    return singletons

# fills in all the variables that only have 1 candidate
def fillSingletons(currentState):
    singletons = getSingletons(currentState)
    changes = False

    while len(singletons) > 0:
        changes = True
        singleton = singletons.pop()
        value = singleton[1]
        currentState[singleton[0][0]][singleton[0][1]] = value

        # check for more singletons
        singletons = getSingletons(currentState)
        
    return currentState, changes

# assign all the variables that have a unique candidate for their row, col and quad
def fillUniqueCandidates(board):
    changes = False
    candidates = getBoardCandidates(board)    
    
    # check for unique candidates in each row
    for value in range(1,10):
        for i in range(9):
            countRow = 0
            indexRow = 0
            
            for j in range(9):
                variableCandidatesRow = candidates[i][j]
                
                # ignore filled in rows
                if variableCandidatesRow != -1 and value in variableCandidatesRow:
                    countRow += 1
                    indexRow = [i,j]
                    
                # if there is already more than 1, move onto the next row
                if countRow > 1:
                    break
            
            # if there is only one candidate, assign the variable
            if countRow == 1:
                board[indexRow[0]][indexRow[1]] = value
                changes = True
        
    # check for unique candidates in each col
    for value in range(1,10):
        for i in range(9):
            countCol = 0
            indexCol = 0

            for j in range(9):
                variableCandidatesCol = candidates[j][i]

                # ignore filled in cols
                if variableCandidatesCol != -1 and value in variableCandidatesCol:
                    countCol += 1
                    indexCol = [j,i]
                
                # if there is already more than 1, move onto the next col
                if countCol > 1:
                    break
            
            # if there is only one candidate, assign the variable
            if countCol == 1:
                board[indexCol[0]][indexCol[1]] = value
                changes = True
                
    return board, False
    
    # check for unique candidates in each quadrant
    for val in range(1, 10):
        for i in range(3):
            for j in range(3):
                positions = getQuadrantPositions([i * 3, j * 3])
                count = 0
                index = 0

                # check each position in the quad
                for pos in positions:
                    if candidates[pos[0]][pos[1]] != - 1 and val in candidates[pos[0]][pos[1]]:
                        count += 1
                        index = [pos[0],pos[1]]
                    
                    # if there is already more than 1, move onto the next quad
                    if count > 1:
                        break

                # if the candidate is unique, assign the variable
                if count == 1:
                    board[index[0]][index[1]] = val
                    changes = True
    
    return board, changes
                
# test a single sudoku
def testSingle(difficulty, num = ran.randint(0, 14)):    
    # load the sudoku and the answer
    sudoku = np.load("data/" +  difficulty + "_puzzle.npy")[num]
    sudokuAnswer = np.load("data/" +  difficulty + "_solution.npy")[num]

    # time the solve
    start = time.perf_counter()
    solution = sudoku_solver(sudoku)
    end = time.perf_counter()

    # output the result
    if np.array_equal(solution, sudokuAnswer): print(num, "Correct in", end-start, "seconds")
    else: print(num, "Incorrect, solution isn't \n", np.array(solution), "\nwhich you put lol \nIt took", end-start)

# gives data about the time taken for the algorithm to solve given sudokus
def performanceTest(difficulties, loops = 1):
    print("running testing script")

    for difficulty in difficulties:
        # load the sudokus
        sudokus = np.load("data/" + difficulty + "_puzzle.npy")
        sudokuAnswers = np.load("data/" + difficulty + "_solution.npy")
        averageTime = 0

        # solve each sudoku a number of times
        # suggestion: the higher loops is the faster the sudoku is?
        for iterations in range(loops):
            for num in range(15):
                sudoku = sudokus[num]
                
                # time the solve
                start = time.perf_counter()
                sudokuAnswer = sudoku_solver(sudoku)
                end = time.perf_counter()
                
                # check solution is correct
                sudokuAnswer = sudokuAnswer.tolist()
                if np.array_equal(sudokuAnswer, sudokuAnswers[num]): averageTime += end - start
                else: print("wrong")
        print("Average time to solve", difficulty, "was", averageTime / (loops * 15))
    print("testing finished")
        
# finds which variable would be optimal to change using MRV
def selectVariableToChange(board):    
    lowestValue = 10
    lowestPosition = []
    for i in range(9):
        for j in range(9):
            # ignore filled in spaces
            if board[i][j] != 0:
                continue
            
            candidates = getVariableCandidates(board, [i,j])
            numberOfCandidates = len(candidates)
            if numberOfCandidates < lowestValue:
                lowestValue = numberOfCandidates
                lowestPosition = [i,j]
            if numberOfCandidates == 2:
                return lowestPosition
                
    return lowestPosition

# returns the candidate for a single variable
def getVariableCandidates(board, position):
    if board[position[0]][position[1]] == 0:
        candidates = []
        for val in range(1, 10):
            if (isValidVariable(val, position[0], position[1], board)):
                candidates.append(val)
        return candidates
    else: return -1

# performs a depth-first search recursively
def recursiveDFS(state):
    # fill in singletons and unique values
    singletonChanges = True
    uniqueChanges = True
    while (singletonChanges or uniqueChanges):
        state, uniqueChanges = fillUniqueCandidates(state)
        state, singletonChanges = fillSingletons(state)
        
    # check for final states
    if isGoal(state): 
        return state
    elif not isValidState(state):
        return None
    
    # select the optimal variable to change
    variablePosition = selectVariableToChange(state)
    candidates = getVariableCandidates(state, variablePosition)
    ran.shuffle(candidates)
    
    # traverse the search tree
    for candidate in candidates:
        # assign the new variable
        newState = copy.deepcopy(state)
        newState[variablePosition[0]][variablePosition[1]] = candidate
                                  
        # check for final states
        if isGoal(newState):
            return newState
        if isValidState(newState):
            deepState = recursiveDFS(newState)
            if deepState is not None and isGoal(deepState):
                return deepState
            
    return None

# checks if a state is has any rule violations
def stateContainsViolations(board):
    # check for row or column violations
    for i in range(9):
        col = [x for x in ([k[0 + i:1 + i][0] for k in board[0:9]]) if x != 0] 
        row = [x for x in board[i] if x != 0] 
            
        if len(set(col)) < len(col) or len(set(row)) < len(row):
            return True
        
    # check for quadrant violations
    for i in range(3):
        for j in range(3):
            quad = getQuadrant([i * 3, j * 3], board)
            quad = [x for x in sum(quad, []) if x != 0] 
                
            if len(set(quad)) < len(quad):
                return True
        
    return False
    
# solves a sudoku and returns np array of solution
def sudoku_solver(state):
    state = state.tolist()
    
    # check if the initial state is actually possible
    if stateContainsViolations(state):
        return np.array([[-1 for i in range(9)] for j in range(9)])
    
    # find the solution
    solution = recursiveDFS(state)    
    if not isinstance(solution, list):
        return np.array([[-1 for i in range(9)] for j in range(9)])
    return np.array(solution) 
