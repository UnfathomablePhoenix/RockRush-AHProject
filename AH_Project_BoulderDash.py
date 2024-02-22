#!/usr/bin/env python
# Example file showing a circle moving on screen
import pygame
#https://www.pygame.org/wiki/Spritesheet
from spritesheet import spritesheet
#https://docs.python.org/3/library/wave.html
import time
import database

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True
dt = 0

#declaring other global variables
scoreTime = 200
objectMap = None
score = 0
screenDisplace_x = 0
screenDisplace_y = 0
playerPos = pygame.Vector2()
levelNo = 1
start = False

ss_image_size = 12
scaling_factor = 4
ss = spritesheet('GameArt/OpenArt-RockRush/Raw/tileset.png')


# Sprite is 16x16 pixels at location 0,0 in the file...
def get_spritesheet_image(x, y):
  #gets the placements for the sprite sheet
  x *= ss_image_size
  y *= ss_image_size
  return ss.image_at((x, y, ss_image_size, ss_image_size))

def dead():
  #a procedure for if the player is killed/crushed.
  global start
  start = False
  #screen.fill("Black")
  font = pygame.font.Font('freesansbold.ttf', 100)
  text = font.render("You Lose. " + "Score: " + str(score), True, "white")
  textRect = text.get_rect()
  textRect.topleft = (50, 50)
  screen.blit(text, textRect)
  pygame.display.flip() 
  time.sleep(5)

def win(): 
  #a procedure for if the player manages to reach the exit
  #ends current run and displays win screen, then gets name and saves score to database
  global start
  global score
  global scoreTime
  start = False
  score += float(round(scoreTime) * 1)
  screen.fill("Black")
  font = pygame.font.Font('freesansbold.ttf', 100)
  text = font.render("You Win. " + "Score: " + str(round(score,0)), True, "white")
  textRect = text.get_rect()
  textRect.topleft = (50, 50)
  screen.blit(text, textRect)
  pygame.display.flip() 
  time.sleep(5)
  getName = False
  nameInput = ""
  while not getName:

    screen.fill("Black")
    text = font.render("Enter Name.", True, "white")
    textRect = text.get_rect()
    textRect.topleft = (50, 50)
    screen.blit(text, textRect)

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
          if nameInput != "":
            getName = True
        elif event.key == pygame.K_BACKSPACE:
          if nameInput == "":
            pass
          else:
            nameInput = nameInput[0:(len(nameInput) - 1)]
        elif 'a' <= event.unicode <= 'z' or 'A' <= event.unicode <= 'Z':
            nameInput += event.unicode

    text = font.render(nameInput, True, "white")
    textRect = text.get_rect()
    textRect.topleft = (50, 180)
    screen.blit(text, textRect)
    pygame.display.flip() 

  database.putInDatabase(nameInput,score)
  
  #https://stackoverflow.com/questions/46390231/how-can-i-create-a-text-input-box-with-pygame
  #https://github.com/Nearoo/pygame-text-input



# person 2,12 - diamond 3,12 - boulder 0, 17 - dirt 1,1
#image = get_spritesheet_image(0, 17)
#image = pygame.transform.scale(image, (ss_image_size*scaling_factor, ss_image_size*scaling_factor))

#gets the screen dimentions to base the sprite positions off of

sprite_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
screen_dimensions = pygame.Vector2(screen.get_width(), screen.get_height())


class sprite():
  #class for the sprites to be displayed on screen 
  def __init__(self, xcoord, ycoord):
    self.xcoord = xcoord
    self.ycoord = ycoord

  def draw(self):
    sprite_pos.x = (((self.xcoord - 1 - screenDisplace_x) * 48) + 48)
    sprite_pos.y = (((self.ycoord - 1 - screenDisplace_y) * 48) + 49)
    screen.blit(self.image, (sprite_pos.x, sprite_pos.y))

  def update(self, dt):
    pass


