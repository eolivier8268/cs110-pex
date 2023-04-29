import math
import simulation

#map data
discovered_balloons = []
fuel_sites = [(6,11), (19,3),      (9,19), (26,8), (41,24), (25,35)]
static_intel = []

#gathers intel from the map
def intel_balloons(player_x, player_y, field_of_view):
    global discovered_balloons
    #check for any undiscovered balloons in the fov
    for row in field_of_view:
        for column in row:
            for entry in column:
                #check for balloons in the fov
                if entry == "BN":
                    #calculate the offset from the center, and use to calculate the coordinates of the balloon
                    dy = field_of_view.index(row) - 6
                    dx = row.index(column) - 6
                    discovered_balloons.append((player_x+dx, player_y+dy))
                #clear duplicates from balloons list by converting to and from a set
                discovered_balloons = list(set(discovered_balloons))

# determines if you are facing and in range of a target
def in_range(x, y, distance):
    if simulation.player_symbol != "E":
        if simulation.player_heading == "N":
            return simulation.player_x == x and simulation.player_y > y and abs(simulation.player_y-y) <= distance
        elif simulation.player_heading == "S":
            return simulation.player_x == x and simulation.player_y < y and abs(simulation.player_y-y) <= distance
        elif simulation.player_heading == "E":
            return simulation.player_y == y and simulation.player_x > x and abs(simulation.player_x-x) <= distance
        elif simulation.player_heading == "W":
            return simulation.player_y == y and simulation.player_x > x and abs(simulation.player_x-x) <= distance
    return False;

def check_fuel(player_x, player_y):
    d0 = abs(player_x - fuel_sites[0][0]) + abs(player_y - fuel_sites[0][1])
    d1 = abs(player_x - fuel_sites[1][0]) + abs(player_y - fuel_sites[1][1])
    d2 = abs(player_x - fuel_sites[2][0]) + abs(player_y - fuel_sites[2][1])
    d3 = abs(player_x - fuel_sites[3][0]) + abs(player_y - fuel_sites[3][1])
    d4 = abs(player_x - fuel_sites[4][0]) + abs(player_y - fuel_sites[4][1])
    d5 = abs(player_x - fuel_sites[5][0]) + abs(player_y - fuel_sites[5][1])
    fuel_routes = [d0, d1, d2, d3, d4, d5]
    best_fuel_dist = min(fuel_routes)
    
    #print("fuel source distance: " + str(best_fuel_dist))
    #print(fuel_routes)
    #print("best fuel route: station#" + str(fuel_routes.index(best_fuel_dist)) +  " at dist: " + str(best_fuel_dist))

    return((best_fuel_dist, fuel_routes.index(best_fuel_dist)))
    
def patrol(player_x, player_y, target):
    point1 = (6,22)
    dist1 = abs(point1[0] - player_x) + abs(point1[1] - player_y)
    point2 = (26,2)
    dist2 = abs(point2[0] - player_x) + abs(point2[1] - player_y)
    
    #if the player is at a different target (ex refueling), return to the closest patrol point
    if player_x == target[0] and player_y == target[1]:
        if dist1 < dist2 and target != point1: 
            return point1
        elif dist2 < dist1 and target != point2:
            return point2
        else:
            if target != point1:
                return point1
            else:
                return point2
    #if at point 1, set the target to point 2
    elif player_x == point1[0] and player_y == point1[1]:
        return point2
    #if at point 2, set the target to point 1
    elif player_y == point2[0] and player_y == point2[1]:
        return point1
    #otherwise maintain the current target
    else:
        return target

def balloonfarm(player_x, player_y, field_of_view):
    global discovered_balloons
    fire_command = ""
    balloon_routes = []; best_balloon_dist = 100; best_balloon = 100 
    for i in discovered_balloons:
        #determine if we can get a shot on any balloon
        if in_range(i[0], i[1], 4):
            fire_command = ";ATK,A2A"    
            #fire_command = "ATK,A2A"
            discovered_balloons.remove((i[0], i[1]))
            #if there is another baloon, target it
            if len(discovered_balloons) > 1:
                return(discovered_balloons[0], fire_command)
            elif len(discovered_balloons) == 1:
                return(discovered_balloons[0], fire_command)
            #if there is no baloon, return to the patrol path
            else:
                return(patrol(player_x, player_y, simulation.target), fire_command)
        #otherwise, target the nearest balloon
        else:        
            balloon_routes.append(abs(player_x - i[0]) + abs(player_y - i[1]))
            best_balloon_dist = min(balloon_routes)
            best_balloon = discovered_balloons[balloon_routes.index(best_balloon_dist)]
            return(best_balloon, fire_command)      

