from graph_algorithms import find_path, generate_waypoints, link_waypoints, enough_space
import bottle
import os
import time

EMPTY = 0
WALL = 1
SNAKE = 2
FOOD = 3
DANGER = 4
DIRECTIONS = ['up', 'down', 'left', 'right']
taunt = 'Do battle snakes dream of electric apples?'


def point_to_list(json_object):
    return (json_object['x'], json_object['y'])


def objectives(data):
    results = []
    food = data['food']['data']
    for f in food:
        results.append(point_to_list(f))
    return results


def display_grid(grid):
    for y in range(len(grid)):
        row = ""
        for x in range(len(grid[y])):
            row = row + str(grid[x][y]) + " "
        print(row)


def generate_grid(snake_id, my_snake_length, data):
    grid = [[0 for col in range(data['height'])] for row in range(data['width'])]

    for food in data['food']['data']:
        food = point_to_list(food)
        grid[food[0]][food[1]] = FOOD

    for snake in data['snakes']['data']:
        for coord in snake['body']['data']:
            coord = point_to_list(coord)
            # Add in once accounting for eating an apple
            # if coord != snake['coords'][-1]:
            grid[coord[0]][coord[1]] = SNAKE

        if snake_id != snake['id']:
            if my_snake_length <= snake['length']:
                danger_spots = open_neighbours(point_to_list(snake['body']['data'][0]), grid)
                for n in danger_spots:
                    grid[n[0]][n[1]] = DANGER

    return grid


def direction(a, b):
    if(a[0] > b[0]):
        return 'left'
    if(a[0] < b[0]):
        return 'right'
    if(a[1] > b[1]):
        return 'up'
    if(a[1] < b[1]):
        return 'down'


def smart_direction(a, b, grid, obstacles):
    if(a[0] > b[0] and grid[a[0] - 1][a[1]] not in obstacles):
        return 'left'
    if(a[0] < b[0] and grid[a[0] + 1][a[1]] not in obstacles):
        return 'right'
    if(a[1] > b[1] and grid[a[0]][a[1] - 1] not in obstacles):
        return 'up'
    if(a[1] < b[1] and grid[a[0]][a[1] + 1] not in obstacles):
        return 'down'


def move_to_position(origin, direction):
    if direction is 'up':
        return (origin[0], origin[1] - 1)
    if direction is 'down':
        return (origin[0], origin[1] + 1)
    if direction is 'right':
        return (origin[0] + 1, origin[1])
    if direction is 'left':
        return (origin[0] - 1, origin[1])


def path_distance(path):
    dis = 0
    path = tuple(path)
    index = 0
    while index < len(path) - 1:
        dis = dis + distance(path[index], path[index + 1])
        index = index + 1
    return dis


