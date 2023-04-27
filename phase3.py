# -----------------------------------
# Name:
# Course:  CS110H, Spring 2023
# Assignment:  Air Combat Simulator
# Documentation: I did not receive any help with this assignment.  
# -----------------------------------

import pythonGraph
import graphics
import simulation as simulation
import ai

# Specifies the Dimensions of the Screen
SCREEN_WIDTH = 990
SCREEN_HEIGHT = 990
player_view_radius = 6

def erase():
    pythonGraph.clear_window("WHITE")

def draw():
    # TODO:  Call the get_field_of_view function in simulation
    # TODO:  Call the draw_world function in graphics
    field_of_view = simulation.get_field_of_view()
    graphics.draw_world(field_of_view, SCREEN_WIDTH, SCREEN_HEIGHT, player_view_radius)
    graphics.draw_hud(simulation.player_x, simulation.player_y)

def update():
    simulation.update_simulation()
    # TODO:  Call the update_simulation function in simulation
    

# -----------------------------------
# Main Program
# -----------------------------------
pythonGraph.open_window(SCREEN_WIDTH, SCREEN_HEIGHT)
pythonGraph.set_window_title("Air Combat Simulator Phase 3")

#Connect to the world server
simulation.connect()

# Initialize the Simulation
simulation.initialize("map.csv", "map_entities.csv")

# Animation Loop
while pythonGraph.window_not_closed():
    erase()
    draw()
    update()
    pythonGraph.update_window()
    
    #pythonGraph.wait_for_close()

#disconnect from the game server once the window has closed
simulation.disconnect()



    
    

