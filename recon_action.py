#don't copy this
import ai
import simulation
import math

##############################################################################################
###Paste the following into get_player_action() and modify variables and calls as necessary###
#################################Change your plane type to Recon##############################
##############################################################################################
def get_player_action():
    global player_heading, command_to_send, PLAYER_AC_TYPE, target, secondary_target, player_x, player_y, missle_warning, entities
    fire_command = ""
    ########################
    ######### Intel ########
    ########################
    #listen for radio messages
    #gather intel about which planes are in the field of view
    ai.intel_hostiles(player_x, player_y, field_of_view)

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
        if (fuel <= (fuel_data[0] + 5)) or (countermeasures < 1) or (player_symbol[0] == "F" and a2a==0) or (player_symbol[0] == "B" and bombs==0):
            print("low fuel or munitions, reorinenting")
            target = ai.fuel_sites[fuel_data[1]]

        #2. pursue the nearest plane in the fov
        elif len(ai.local_threats) > 0:
            print("starting fire sequence")
            target, fire_command = ai.a2akill(player_x,player_y,target)
        
        #3. if there are no planes, patrol around our base
        else:
            target = ai.patrol(player_x, player_y, target)

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