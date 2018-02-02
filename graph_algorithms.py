def distance(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return dx+dy

def neighbours(node, grid, ignore_list):
    width = len(grid)
    height = len(grid[0])
    
    result = []
    #self, pos, value, start, goa
    if(node[0] > 0):
        result.append((node[0]-1, node[1]))
    if(node[0] < width - 1):
        result.append((node[0]+1, node[1]))
    if(node[1] > 0):
        result.append((node[0], node[1]-1))
    if(node[1] < height-1):
        result.append((node[0], node[1]+1))
	
    result = filter(lambda n: (grid[n[0]][n[1]] not in ignore_list), result) 
	
    return result

def trace_path(came_from, current):
    result = [current]
	
    while current in came_from.keys():
        current = came_from[current]
        result.append(current)
    
    result.reverse()
    return result

def find_path(start, goal, grid, ignore_list):
    start = tuple(start)
    goal = tuple(goal)
	
    open_set = [start]
    closed_set = []
    came_from = {}

    g_score = [[10000 for x in range(len(grid[y]))] for y in range(len(grid))]
    g_score[start[0]][start[1]] = 0
    
    f_score = [[10000 for x in range(len(grid[y]))] for y in range(len(grid))]
    f_score[start[0]][start[1]] = distance(start, goal)
        
    while len(open_set) > 0:
        current = min(open_set, key=lambda p: f_score[p[0]][p[1]])
        
        if(current == goal):
            path = trace_path(came_from, current)
            #for x in path:
            #    print(str(x))
            return path

        open_set.remove(current)
        closed_set.append(current)
                      
        for n in neighbours(current, grid, ignore_list):
            if n in closed_set:
                continue
                      
            tentative_g_score = g_score[current[0]][current[1]] + distance(current, n)
                      
            if n not in open_set:
                open_set.append(n)      
            elif tentative_g_score >= g_score[n[0]][n[1]]:
                continue

            came_from[n] = current
            g_score[n[0]][n[1]] = tentative_g_score
            f_score[n[0]][n[1]] = tentative_g_score + distance(n, goal)         
    return None