class fallingSprite(sprite):
  #subclass of sprite for all falling objects
  def __init__(self, xcoord, ycoord):
    super().__init__(xcoord, ycoord)
    #Accumilated time
    self.acct = 0
    self.crush = False

  #code to check the area around the player and make the boulder move if it can
  def update(self, dt):
    self.acct += dt

    if self.acct >= 0.5:
      self.acct -= 0.5
      #print(self.ycoord,self.xcoord,type(objectMap[self.ycoord][self.xcoord]))
      if type(objectMap[self.ycoord + 1][self.xcoord]) == Empty or type(objectMap[self.ycoord + 1][self.xcoord]) == Player:
        if type(objectMap[self.ycoord + 1][self.xcoord]) == Player and self.crush == True:
          dead()
        elif type(objectMap[self.ycoord + 1][self.xcoord]) == Empty:
          objectMap[self.ycoord +
                    1][self.xcoord] = objectMap[self.ycoord][self.xcoord]
          objectMap[self.ycoord][self.xcoord] = Empty(self.ycoord, self.xcoord)
          self.ycoord += 1
          self.crush = True


      elif (type(objectMap[self.ycoord + 1][self.xcoord + 1])
            == Empty) and (type(objectMap[self.ycoord][self.xcoord + 1])
                           == Empty) and (issubclass(
                               type(objectMap[self.ycoord + 1][self.xcoord]),
                               fallingSprite)):
        #else if next to & diagonal
        objectMap[self.ycoord][self.xcoord +
                               1] = objectMap[self.ycoord][self.xcoord]
        objectMap[self.ycoord][self.xcoord] = Empty(self.ycoord, self.xcoord)
        self.xcoord += 1

      elif (type(objectMap[self.ycoord + 1][self.xcoord - 1])
            == Empty) and (type(objectMap[self.ycoord][self.xcoord - 1])
                           == Empty) and (issubclass(
                               type(objectMap[self.ycoord + 1][self.xcoord]),
                               fallingSprite)):
        objectMap[self.ycoord][self.xcoord -
                               1] = objectMap[self.ycoord][self.xcoord]
        objectMap[self.ycoord][self.xcoord] = Empty(self.ycoord, self.xcoord)
        self.xcoord -= 1

      else:
        self.crush = False


class boulder(fallingSprite):
  #a class of falling sprite which is specific to boulders
  def __init__(self, xcoord, ycoord):
    super().__init__(xcoord, ycoord)
    self.image = get_spritesheet_image(0, 17)
    self.image = pygame.transform.scale(
        self.image,
        (ss_image_size * scaling_factor, ss_image_size * scaling_factor))


class dirt(sprite):
  #a class of sprite which is specific to dirt
  def __init__(self, xcoord, ycoord):
    super().__init__(xcoord, ycoord)
    self.image = get_spritesheet_image(1, 1)
    self.image = pygame.transform.scale(
        self.image,
        (ss_image_size * scaling_factor, ss_image_size * scaling_factor))


class SolidWall(sprite):
  #a class of sprite which is specific to unbreakable walls
  def __init__(self, xcoord, ycoord):
    super().__init__(xcoord, ycoord)
    self.image = get_spritesheet_image(4, 0)
    self.image = pygame.transform.scale(
        self.image,
        (ss_image_size * scaling_factor, ss_image_size * scaling_factor))


class Gem(fallingSprite):
  #a class of sprite which is specific to gems 
  def __init__(self, xcoord, ycoord):
    super().__init__(xcoord, ycoord)
    self.image = get_spritesheet_image(3, 12)
    self.image = pygame.transform.scale(
        self.image,
        (ss_image_size * scaling_factor, ss_image_size * scaling_factor))


class Player(sprite):
  #a class of sprite which is specific to the player and can move via the wasd keys and the arrow keys.
  def __init__(self, xcoord, ycoord):
    super().__init__(xcoord, ycoord)
    self.image = get_spritesheet_image(2, 12)
    self.image = pygame.transform.scale(
        self.image,
        (ss_image_size * scaling_factor, ss_image_size * scaling_factor))
    self.acct = 0

  def update(self, dt):
    self.acct += dt
    global score
    global playerPos
    global levelNo
    global scoreTime

    if self.acct >= 0.3 and pygame.key.get_pressed():
      self.acct = 0
      keys = pygame.key.get_pressed()
      #print(self.ycoord,self.xcoord,type(objectMap[self.ycoord][self.xcoord]))
      if (type(objectMap[self.ycoord + 1][self.xcoord]) != boulder
          and type(objectMap[self.ycoord + 1][self.xcoord]) != SolidWall) and (
              keys[pygame.K_s] or keys[pygame.K_DOWN]):
        if type(objectMap[self.ycoord + 1][self.xcoord]) == Gem:
          score += 10
        elif type(objectMap[self.ycoord + 1][self.xcoord]) == Exit:
          win()
        objectMap[self.ycoord +
                  1][self.xcoord] = objectMap[self.ycoord][self.xcoord]
        objectMap[self.ycoord][self.xcoord] = Empty(self.ycoord, self.xcoord)
        self.ycoord += 1
      elif (type(objectMap[self.ycoord - 1][self.xcoord]) != boulder
            and type(objectMap[self.ycoord - 1][self.xcoord]) != SolidWall
            ) and (keys[pygame.K_w] or keys[pygame.K_UP]):
        if type(objectMap[self.ycoord - 1][self.xcoord]) == Gem:
          score += 10
        elif type(objectMap[self.ycoord - 1][self.xcoord]) == Exit:
          win()
        objectMap[self.ycoord -
                  1][self.xcoord] = objectMap[self.ycoord][self.xcoord]
        objectMap[self.ycoord][self.xcoord] = Empty(self.ycoord, self.xcoord)
        self.ycoord -= 1
      elif (type(objectMap[self.ycoord][self.xcoord + 1]) != boulder
            and type(objectMap[self.ycoord][self.xcoord + 1]) != SolidWall
            ) and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
        if type(objectMap[self.ycoord][self.xcoord + 1]) == Gem:
          score += 10
        elif type(objectMap[self.ycoord][self.xcoord + 1]) == Exit:
          win()
        objectMap[self.ycoord][self.xcoord +
                               1] = objectMap[self.ycoord][self.xcoord]
        objectMap[self.ycoord][self.xcoord] = Empty(self.ycoord, self.xcoord)
        self.xcoord += 1
      elif (type(objectMap[self.ycoord][self.xcoord - 1]) != boulder
            and type(objectMap[self.ycoord][self.xcoord - 1]) != SolidWall
            ) and (keys[pygame.K_a] or keys[pygame.K_LEFT]):
        if type(objectMap[self.ycoord][self.xcoord - 1]) == Gem:
          score += 10
        elif type(objectMap[self.ycoord][self.xcoord - 1]) == Exit:
          win()
        objectMap[self.ycoord][self.xcoord -
                               1] = objectMap[self.ycoord][self.xcoord]
        objectMap[self.ycoord][self.xcoord] = Empty(self.ycoord, self.xcoord)
        self.xcoord -= 1
      else:  
        pass
      playerPos.xy = self.xcoord, self.ycoord
    if self.acct > 10:
      self.acct = 0.3