def distance(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return dx+dy


def is_free(target, grid):
    value = grid[target[0]][target[1]]
    if(value == 1 or value == 4 or value == 2):
        return False
    return True


def open_neighbours(pos, grid):
    width = len(grid)
    height = len(grid[0])

    result = []
    if(pos[0] > 0):
        n = (pos[0]-1, pos[1])
        if(is_free(n, grid)):
            result.append(n)
    if(pos[0] < width - 1):
        n = (pos[0]+1, pos[1])
        if(is_free(n, grid)):
            result.append(n)
    if(pos[1] > 0):
        n = (pos[0], pos[1]-1)
        if(is_free(n, grid)):
            result.append(n)
    if(pos[1] < height-1):
        n = (pos[0], pos[1]+1)
        if(is_free(n, grid)):
            result.append(n)

    return result


def run_ai(data):
    # Important Info:
    move = 'left'
    snake_id = data['you']['id']
    goals = objectives(data)
    my_snake_length = data['you']['length']
    my_snake_health = data['you']['health']
    if my_snake_health < 15:
        print('About to die of hunger!')
    grid = generate_grid(snake_id, my_snake_length, data)
    my_snake_head = point_to_list(data['you']['body']['data'][0])
    my_snake_tail = point_to_list(data['you']['body']['data'][-1])

    # Do I want or need food?
    # Can I bully?
    # Should I find free space?
    # Is food near me?
    # Safe Roam or chase tail?

    # Currently I either eat the nearest food
    # the enemy is not at or I roam
    current_path = None
    start = time.time()
    waypoints = generate_waypoints(grid, [1, 2, 4], my_snake_head)
    end = time.time()
    print('Time to waypoints: ' + str((end - start) * 1000) + 'ms')
    start = time.time()
    links = link_waypoints(waypoints, grid, [1, 2, 4])
    end = time.time()
    current_path = None
    print('Time to link waypoints: ' + str((end - start) * 1000) + 'ms')
    for goal in goals:
        easy = True
        for snake in data['snakes']['data']:
            if(snake['id'] != snake_id):
                enemy_dist = distance(point_to_list(snake['body']['data'][0]), goal)
                if enemy_dist < distance(my_snake_head, goal):
                    easy = False
                    break
        # TODO update hunger level to be dependent on food amount and game boad size
        if not easy and my_snake_health > 20:
            continue
        start = time.time()
        path = find_path(my_snake_head, goal, waypoints, links, grid, [1, 2, 4])
        end = time.time()
        # print('Time to get path from o_path: ' + str((end - start) * 1000) + 'ms')
        if current_path is None:
            if path is None:
                continue
            start = time.time()
            possible_move = smart_direction(my_snake_head, path[1], grid, [1, 2, 4])
            block_pos = move_to_position(my_snake_head, possible_move)
            temp_hold = grid[block_pos[0]][block_pos[1]]
            grid[block_pos[0]][block_pos[1]] == 1
            # if the snake body can fit in flood fill then legal move
            if my_snake_length <= enough_space(path[-1], my_snake_length, grid, [1, 2, 4]):
                current_path = path
            grid[block_pos[0]][block_pos[1]] == temp_hold
            end = time.time()
            print('Time to fill: ' + str((end - start) * 1000) + 'ms')
        elif path is not None:
            # get move, then place move on grid, then flood fill on target.
            start = time.time()
            possible_move = smart_direction(my_snake_head, path[1], grid, [1, 2, 4])
            block_pos = move_to_position(my_snake_head, possible_move)
            temp_hold = grid[block_pos[0]][block_pos[1]]
            grid[block_pos[0]][block_pos[1]] == 1
            # if the snake body can fit in flood fill then legal move
            if my_snake_length <= enough_space(path[-1], my_snake_length, grid, [1, 2, 4]):
                if path_distance(path) < path_distance(current_path):
                    current_path = path
            grid[block_pos[0]][block_pos[1]] == temp_hold
            end = time.time()
            print('Time to fill: ' + str((end - start) * 1000) + 'ms')

    if current_path is not None:
        '''print('Printing path')
        for n in current_path:
            print(n)'''
        move = smart_direction(my_snake_head, current_path[1], grid, [1, 2, 4])
        print('Going to ' + str(current_path[1]) + ' by going ' + str(move))
    else:
        # print('No good goals!!!')
        # follow tail
        tail_neighbours = open_neighbours(my_snake_tail, grid)
        for n in tail_neighbours:
            path = find_path(my_snake_head, n, waypoints, links, grid, [1, 2, 4])
            if path is not None:
                current_path = path
                break
        if path is not None:
            move = smart_direction(my_snake_head, current_path[1], grid, [1, 2, 4])
            print('Going to ' + str(current_path[1]) + ' by going ' + str(move))
        else:
            # TODO: FIND LARGEST PATH OR MOVE TO CENTRE
            possible_positions = open_neighbours(my_snake_head, grid)
            if len(possible_positions) > 0:
                # taunt = 'I love the smell of battle snake in the...'
                move = direction(my_snake_head, possible_positions[0])
            else:
                move = 'down'
                # taunt = 'That was irrational of you. Not to mention unsportsmanlike.'
        print('Going ' + move)

    return move


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    print("New game started!")
    board_width = data['width']
    board_height = data['height']
    print(str(game_id) + " " + str(board_width) + " " + str(board_height))

    # TODO: Do things with data

    return {
        'color': 'DarkMagenta',
        'secondary_color': 'red',
        'taunt': 'Quite an experience to live in fear, isn\'t it?',
        'name': 'Batty Snake'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    # print(str(data))
    start = time.time()
    output = run_ai(data)
    end = time.time()
    print('Time to get AI move: ' + str((end - start) * 1000) + 'ms')
    return {
        'move': output,
        'taunt': taunt
    }


@bottle.get('/')
def status():
    return{
        "<!DOCKTYPE html><html><head><title>2018</title><style>p{color:orange;}</style></head><body><p>BattleSnake 2018 by Mitchell Nursey.</p></body></html>"
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, server='auto', host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
