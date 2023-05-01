import pythonGraph
import simulation

def draw_fighter(x,y,width,height, id):
    filename = str("images/" + id + ".png")
    pythonGraph.draw_image(filename, x, y, width, height)

def draw_bomber(x,y, width,height, id):
    filename = str("images/" + id + ".png")
    pythonGraph.draw_image(filename, x, y, width, height)
    
def draw_recon(x,y, width,height, id):
    filename = str("images/" + id + ".png")
    pythonGraph.draw_image(filename, x, y, width, height)

def draw_missile(x,y, width,height, id):
    if id[2] == "W":
        pythonGraph.draw_image("images/M-W.png", x, y, width, height)
    elif id[2] == "N":
        pythonGraph.draw_image("images/M-N.png", x, y, width, height)
    elif id[2] == "E":
        pythonGraph.draw_image("images/M-E.png", x, y, width, height)
    elif id[2] == "S":
        pythonGraph.draw_image("images/M-S.png", x, y, width, height)

def draw_explosion(x,y, width,height):
    pythonGraph.draw_image("images/E.png", x, y, width, height)
def draw_countermeasure(x,y, width,height):
    pythonGraph.draw_image("images/C.png", x, y, width, height)

def draw_air_defense(x,y, width,height, id):
    filename = str("images/" + id + ".png")
    pythonGraph.draw_image(filename, x, y, width, height)
def draw_air_base(x,y, width,height, id):
    filename = str("images/" + id + ".png")
    pythonGraph.draw_image(filename, x, y, width, height)
    
def draw_terrain(x,y, width,height, id):
    filename = str("images/" + id + ".png")
    pythonGraph.draw_image(filename, x, y, width,height)
    
def draw_world(field_of_view, scr_width, scr_height, player_view_radius):
    x=0; y=0
    num_rows = len(field_of_view[0])
    num_col = len(field_of_view)
    
    grid_height = scr_height / num_rows
    grid_width = scr_width / num_rows
    #grid_size = scr_height/(player_view_radius * 2 + 1)
    
    #i will store the current row number, not the row data
    #field_of_view[i][j].append("FFN")
    for y in range(num_rows):
        #j does the same for columns
        for x in range(num_col):
            for sym in field_of_view[y][x]:
                #ensure program doesn't crash if there is a blank area in array
                if str(sym) == "":
                    continue
                #planes
                if sym[0] == 'B':
                    draw_bomber((x*grid_width), (y*grid_height), grid_width, grid_height, sym)
                elif sym[0] == 'I':
                    draw_recon((x*grid_width), (y*grid_height), grid_width, grid_height, sym)
                elif sym[0] == 'F':
                    draw_fighter((x*grid_width), (y*grid_height), grid_width, grid_height, sym)
                #bases
                elif sym[0] == 'A':
                    draw_air_base((x*grid_width), (y*grid_height), grid_width, grid_height, sym)
                elif sym[0] == 'D':
                    draw_air_defense((x*grid_width), (y*grid_height), grid_width, grid_height, sym)
                #weapon entities
                elif sym == 'C':
                    draw_countermeasure((x*grid_width), (y*grid_height), grid_width, grid_height)
                elif sym == 'E':
                    draw_explosion((x*grid_width), (y*grid_height), grid_width, grid_height)
                elif sym[0] == 'M' and len(sym) == 3:
                    draw_missile((x*grid_width), (y*grid_height), grid_width, grid_height, sym)
                #all terrain tiles
                elif sym == "G" or sym =="F" or sym =="W" or sym == "O" or sym == "M" or sym == "S":
                    draw_terrain((x*grid_width), (y*grid_height), grid_width, grid_height, sym)
                #draw "boundary" tiles on any null areas
                else:
                    draw_terrain((x*grid_width), (y*grid_height), grid_width, grid_height, 'N')

def draw_hud(x,y):
    pythonGraph.draw_text("coordinates: " + str(x) + ", " + str(y), 5, 5, "white", 24)
    pythonGraph.draw_text("target: " + str(simulation.target), 5, 20, "white", 24)
    pythonGraph.draw_text("fuel: " + str(simulation.fuel), 5, 35, "white", 24)
    pythonGraph.draw_text("a2a: " + str(simulation.a2a) + "; a2g: " + str(simulation.a2g) + "; bombs: " + str(simulation.bombs) + "; cm's: " + str(simulation.countermeasures), 5, 50, "white", 24)