class Exit(sprite):
  #a class of sprite which is specific to the exit
  def __init__(self, xcoord, ycoord):
    super().__init__(xcoord, ycoord)
    self.image = get_spritesheet_image(2, 7)
    self.image = pygame.transform.scale(
        self.image,
        (ss_image_size * scaling_factor, ss_image_size * scaling_factor))

  def addScore(self):
    pass

class Empty(sprite):
  #a class of sprite which is specific to air/nothing
  def __init__(self, xcoord, ycoord):
    super().__init__(xcoord, ycoord)
    self.image = get_spritesheet_image(10, 4)
    self.image = pygame.transform.scale(
        self.image,
        (ss_image_size * scaling_factor, ss_image_size * scaling_factor))


def readMap():
  #reads CSV file contence to get map
  global levelNo
  Map = []
  #if levelNo == 1:
  file1 = open("TiledMaps/Map1.csv", "r")
  lines = file1.readlines()
  for row in lines:
    row = row.strip()
    list_of_strings = row.split(",")
    #print(list_of_strings)
    # https://stackoverflow.com/questions/6429638/how-to-split-a-string-of-space-separated-numbers-into-integers
    list_of_ints = list(map(int, list_of_strings))
    #print(list_of_ints)
    Map.append(list_of_ints)
    #print(Map)
    #Map.append(map(int, row.split(,)))

  file1.close()
  return Map


def elementToXY(element):
  x = element % 20
  y = element // 20
  return x, y


TileConverter = {
    #a dictionary to convert the csv extracted text to a 2d object array(list)
    4: SolidWall,
    25: SolidWall,
    21: dirt,
    29: dirt,
    340: boulder,
    243: Gem,
    242: Player,
    142: Exit
}


def converterMap(integer_map):
  #to convert the map from text to a 2d array of objects
  real_map = []
  position_y = 0
  for line in integer_map:
    object_line = []
    position_x = 0
    for element in line:
      if element in TileConverter:
        object_class = TileConverter[element]
        # do something
      else:
        object_class = boulder
      #x,y = elementToXY(element)
      object_line.append(object_class(position_x, position_y))
      position_x += 1
    real_map.append(object_line)
    position_y += 1

  return real_map


tempMap = readMap()
objectMap = converterMap(tempMap)

#test code which I should proably delete
#Boulder1 = boulder(1,1)
#Boulder2 = boulder(2,1)
#Boulder3 = boulder(3,2)
#Boulder4 = boulder(4,3)
#Boulder5 = boulder(5,4)
#Dirt1 = dirt(3,1)

#---- boulder_fall_test_code ------
#objectMap[3][4] = Empty(3,4)
#objectMap[4][4] = Empty(4,4)
#-------------- end ---------------