def ai_recon():
    #check each entity, and add to the static list if it is a static
    for entry in simulation.entities:
        if entry[2] == "AF":
            static_intel.append(entry)
            print(simulation.entities)  
    #check each moving entity and add to the dynamic list (do we actually need this?)
    #check each entity in the static list and determine if it is still alive
    for entry in static_intel:
        print()
    #broadcast via radio all data

def navigate_simple(player_x, player_y, target):
    if player_x < target[0]:
        return("DIR,EAST")
    elif player_x > target[0]:
        return("DIR,WEST")
    elif player_y < target[1]:
        return("DIR,SOUTH")
    elif player_y > target[1]:
        return("DIR,NORTH")
    else:
        return("DIR,NORTH")

def dodge_missile(player_x, player_y, target):
    #define potential actions
    print("Beginning dodge sequence")
    possible_commands = ["DIR,NORTH", "DIR,EAST", "DIR,SOUTH", "DIR,WEST"]
    fire_command = ""
    #by changing the awareness radius, we can change approx how many tiles the plane moves when dodging
    #5 => one tile back; 10=> 2 tiles back
    aware_radius = 10
    #detect missiles in fov and evaluate which directions are best to avoid
    for threat in simulation.entities:
        if str(threat[2])[0] == "M":
            if int(threat[0]) > player_x and int(threat[0]) < (player_x + aware_radius) and "DIR,EAST" in possible_commands:
                possible_commands.remove("DIR,EAST")
                fire_command = ";DEF"
                #return "DIR,WEST"
            elif int(threat[0]) < player_x and int(threat[0]) > (player_x - aware_radius) and "DIR,WEST" in possible_commands:
                possible_commands.remove("DIR,WEST")
                fire_command = ";DEF"
                #return "DIR,EAST"
            elif int(threat[1]) > player_y and int(threat[1]) < (player_y + aware_radius) and "DIR,SOUTH" in possible_commands:
                possible_commands.remove("DIR,SOUTH")
                fire_command = ";DEF"
                #return "DIR,NORTH"
            elif int(threat[1]) < player_y and int(threat[1]) > (player_y - aware_radius) and "DIR,NORTH" in possible_commands:
                possible_commands.remove("DIR,NORTH")
                fire_command = ";DEF"
                #return "DIR,SOUTH"
    print("possible moves are " + str(possible_commands))
    #determine if the desired command is allowed, and if not, choose the opposite direction
    if player_x < target[0]:
        if "DIR_EAST" in possible_commands:
            return "DIR,EAST" + str(fire_command)
        else:
            return "DIR,WEST" + str(fire_command)
    if player_x > target[0]:
        if "DIR,WEST" in possible_commands:
            return "DIR,WEST" + str(fire_command)
        else:
            return "DIR,EAST" + str(fire_command)
    if player_y < target[1]:
        if "DIR,SOUTH" in possible_commands:
            return "DIR,SOUTH" + str(fire_command)
        else:
            return "DIR,NORTH" + str(fire_command)
    if player_y > target[1]:
        if "DIR,NORTH" in possible_commands:
            return "DIR,NORTH" + str(fire_command)
        else:
            return "DIR,SOUTH" + str(fire_command)
    else:
        return navigate_simple(simulation.player_x, simulation.player_y, simulation.target)

#indev, don't run
def navigate_advanced(player_x, player_y, field_of_view):
    global command_to_send
    possible_commands = ["DIR,NORTH", "DIR,EAST", "DIR,SOUTH", "DIR,WEST"]
    threats = []
    #check if there are hostilities in the fov fov and add them to a threat array
    for row in field_of_view:
        for column in row:
            for entry in column:
                #check for planes in the fov
                if entry[0:1] == "FH" or entry[0:1] == "BH" or entry[0:1] == "RH" :
                    threats.append([entry, row, column])
                #check for bases, iads in the fov
                elif entry == "AH" or entry == "DH":
                    threats.append([entry, row, column])
                #check for missiles in the fov
                elif entry[0] == "M":
                    threats.append([entry, row, column])
    
    #first avoid missiles by eliminating options
    for threat in threats:
        if str(threat[0][0]) == "M":
            #check if the missile falls on each side of the plane
            if threat[1] > player_x and threat[1] < (player_x + 5):
                possible_commands.remove("DIR,EAST")
            elif threat[1] < player_x and threat[1] > (player_x - 5):
                possible_commands.remove("DIR,WEST")
            elif threat[2] > player_y and threat[2] < (player_y + 5):
                possible_commands.remove("DIR,SOUTH")
            elif threat[2] < player_y and threat[2] > (player_y - 5):
                possible_commands.remove("DIR,NORTH")


    #then avoid planes and bases based on proximity

    #if no threats
    #check if we are lined up or at a diagonal offset
        #if we are diagonal, randomize direction
    #print(threats)
    