import pygame
from pygame import mixer
from pygame.locals import *
from client import *


client = Client()

threading.Thread(target=client.screen).start()

players = {}


print("in")
mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

FPS = 60
clock= pygame.time.Clock()


def process_message( messages ):
	#print(len(messages))
	for msg in messages:
		if msg["prpse"][0] == 0:
			print(msg["msg"] ,"from",msg["from"])
		else:
			if msg["from"] not in players :
				print("Player created")
				players[msg["from"]] = Player(50, 50, 50, 50, (255, 0, 0))
			
			if msg["prpse"][0] == 1:
				players[msg["from"]].rect = msg["msg"]
				#print("Received:",msg["msg"])
		client.received_message.remove(msg)

class Player:
    def __init__(self, x, y, width, height, color,is_player = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.is_player = is_player
        self.vel = 5
        self.rect = pygame.rect.Rect(x,y,width,height)
        self.keys = [False,False,False,False]

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height))

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[K_LEFT]:
            self.rect.x -= self.vel
        if keys[K_RIGHT]:
            self.rect.x += self.vel
        if keys[K_UP]:
            self.rect.y -= self.vel
        if keys[K_DOWN]:
            self.rect.y += self.vel
        if (len(client.messages)<5 and self.is_player ):
            client.messages.append({"prpse":(1,),"msg":self.rect})
            #print(len(client.messages),self.rect)

    def is_colliding(self, other_rect):
            player_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
            return player_rect.colliderect(other_rect)

# Example Usage
pygame.init()


def game():
	win = pygame.display.set_mode((500, 500))
	pygame.display.set_caption("Player Example")

	player = Player(50, 50, 50, 50, (255, 0, 0),True)

	run = True
	while run:
		clock.tick(FPS)
		process_message(client.received_message)
		#pygame.time.delay(100)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_DOWN:
					player.keys[0] = True 



		win.fill((0, 0, 0))

		player.move()
		for i in players:
			
			if player.is_colliding(players[i]):
				pass
				#print("Collision Detected!")
			players[i].draw(win)

		player.draw(win)
		pygame.display.update()

	pygame.quit()

while True:
	if client.running == True:
		print("Starting main game.")
		threading.Thread(target=game).start()
		break


