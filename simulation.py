import time
import math
import paho.mqtt.client as mqtt
import threading
import ai

# PLAYER VARIABLES
player_x = 13
player_y = 13
target = (18,15)
secondary_target = ()
player_heading = "N"
player_view_radius = 10
a2a = 0
a2g = 0
bombs = 0
countermeasures = 0
fuel = 100
missle_warning = False

#static map data to store

# SIMULATION VARIABLES
world_map = []
entities = []
field_of_view = []
last_update = time.time()

UPDATE_INTERVAL_IN_SECONDS = 1.0
last_update = time.time()

#variables for network capability
player_symbol = ""
SERVER_IP_ADDRESS = "96.66.89.56"
PLAYER_ID = "snap"
PLAYER_TEAM = "silver"
PLAYER_AC_TYPE = "recon"
COMMAND_CHANNEL = "acs_server"
TEAM_CHANNEL = "comm"
client = None
command_to_send = ""
server_cmd_log = []

# -----------------------------------------------------------
# initialize()
# -----------------------------------------------------------
# YOUR FUNCTION GOES HERE
def initialize (map_file, entity_file):
    global world_map, entities
    f = open(map_file)
    fcontents = f.read()
    lines = fcontents.split('\n')
    
    for i in lines:
        elements_list = i.split(',')
        world_map.append(elements_list)        
    f.close()
    
    #entity file initialization goes here
    f = open(entity_file)
    fcontents = f.read()
    lines = fcontents.split('\n')
    
    for i in lines:
        elements_list = i.split(',')
        entities.append(elements_list)
    
    #print(world_map)
    #print(entities)
    

# -----------------------------------------------------------
# get_field_of_view()
# -----------------------------------------------------------
# YOUR FUNCTION GOES HERE
def get_field_of_view():
    global player_x, player_y, player_heading, player_view_radius, field_of_view, world_map, entities, player_symbol
    y=0; x=0
    field_of_view = []
    # i is the row
    for y in range((player_y - player_view_radius), (player_y + player_view_radius+1)):
        row = []; col = []
        #j is the column
        for x in range((player_x - player_view_radius), (player_x + player_view_radius+1)):
            if y <= 49 and y >= 1 and x <= 50 and x >= 1: 
                row.append([world_map[y-1][x-1]])
            else:
                row.append(["N"])
            for entry in entities:
                if int(entry[0]) == x and int(entry[1]) == y:
                    row[x - player_x + player_view_radius].append(entry[2])
            if (x == player_x) and (player_y == y):
                #print("player symbol: " + player_symbol)
                if player_heading == 'N':
                    row[player_view_radius].append(str(player_symbol))
                elif player_heading == 'S':
                    row[player_view_radius].append(str(player_symbol))
                elif player_heading == 'W':
                    row[player_view_radius].append(str(player_symbol))
                elif player_heading == 'E':
                    row[player_view_radius].append(str(player_symbol))
        field_of_view.append(row)
    return field_of_view
    

