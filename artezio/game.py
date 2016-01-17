import random

def choice_winner(n):
    result = []                        #for addition rows, columns, diagonals
    matrix = generate_matrix(n)
    for row in matrix:
        print row
        result.append(row)

    #create and  append list from columns [0][0], [1][0],[2][0] ect.
    column = []
    column = ([[matrix[j][i] for j in range(n)] for i in range(n)])
    result += column

    #create and append list from straight diagonal [[0][0], [1][1], [2][2] ect.
    straight_diagonal = []
    [[straight_diagonal.append(matrix[i][j]) for j in range(n) if i == j] for i in range(n)]
    result.append(straight_diagonal)

    #create and append list from return diagonal [[0][2], [1][1], [2][0] ect.
    return_diagonal = []
    [return_diagonal.append(matrix[i][n-1-i]) for i in range(n)]
    result.append(return_diagonal)

    # check for winner
    if [0]*n in result:
        print "Winner 0"
    elif [1]*n in result:
        print "Winner 1"
    else:
        print "Friendship"

def generate_matrix(n):
    play_space = []
    for row in range(n):
        play_space.append([])                             # create an empty raw(list)
        for col in range(n):                              # every raw have n elements
            play_space[row].append(random.randint(0, 1))  # put new element in row
    return play_space


print "Enter please number: "
choice_winner(input())
