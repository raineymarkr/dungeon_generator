import pygame
import sys
import numpy as np
from scipy.spatial import Delaunay

#Initialize Pygame
pygame.init()

#Screen Setup
screen = pygame.display.set_mode((1024, 768))
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() /2 )
centerx = screen.get_width() / 2
centery = screen.get_height() / 2
#Main Game Loop
running = True
clock = pygame.time.Clock()
dt = 0
tilesize = 4
mean = 50
dungeon_height = 1240
dungeon_width = 768
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
    for room in allArray:
        pygame.draw.rect(screen, 'yellow', pygame.Rect(room[0], room[1], room[2], room[3]))
    for room in dungeonArray:
        pygame.draw.rect(screen, 'blue', pygame.Rect(room[0], room[1], room[2], room[3]))

def moveRooms(room_array, room_mean):
    any_room_moved = False
    for i, room in enumerate(room_array): 
        room_loc = pygame.Vector2(room[0], room[1])
        room_size = [room[2], room[3]]
        room_rect = pygame.Rect(room_loc.x, room_loc.y, room_size[0], room_size[1])
        
        for j, other_room in enumerate(room_array):
            if i != j:
                other_loc = pygame.Vector2(other_room[0], other_room[1])
                other_size = pygame.Vector2(other_room[2], other_room[3])
                other_rect = pygame.Rect(other_loc.x, other_loc.y, other_size.x, other_size.y)
                
                if room_rect.colliderect(other_rect):
                    overlap = room_rect.clip(other_rect)
                    if overlap.width < overlap.height:
                        #horiz
                        if room_loc.x < other_loc.x:
                            room[0] -= overlap.width
                        else:
                            room[0] += overlap.width
                    else:
                        #vert
                        if room_loc.y < other_loc.y:
                            room[1] -= overlap.height
                        else:
                            room[1] += overlap.height
             # Check if any room has moved
            if room[0] != room_loc.x or room[1] != room_loc.y:
                any_room_moved = True
    # Round positions to align with the grid
    room[0] = roundm(room[0], tilesize)
    room[1] = roundm(room[1], tilesize)
    return any_room_moved

def reduceDungeon(room_array, room_mean):
    for room in room_array:
        width = room[2]
        height = room[3]
        roomPos = pygame.Vector2(room[0], room[1])
        if (width >= 1.1*room_mean and height >= 1.1*room_mean):
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

def drawMST(screen, points, mst):
    for edge in mst:
        pygame.draw.line(screen, 'green', points[edge[0]], points[edge[1]], 1)    


generateDungeon(100, mean, mean-10, 100)
rooms_finalized = False
mst = []
points = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Game Logic
    pygame.draw.circle(screen, "red", player_pos, 40)
    
    

    def move_char(axis, dir):
        delta = 1
        if dir == 1:
            axis += delta
        elif dir == 0:
            axis -= delta
        return axis

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos.x = move_char(player_pos.x, 0)
    elif keys[pygame.K_RIGHT]:
        player_pos.x = move_char(player_pos.x, 1)
    elif keys[pygame.K_UP]:
        player_pos.y = move_char(player_pos.y, 0)
    elif keys[pygame.K_DOWN]:
        player_pos.y = move_char(player_pos.y, 1)

    if not rooms_finalized:
        if not moveRooms(dungeon_array, mean):
            # Perform triangulation and compute MST once rooms are finalized
            points, tris = triangulateDungeon(dungeon_array)
            edges = createGraph(tris, points)
            mst, all = kruskal(edges, len(points))
            mst = addBack(mst, all, 0.08)  # Add back 15% of the edges
            rooms_finalized = True

    # Draw Dungeon and MST
    printDungeon(new_array, dungeon_array)
    if rooms_finalized:
        drawMST(screen, points, mst)

    
    #pygame.draw.rect(screen, 'red', pygame.Rect(500, 500 ,  50, 50)) 

    #Screen Refresh
    pygame.display.flip()

    dt =  clock.tick(60) / 1000



#Quit Pygame
pygame.quit()
sys.exit()