# -----------------------------------------------------------
# get_player_action()
# -----------------------------------------------------------
# YOUR FUNCTION GOES HERE
def get_player_action():
    global player_heading, command_to_send, PLAYER_AC_TYPE, target, secondary_target, player_x, player_y, missle_warning, entities
    fire_command = ""
    ########################
    ######### Intel ########
    ########################
    #check for ballons on the map and add to the ai.discovered_balloons list
    #ai.intel_balloons(player_x, player_y, field_of_view)
    ai.intel_hostiles(player_x, player_y, field_of_view)
    #print(ai.local_threats)
    #print("bases remaining: " + str(ai.enemey_bases))

    ########################
    ####Dodging mechanic####
    ########################
    #0. determine if there is a threat we need to dodge. If so, send a safe heading command and ignore target calculations
    for threat in entities:
        #print(threat)
        dist = math.dist([player_x, player_y], [int(threat[0]), int(threat[1])])
        if str(threat[2])[0] == "M" and dist < 4:
            missle_warning = True
    if missle_warning == True:
        #dodge immediately
        command_to_send = ai.dodge_missile(player_x, player_y, target)
        #re-evaluate whether to dodge
        missle_warning = False
        for threat in entities:
            if str(threat[2])[0] == "M":
                missle_warning = True
    
    ########################
    ####Target Selection####
    ########################
    #only enter the main logic sequence if there are no immediate threats to dodge (else)
    else:       
        #1. check fuel, if the distance to nearest base <= current fuel + 10, set closest base as target, back up current target
        fuel_data = ai.check_fuel(player_x, player_y)
            #a tuple storing (0)the number of tiles to the closest fuel source (1)the index of the closest fuel source in the fuel_sites array
        if (fuel <= (fuel_data[0] + 5)) or (countermeasures < 1) or (player_symbol[0] == "F" and a2a==0) or (player_symbol[0] == "B" and bombs==0) or (player_symbol[0] == "R" and a2a==0):
            print("low fuel or munitions, reorinenting")
            target = ai.fuel_sites[fuel_data[1]]
        
        #2. attempt to bomb the closest base
        #elif len(ai.enemey_bases) >= 1:
        #    target, fire_command = ai.nearestEnemeyBase(player_x, player_y)

        #. patrol between points and attempt to shoot down fighters if detected
        elif len(ai.local_threats) < 1:
            target = ai.patrol(player_x, player_y,target)
        else: 
            target, fire_command = ai.a2akill(player_x, player_y, target)

        #3. once all bases have been destroyed, patrol between two baloon points
        #elif len(ai.discovered_balloons) < 1:
        #    target = ai.patrol(player_x, player_y, target)

        #4. send a fighter to attack balloons
        #else:
        #    print('all objectives completed. returning to patrol sequence')
        #    target,fire_command = ai.balloonfarm(player_x, player_y, field_of_view)
                       
        
        #4. once all targets accomplished, patrol between two points
        #else:
        #    target = ai.patrol(player_x, player_y, target)
        #    

        ########################
        #######Navigation#######
        ########################
        #we determined the target, now we move to it with the following navigation code
        #we always move in the x direction first, then the y direction
        command_to_send = ai.navigate_simple(player_x, player_y, target)

        ########################
        ##Additional  Commands##
        ########################
        #if we need to append any commands earlier, send
        if fire_command != "":
            command_to_send += fire_command 

    
    
    
    # if pythonGraph.key_down("left"):
    #     command_to_send = "DIR,WEST"
    # elif pythonGraph.key_down("right"):
    #     command_to_send = "DIR,EAST"
    # elif pythonGraph.key_down("up"):
    #     command_to_send = "DIR,NORTH"
    # elif pythonGraph.key_down("down"):
    #     command_to_send = "DIR,SOUTH"
    # elif pythonGraph.key_down("c"):
    #     command_to_send = "DEF"
    # elif pythonGraph.key_down("1"):
    #     command_to_send = "ATK,A2A"
    # elif pythonGraph.key_down("2"):
    #     command_to_send = "ATK,A2G"
    # elif pythonGraph.key_down("3"):
    #     command_to_send = "ATK,BOMB"
    # elif pythonGraph.key_down("q"):
    #     PLAYER_AC_TYPE = "fighter"

# update_simulation()
# checks time and if one second has passed, the current command is sent to the server
def update_simulation():
    global player_y, player_x, player_heading, last_update, command_to_send
    #move get_player_action here when using arrow keys
    #get_player_action()
    if float(time.time()) > last_update + UPDATE_INTERVAL_IN_SECONDS:
        #move get_player_action here when using AI
        get_player_action()
        send_command(command_to_send)
        command_to_send = ""
        last_update = time.time()
    
# NETWORKING FUNCTION
# This connects to the server
def connect():
    global client

    # Connects to the Server
    client = mqtt.Client(client_id=PLAYER_ID, clean_session=True)
    client.on_message = on_raw_message
    client.on_connect = on_connect
    client.connect(host=SERVER_IP_ADDRESS)

    # Tells the Program to Listen Forever
    sub = threading.Thread(target=listen_for_messages)
    sub.start()

# NETWORKING FUNCTION
# This disconnects from the server when the pythonGraph window is closed
def disconnect():
   print("Disconnecting from server:", SERVER_IP_ADDRESS)
   send_command("LOGOUT," + PLAYER_ID)
   client.disconnect()

