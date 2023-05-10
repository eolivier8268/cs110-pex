import math
import simulation

#map data
discovered_balloons = []
fuel_sites = [(6,11), (19,3), (9,19), (26,8), (41,24), (25,35)]
local_threats = []
global_threats = []
enemey_bases = [(37,39), (45,35), (34,4), (42,10), (6,37), (13,40), (30,22), (20,19)]
enemey_iads = []
blue_bases = [(37,39), (45,35)]
red_bases = [(34,4), (42,10)]
yellow_bases = [(6,37), (13,40)]
green_bases = [(30,22), (20,21)]

#two points used for the patrol function
point1 = (19,2)
point2 = (6,11)

#gets balloons in the fov and appends them to discovered_balloons. Mostly replaced by local intel 
def intel_balloons(player_x, player_y, field_of_view):
    global discovered_balloons
    #check for any undiscovered balloons in the fov
    for row in field_of_view:
        for column in row:
            for entry in column:
                #check for balloons in the fov
                if entry == "BN":
                    #calculate the offset from the center, and use to calculate the coordinates of the balloon
                    dy = field_of_view.index(row) - simulation.player_view_radius
                    dx = row.index(column) - simulation.player_view_radius
                    discovered_balloons.append((player_x+dx, player_y+dy))
                #clear duplicates from balloons list by converting to and from a set
                discovered_balloons = list(set(discovered_balloons))

#gets hostile planes or balloons from the map and appends them to local_threats
def intel_hostiles(player_x, player_y, field_of_view):
    global local_threats
    #check for any undiscovered balloons in the fov
    local_threats = []
    for row in field_of_view:
        for column in row:
            for entry in column:
                #print(entry)
                #check for balloons or enemy planes in the fov
                if entry[:2] == "BH" or entry[:2] == "FH" or entry[:2] == "RH" or entry == "BN":
                    print("tracking hostile entity: " + str(entry))
                    #calculate the offset from the center, and use to calculate the coordinates of the balloon
                    #dist = math.dist([player_x, player_y], entry)
                    dy = field_of_view.index(row) - simulation.player_view_radius
                    dx = row.index(column) - simulation.player_view_radius
                    local_threats.append((player_x+dx, player_y+dy))
                local_threats = list(set(local_threats))

#broadcasts via the radio everything the recon plane sees
def recon_broadcast(entities):
    #check each entity, and add to the static list if it is a static
    intel = 'INTEL,'
    for row in entities:
        intel+=str(row[0])+','+str(row[1])+','+str(row[2])+','
    #print(intel)
    simulation.send_team_message(intel)
    #broadcast via radio all data

def intel_from_broadcasts(message):
    global global_threats,fuel_sites,enemey_iads,enemey_bases
    global_threats = []
    message.remove(message[0])
    message.remove(message[0])
    message.remove('')
    evaluate_fuel_sites = []
    evaluate_iads = []
    evaluate_hostile_bases = []
    #print(message)
    #iterate through each triplet of data
    for i in range(int(len(message)/3)):
        curr_entity = []
        #appends the x value
        curr_entity.append(int(message[3*i]))
        #appends the y value
        curr_entity.append(int(message[1+3*i]))
        #appends the entity id
        curr_entity.append(str(message[2+3*i]))    
        #checks the entity id to determine where to put it 
        if curr_entity[2] == "BN":
            discovered_balloons.append((curr_entity[0], curr_entity[1]))
        if curr_entity[2] == "AF" or curr_entity[2] == "AN":
            fuel_sites.append((curr_entity[0], curr_entity[1]))
            evaluate_fuel_sites.append((curr_entity[0], curr_entity[1]))
        if curr_entity[2] == "AH":
            enemey_bases.append((curr_entity[0], curr_entity[1]))
            evaluate_hostile_bases.append((curr_entity[0], curr_entity[1]))
        if curr_entity[2] == "DH":
            enemey_iads.append((curr_entity[0], curr_entity[1]))
            evaluate_iads.append((curr_entity[0], curr_entity[1]))
        if curr_entity[2][:2] == "BH" or curr_entity[2][:2] == "FH" or curr_entity[2][:2] == "RH" or curr_entity[2] == "BN":
            global_threats.append((curr_entity[0], curr_entity[1], curr_entity[2]))
    #iterate through each static intel and see if it was destroyed
    for entry in fuel_sites:
        if entry not in evaluate_fuel_sites:
            fuel_sites.remove(entry)
    for entry in enemey_bases:
        if entry not in evaluate_hostile_bases:
            enemey_bases.remove(entry)
    for entry in enemey_iads:
        if entry not in evaluate_iads:
            enemey_iads.remove(entry)
    #clear duplicates from lists
    global_threats = list(set(global_threats))
    print("global threats "+ str(global_threats))
    enemey_bases = list(set(enemey_bases))
    print('enemey_bases ' + str(enemey_bases))
    enemey_iads = list(set(enemey_iads))
    print("enemy_iads "+ str(enemey_iads))

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
    #modify to no longer have fuel sites hard coded
    i=0
    distances = []
    for i in fuel_sites:
        distances.append(math.dist((player_x, player_y), (i[0], i[1])))
    best_fuel_dist = min(distances)
    
    #d0 = abs(player_x - fuel_sites[0][0]) + abs(player_y - fuel_sites[0][1])
    #d1 = abs(player_x - fuel_sites[1][0]) + abs(player_y - fuel_sites[1][1])
    #d2 = abs(player_x - fuel_sites[2][0]) + abs(player_y - fuel_sites[2][1])
    #d3 = abs(player_x - fuel_sites[3][0]) + abs(player_y - fuel_sites[3][1])
    #d4 = abs(player_x - fuel_sites[4][0]) + abs(player_y - fuel_sites[4][1])
    #d5 = abs(player_x - fuel_sites[5][0]) + abs(player_y - fuel_sites[5][1])
    #fuel_routes = [d0, d1, d2, d3, d4, d5]
    #print("fuel source distance: " + str(best_fuel_dist))
    #print(fuel_routes)
    #print("best fuel route: station#" + str(fuel_routes.index(best_fuel_dist)) +  " at dist: " + str(best_fuel_dist))

    return((best_fuel_dist, distances.index(best_fuel_dist)))