def Hud(dt):
  #to print the hud on the screen with the current score and time on it
  global levelNo
  global scoreTime
  
  scoreTime -= dt

  font = pygame.font.Font('freesansbold.ttf', 32)
  text = font.render("Score: " + str(score), True, "black")
  textRect = text.get_rect()
  textRect.topleft = (10, 10)
  screen.blit(text, textRect)
  text = font.render("Time:" + str(int(round(scoreTime,0))), True, "black")
  textRect = text.get_rect()
  textRect.topleft = (200, 10)
  screen.blit(text, textRect)

def mainMenuSubText(Pos):
  #to figure out the main menu sub test position
  mainMenuSubText = 10 + (60*(Pos-1) + 160)
  return mainMenuSubText

def menuText():
  #to display the main menu text on the screen
  screen.fill("brown")

  Pos = 0
  title = pygame.Vector2(10, 10)

  font = pygame.font.Font('freesansbold.ttf', 100)
  text = font.render("Rock Rush", True, "white")
  textRect = text.get_rect()
  textRect.topleft = title
  screen.blit(text, textRect)

  Pos = 1
  font = pygame.font.Font('freesansbold.ttf', 50)
  text = font.render("Start : Space", True, "green")
  textRect = text.get_rect()
  textRect.topleft = (10,mainMenuSubText(Pos))
  screen.blit(text, textRect)

  Pos = 2
  font = pygame.font.Font('freesansbold.ttf', 50)
  text = font.render("LeaderBoard : L", True, "yellow")
  textRect = text.get_rect()
  textRect.topleft = (10,mainMenuSubText(Pos))
  screen.blit(text, textRect)

  Pos = 3
  font = pygame.font.Font('freesansbold.ttf', 50)
  text = font.render("Quit : esc", True, "orange")
  textRect = text.get_rect()
  textRect.topleft = (10,mainMenuSubText(Pos))
  screen.blit(text, textRect)

  pygame.display.flip()
  
def leaderboard():
  #to display the leaderboard on the screen after extracting the data from the leaderboard database- "scores.db"
  numRowsDisplay = 8
  runLeaderBoard = True 
  rows = database.takeOutDatabase()
  lenRows = len(rows)
  if lenRows > numRowsDisplay:
    lenRows = numRowsDisplay 


  screen.fill("Purple")
  font = pygame.font.Font('freesansbold.ttf', 50)
  text = font.render("Leaderboard", True, "green")
  textRect = text.get_rect()
  textRect.topleft = (10,10)
  screen.blit(text, textRect)

  
  for i in range(0,lenRows):
    scoreForDisplay = rows[i][0] + "/t" + rows[i][1] + "/t" + rows [i][2]
    font = pygame.font.Font('freesansbold.ttf', 50)
    text = font.render(scoreForDisplay, True, "green")
    textRect = text.get_rect()
    textRect.topleft = (10,(i * 50) + 70)
    screen.blit(text, textRect)

  pygame.display.flip()
  while runLeaderBoard:
    if pygame.key.get_pressed():
      keys = pygame.key.get_pressed()
      if keys[pygame.K_p]:
        runLeaderBoard = False



while running:
  #the main loop of the program
  start = False
  tempMap = readMap()
  objectMap = converterMap(tempMap)
  scoreTime = 200
  dt = clock.tick(60) / 1000
  score = 0
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  menuText()

  #a detection method to get the current key that is pressed
  #should test if multiple keys are pressed at once --- --- --- --- --- --- --- --- --- 
  if pygame.key.get_pressed():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
      running = False
    elif keys[pygame.K_SPACE]:
      start = True
    elif keys[pygame.K_l]:
     leaderboard()#LeaderBoard Link Code 

  
    pass
  while start:
    # the loop of the actual game in which the player can move about the screen
    # pygame.QUIT event means the user clicked X to close your window - checks if the program has been closed
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        start = False
        break

    #if the time runs out you go back to the menu
    if scoreTime <= 0:
      start = False
      dead()


    # fill the screen with black color to wipe away anything from last frame
    screen.fill("black")

    # loop to draw the sprites on the screen
    for line in objectMap:
      for column in line:
        column.draw()

    # to find the change in time between frames
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate.
    dt = clock.tick(60) / 1000

    # displays hud
    Hud(dt)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # updates all of the sprites on the screen. 
    for line in objectMap:
      for column in line:
        column.update(dt)

pygame.quit()
'''
https://stackoverflow.com/questions/10560446/how-do-you-select-a-sprite-image-from-a-sprite-sheet-in-python

https://www.pygame.org/wiki/Spritesheet

https://stackoverflow.com/questions/20109487/how-do-i-use-sprite-sheets-in-pygame

https://www.pygame.org/docs/ref/sprite.html

https://www.pygame.org/wiki/Spritesheet

----------- IMPORTANT ------------

https://www.mapeditor.org/

https://opengameart.org/content/rock-rush-tiles-sprites-hud-backgrounds

'''