import pygame
import sys
import numpy as np
from scipy.spatial import Delaunay
import time

#Initialize Pygame
pygame.init()

#Screen Setup
screen = pygame.display.set_mode((1000, 1000))

centerx = screen.get_width() / 2
centery = screen.get_height() / 2

#generation variables
tilesize = 5
mean = 30
stdev = 90
room_count = 50
radius = 30
dungeon_height = 600 
dungeon_width = 600

#Main Game Loop
running = True
clock = pygame.time.Clock()
dt = 0
dungeon_array = []
new_array = []
#Dungeon Creation Logic
def roundm(n, m):
    return np.floor((n + m - 1)/m) * m

def getRandomPointInCircle(radius):
    t = 2 * np.pi * np.random.rand()
    u = np.random.rand() + np.random.rand()
    r = 0

    if u > 1:
        r = 2 - u
    else:
        r = u

    return roundm(radius * r * np.cos(t), tilesize), roundm(radius * r * np.sin(t), tilesize)  

def getRandomDimensions(mean, std):
    x = roundm(np.random.normal(mean, std), tilesize)
    y = roundm(np.random.normal(mean, std), tilesize)
    return x, y
all_array = []
def generateDungeon(radius, room_mean, room_std, room_count):
    for i in range(room_count):
        count = 0
        x, y = getRandomPointInCircle(radius)
        x = roundm(x, tilesize)
        y = roundm(y, tilesize)
        roomPos = pygame.Vector2(centerx - x,centery - y)
        width, height = getRandomDimensions(room_mean, room_std)
        width = roundm(width, tilesize)
        height = roundm(height, tilesize)
        dungeon_array.append(pygame.draw.rect(screen, 'blue', pygame.Rect(roomPos.x,roomPos.y, width, height)))
        

def printDungeon(dungeonArray, allArray):
    moveRooms(dungeon_array, mean)  
    screen.fill((0, 0, 0))  # Clear screen
    #for room in allArray:
        #pygame.draw.rect(screen, 'yellow', pygame.Rect(room[0], room[1], room[2], room[3]))
    for room in dungeonArray:
        pygame.draw.rect(screen, 'blue', pygame.Rect(room[0], room[1], room[2], room[3]))

def moveRooms(room_array, room_mean):
    start_time = time.time()
    any_room_moved = False
    for i, room in enumerate(room_array):
        # Check if time limit exceeded
        if time.time() - start_time > 2:  # 2 seconds limit
            return False, True
         
        room_rect = pygame.Rect(room[0], room[1], room[2], room[3])
        
        for j, other_room in enumerate(room_array):
            if i != j:
                other_rect = pygame.Rect(other_room[0], other_room[1], other_room[2], other_room[3])
                
                if room_rect.colliderect(other_rect):
                    overlap = room_rect.clip(other_rect)
                    move_x = overlap.width if room_rect.width > overlap.width else 0
                    move_y = overlap.height if room_rect.height > overlap.height else 0

                    # Adjust position to resolve overlap
                    if room_rect.x < other_rect.x:
                        room[0] -= move_x
                    else:
                        room[0] += move_x

                    if room_rect.y < other_rect.y:
                        room[1] -= move_y
                    else:
                        room[1] += move_y

                    any_room_moved = True

        # Boundary checks
        room[0] = max(150, min(room[0], dungeon_width - room[2] + 100))
        room[1] = max(150, min(room[1],  dungeon_height - room[3] + 100))

    return any_room_moved, False

def reduceDungeon(room_array, room_mean):
    for room in room_array:
        width = room[2]
        height = room[3]
        roomPos = pygame.Vector2(room[0], room[1])
        if (width >= 1.2 * room_mean and height >=  1.2 * room_mean):
                new_array.append(pygame.draw.rect(screen, 'blue', pygame.Rect(roomPos.x,roomPos.y, width, height)))