# NETWORKING FUNCTION
# Runs when the client connects to the server
def on_connect(client, userdata, flags, rc):
    print("Connected to server:", SERVER_IP_ADDRESS)
    send_command("LOGIN," + PLAYER_ID + "," + PLAYER_TEAM + "," + PLAYER_AC_TYPE)
# NETWORKING FUNCTION
# This function listens for messages from the world and the team
def listen_for_messages():
   client.subscribe(PLAYER_ID) # This is just for this client
   client.subscribe(TEAM_CHANNEL) # This is for the entire team
   client.loop_forever()

# NETWORKING FUNCTION
# This function is called when a message is received
def on_raw_message(client, userdata, raw_message):
   decoded_message = str(raw_message.payload.decode("utf-8"))
   on_data_received(decoded_message)

# NETWORKING FUNCTION
# This sends a command to the server
def send_command(command):
    if len(command) > 0:
       print("Sending:", PLAYER_ID + "," + command)
       client.publish(COMMAND_CHANNEL, PLAYER_ID + "," + command)

# NETWORKING FUNCTION
# This sends a message to other team members
def send_team_message(message):
   if len(message) > 0:
      print("Sending:", PLAYER_ID + "," + message)
      client.publish(TEAM_CHANNEL, PLAYER_ID + "," + message)
      
# pulls the heading based on the player symbol from the server
def get_heading():
    global player_symbol, player_heading
    if player_symbol != "E":
        if player_symbol[2] == "N":
            return "NORTH"
        elif player_symbol[2] == "S":
            return "SOUTH"
        elif player_symbol[2] == "E":
            return "EAST"
        elif player_symbol[2] == "W":
            return "WEST"
    else:
        return "NO HEADING"

# Processes a String Received from the Server
def on_data_received(data):
   global player_symbol, player_heading, player_x, player_y, entities, server_cmd_log, a2a, a2g, bombs, countermeasures, fuel
   #print("data str: " + data)
   data_lines = data.split(";")
   for msg in data_lines:
        msg_split = msg.split(",")
        #print("curr message:" + str(msg_split))
        if str(msg_split[0]) == "STATUS":
            player_symbol = str(msg_split[1])
            player_heading = str(get_heading())[0]
            player_x = int(msg_split[2])
            player_y = int(msg_split[3])
            fuel = float(msg_split[4])
            a2a = int(msg_split[5])
            a2g = int(msg_split[6])
            bombs = int(msg_split[7])
            countermeasures = int(msg_split[8]);
        elif str(msg_split[0]) == "FOV":
            entities = []
            #iterate through each triplet of data
            for i in range(int(msg_split[1])):
                curr_entity = []
                #appends the x value
                #print(msg_split[3+(3*i)])
                curr_entity.append(int(msg_split[3+(3*i)]))
                #appends the y value
                #print(msg_split[4+(3*i)])
                curr_entity.append(int(msg_split[4+(3*i)]))
                #appends the entity id
                #print(msg_split[2+(3*i)])
                curr_entity.append(str(msg_split[2+(3*i)]))
                
                entities.append(curr_entity)
        elif str(msg_split[0]) == "TEXT":
            print("Recv from server: " + msg_split[1])
        elif str(msg_split[0]) == "INTEL":
            print("Recv from radio: " + msg_split[1])
        elif len(msg_split) > 1 and str(msg_split[1]) == "INTEL":
            #print("received a radio message")
            #print(msg_split)
            ai.intel_from_broadcasts(msg_split)

#INTEL:45,35,AH;37,39,AH;19,2,AF;6,11,AF;6,37,AH;13,40,AH;20,19,AH;41,24,AN;26,8,AN;25,35,AN;9,19,AN;45,32,DH;34,40,DH;17,40,DH;8,34,DH;19,5,DF;4,11,DF;18,21,DH;3,24,BN;4,20,BN;39,21,BN;26,10,BN;25,9,BN;24,18,BN;22,24,BN;22,23,BN;23,23,BN;19,2,C;19,2,C;18,2,C;18,2,C;18,2,C;



                

#on_data_received("STATUS,FFS,15,25,100,8,0,0,5;FOV,2,FHN,16,22,BHE,18,24")
#print(entities)