#patrols between two points
def patrol(player_x, player_y, target):
    global point1, point2
    dist1 = abs(point1[0] - player_x) + abs(point1[1] - player_y)    
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

#checks for balloons in the fov, targets the closest, and shoots any nearby. Mostly replaced by a2a kill
def balloonfarm(player_x, player_y, field_of_view):
    global discovered_balloons
    fire_command = ""
    balloon_routes = []
    best_balloon_dist = 100
    best_balloon = 100 
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

#pursues the closest plane on the map, based on intel from recon plane
def pursue(player_x,player_y,target):
    potential_targets = []
    #review all enemy planes
    for threat in global_threats:
        if threat[2][:2] == "BH" or threat[2][:2] == "FH" or threat[2][:2] == "RH":
            dist_to_threat = math.dist((player_x,player_y), (threat[0], threat[1]))
            potential_targets.append([dist_to_threat, threat[0], threat[1], threat[2]])
    #review all balloons
    if len(potential_targets) == 0:
        for threat in global_threats:
            if threat[2][:2] == "BN":
                dist_to_threat = math.dist((player_x,player_y), (threat[0], threat[1]))
                potential_targets.append([dist_to_threat, threat[0], threat[1], threat[2]])
    if len(potential_targets) > 0:
        target = min(potential_targets)
        #remove the distance count
        target.remove(target[0])
        #remove the id
        target.remove(target[2])
        target[0]=int(target[0])
        target[1]=int(target[1])
        return target
    else:
        return target

#looks at the fov, and shoots any plane or balloon in the specified radius
def a2akill(player_x, player_y, target):
    global local_threats
    fire_command = ""
    target = ()
    final_dist = 100
    shot_range = 3
    for i in local_threats:
        #calculate how many planes we can get a shot on
        #either players within 3 tiles, or in a straight line within 6 tiles
        if ((player_x < (i[0]+shot_range) and player_x > (i[0]-shot_range)) and (player_y < (i[1]+shot_range) and player_y > (i[1]-shot_range))) or in_range(i[0], i[1], 6):
        #if in_range(i[0], i[1], 6):
            fire_command += ";ATK,A2A"
        #calculate the nearest plane to follow
        dist = math.dist([player_x, player_y], i)
        if dist < final_dist:
            final_dist = dist
            target = (i[0], i[1])
    #prevents you from getting stuck on balloon and then firing missle
    if target[0] == player_x and target[1] == player_y:
        target = (target[0]-3, target[1])
    print("pursing hostile at " + str(target))
    return (target, fire_command)

#calculates the nearest enemy base, and whether we are on it. Returns the base as a target and a bomb command if we are over it
def nearestEnemeyBase(player_x, player_y):
    global enemey_bases
    target = []
    temp_bases = []
    #define temp bases to all bases from the recon plane
    i=[]; j=[]
    for i in enemey_bases:
        temp_bases.append(i)
    for j in enemey_iads:
        temp_bases.append(j)
    final_dist = 100
    fire_command = ""
    print(temp_bases)
    for base in temp_bases:
        dist = math.dist([player_x, player_y], base)
        if dist < final_dist:
            final_dist = dist
            target = base
        #temp_bases.remove(base)
    if player_x == target[0] and player_y == target[1]: #checks if we can get a shot once we confirm target
        fire_command = ";ATK,BOMB" 
        enemey_bases.remove(target)
        
    return (target,fire_command)

#takes a target point, and changes x and y to get closer to it
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

#looks for missiles in the AOR, deploys countermeasures and moves plane in opposite direction
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