def triangulateDungeon(A):
    points = []
    reduceDungeon(A, mean)
    for room in new_array:
        points.append([room[0] + room[2] / 2, room[1] + room[3] / 2]) 

    tris = Delaunay(points)
    for tri in tris.simplices:
        pt1 = tri[0]
        pt2 = tri[1]
        pt3 = tri[2]

        pygame.draw.circle(screen, 'red', points[pt1], 5)
        pygame.draw.circle(screen, 'red', points[pt2], 5)
        pygame.draw.circle(screen, 'red', points[pt3], 5)

        """ pygame.draw.line(screen, 'red', points[pt1], points[pt2], 1)
        pygame.draw.line(screen, 'red', points[pt2], points[pt3], 1)
        pygame.draw.line(screen, 'red', points[pt1], points[pt3], 1) """

    return points, tris

def createGraph(tri, points):
    edges = []
    for triangle in tri.simplices:
        for i in range(3):
            start = triangle[i]
            end = triangle[ (i+1) % 3 ]
            start_point = pygame.Vector2(points[start])
            end_point = pygame.Vector2(points[end])
            weight = start_point.distance_to(end_point)
            edges.append((weight, start, end))
    return edges

def find(parent, i):
    if parent[i] == i:
        return i
    return find(parent, parent[i])

def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)
    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
    else:
        parent[yroot] = xroot
        rank[xroot] += 1

def kruskal(edges, N):
    result = []
    all = []
    i = 0
    e = 0
    firstRun = True
    
    edges = sorted(edges, key=lambda item: item[0])

    # Check if there are enough edges
    if len(edges) < N - 1:
        print("Not enough edges to form a spanning tree")
        return result

    parent = []
    rank = []

    for node in range(N):
        parent.append(node)
        rank.append(0)

    while e < N - 1 and i < len(edges):  # Add check for edge list length
        weight, u, v = edges[i]
        i += 1
        x = find(parent, u)
        y = find(parent, v)

        if x != y:
            result.append((u, v))
            union(parent, rank, x, y)
        else: all.append((u,v))

    if firstRun:
        result = addBack(result, all, 0.15)
        firstRun = False

    return result, all

def addBack(mst, all, percentage):
    num_edges_to_add_back = int(len(all) * percentage)
    
    # Choose random indices instead of directly choosing from list of tuples
    indices_to_add_back = np.random.choice(len(all), num_edges_to_add_back, replace=False)
    
    # Use indices to pick the edges
    edges_to_add_back = [all[i] for i in indices_to_add_back]

    # Combine MST and selected non-MST edges
    return mst + edges_to_add_back

hallways = []  # Global list to store hallways

def addHalls(mst, dungeon):
    global hallways
    hallways.clear()
    for edge in mst:
        room1, room2 = edge  # Assuming each edge is a tuple (room1, room2)
        
        # Get the centers of the rooms
        x_center1, y_center1 = (dungeon[room1][0] + dungeon[room1][2] // 2, 
                                dungeon[room1][1] + dungeon[room1][3] // 2)
        x_center2, y_center2 = (dungeon[room2][0] + dungeon[room2][2] // 2, 
                                dungeon[room2][1] + dungeon[room2][3] // 2)
        # Draw line between centers
        if(abs(y_center1 - y_center2) >= mean and abs(y_center1 - y_center2) < 200):
            hallway1 = {'start': (x_center1, y_center1), 'end': (x_center1, y_center2), 'width': 10}
            hallway2 = {'start': (x_center2, y_center2), 'end': (x_center2, y_center1), 'width': 10}
            hallways.append(hallway1)
            hallways.append(hallway2)
            new_array.append(pygame.draw.line(screen, 'blue', hallway1['start'], hallway1['end'], hallway1['width']))
            new_array.append(pygame.draw.line(screen, 'blue', hallway2['start'], hallway2['end'], hallway2['width']))
        if (abs(x_center1 - x_center2) >= mean and abs(x_center1 - x_center2) < 200):
            hallway1 = {'start': (x_center1, y_center1), 'end': (x_center2, y_center1), 'width': 10}
            hallway2 = {'start': (x_center2, y_center2), 'end': (x_center1, y_center2), 'width': 10}
            hallways.append(hallway1)
            hallways.append(hallway2)
            new_array.append(pygame.draw.line(screen, 'blue', hallway1['start'], hallway1['end'], hallway1['width']))
            new_array.append(pygame.draw.line(screen, 'blue', hallway2['start'], hallway2['end'], hallway2['width']))
        if(abs(x_center1 - x_center2) <= mean) or (abs(y_center1 - y_center2) >= mean):
            hallway = {'start': (x_center1, y_center1), 'end': (x_center1, y_center2), 'width': 10}
            hallway = {'start': (x_center2, y_center2), 'end': (x_center2, y_center1), 'width': 10}
            hallways.append(hallway)
            new_array.append(pygame.draw.line(screen, 'blue', hallway['start'], hallway['end'], hallway['width']))

def reAddCollidingRooms(all_rooms, hallways, dungeon_array):
    for room in all_rooms:
        if room not in dungeon_array:
            room_rect = pygame.Rect(room[0], room[1], room[2], room[3])
            for hallway in hallways:
                start, end, width = hallway['start'], hallway['end'], hallway['width']
                hallway_rect = pygame.Rect(min(start[0], end[0]), min(start[1], end[1]), abs(start[0] - end[0]) + width, abs(start[1] - end[1]) + width)

                if hallway_rect.colliderect(room_rect):
                    dungeon_array.append(room)
                    break  # No need to check other hallways for this room




def drawMST(screen, points, mst):
    for edge in mst:
        pygame.draw.line(screen, 'green', points[edge[0]], points[edge[1]], 1)    


generateDungeon(radius, mean, stdev, room_count)
rooms_finalized = False
player_init = False
mst = []
points = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Game Logic
    
    

    def move_char(axis, delta):
        return axis + delta
    
    def try_move_player(player_pos, x_delta, y_delta, rooms):
        new_pos = pygame.Vector2(move_char(player_pos.x, x_delta),
                             move_char(player_pos.y, y_delta))
        new_rect = pygame.Rect(new_pos.x, new_pos.y, 5, 5)
        if is_within_dungeon(new_rect, rooms):
            return new_pos
        return player_pos
    
    def is_within_dungeon(player_rect, rooms):
        # Check if inside any room
        for room in rooms:
            if room.colliderect(player_rect):
                return True

        
        return False    

    if not rooms_finalized:
            room_moved, aborted = moveRooms(dungeon_array, mean)

            if aborted:
                # Restart dungeon generation
                dungeon_array.clear()
                new_array.clear()
                generateDungeon(radius, mean, stdev, room_count)
            elif not room_moved:
                # Perform triangulation and compute MST once rooms are finalized
                points, tris = triangulateDungeon(dungeon_array)
                edges = createGraph(tris, points)
                mst, all = kruskal(edges, len(points))
                mst = addBack(mst, all, 0.09)  # Add back a percentage of the edges
                rooms_finalized = True
    
    

    # Draw Dungeon and MST
    printDungeon(new_array, dungeon_array)
    if rooms_finalized:
        #drawMST(screen, points, mst)
        addHalls(mst, new_array)
        reAddCollidingRooms(dungeon_array, hallways, new_array)
        if player_init == False:
            player_pos = pygame.Vector2(new_array[0][0], new_array[0][1] )
            player_init = True 
    if player_init == True:
        keys = pygame.key.get_pressed()
        x_delta = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        y_delta = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        player_pos = try_move_player(player_pos, x_delta, y_delta, new_array)
        player = pygame.draw.rect(screen, 'red', pygame.Rect(player_pos.x, player_pos.y ,  5, 5))
    

    #Screen Refresh
    pygame.display.flip()

    dt =  clock.tick(60) / 1000



#Quit Pygame
pygame.quit()
sys.exit()