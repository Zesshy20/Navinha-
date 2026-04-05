import pygame
import sys
import numpy as np
import time

from pygame.locals import *

WIDTH,HEIGHT = 600,900
SIZE = 20
SPEED = 5
NUM_MAX_ENEMIES = 8

dicionario_key_pressed = {
	pygame.K_LEFT: (-SPEED,0),
	pygame.K_RIGHT : (SPEED,0),
	pygame.K_UP: (0,-SPEED),
	pygame.K_DOWN: (0,SPEED)
}

CORES = [(255,255,255),(255,0,0),(0,255,0),(0,0,255),(255,0,255)]


Lista_coordenadas_inimigo = [
	[(0,0),(2*SIZE,0),(SIZE,2*SIZE)],
	[(0,SIZE),(SIZE,2*SIZE),(2*SIZE,SIZE),(SIZE,0)]
]

class Enemy(pygame.sprite.Sprite):
	def __init__(self, enemy_sprites, space_sprite):
		super().__init__()
		self.center_x = np.random.randint(low=20,high=WIDTH-100)
		self.limit_x_right = self.center_x*(1+np.random.randint(low=30,high=50)/100)
		self.limit_x_left = self.center_x*(1-np.random.randint(low=30,high=50)/100)
	
		self.center_y = SIZE 

		self.image    = pygame.Surface((SIZE*2,SIZE*2))
		self.poligono = Lista_coordenadas_inimigo[np.random.randint(low=0,high=len(Lista_coordenadas_inimigo))]
		cor = CORES[np.random.randint(low=0,high=len(CORES))]
		pygame.draw.polygon(self.image, cor, self.poligono)
		self.rect = self.image.get_rect(center=(self.center_x,self.center_y))
			
		self.speed_y = SPEED*(1+np.random.randint(low=-50,high=50)/100)
		self.speed_x = SPEED*(1+np.random.randint(low=-50,high=50)/100)
		self.controle_x = np.random.randint(low=-1,high=1)
		self.space_ship = space_sprite

	def estou_na_tela(self):
		if self.rect.y + 2*SIZE >= HEIGHT:
			return False
		return True

	def update(self):
		self.rect.y += self.speed_y
		self.rect.x += self.controle_x*self.speed_x
		
		if (self.rect.x >= self.limit_x_right):
				self.controle_x = -1.0
		if self.rect.x <= self.limit_x_left:
				self.controle_x = +1.0

		group_temp = pygame.sprite.Group()
		group_temp.add(self.space_ship)
		hits = pygame.sprite.spritecollide(self,group_temp,dokill=False)
		for other in hits:
			if other != self:
				self.space_ship.bateu = True
	

NUM_MAX_SHOT = 7
SHOT_WIDTH,SHOT_HEIGHT = 5,10
SHOT_SPEED = 5
CONTADOR = 0
class Shot(pygame.sprite.Sprite):

	def __init__(self, center_x, center_y, enemies_sprites):
		super().__init__()
		self.center_x = center_x+SIZE 
		self.center_y = center_y

		self.image = pygame.Surface((SHOT_WIDTH,SHOT_HEIGHT))
		self.retangulo = [(0,0),(0,SHOT_HEIGHT),(SHOT_WIDTH,SHOT_HEIGHT),(SHOT_WIDTH,0)]
		pygame.draw.polygon(self.image, (255,255,255),self.retangulo)
		self.rect = self.image.get_rect(center=(self.center_x,self.center_y))
		
		self.speed = SHOT_SPEED
		self.enemy_sprites = enemy_sprites
	
	def estou_na_tela(self):
		if self.rect.y + 2*SIZE <= 0:
			return False
		return True

	def update(self):
		self.rect.y -= self.speed

		hits = pygame.sprite.spritecollide(self, self.enemy_sprites, dokill=True)
		for other in hits:
			if other != self:
				global CONTADOR 
				CONTADOR += 1

class SpaceShip(pygame.sprite.Sprite):
	
	def __init__(self, enemy_sprites):
		super().__init__()
		self.center_x = WIDTH//2 
		self.center_y = int(HEIGHT*0.90)

		self.image = pygame.Surface((SIZE*2,SIZE*2))
		self.triangle_points = [(SIZE,0),(0,SIZE*2),(SIZE*2,SIZE*2) ]
		pygame.draw.polygon(self.image, (255,255,255), self.triangle_points)
		self.rect = self.image.get_rect(center=(self.center_x,self.center_y))
		
		self.speed = SPEED
		self.bateu = False
		self.enemies_sprites = enemy_sprites

	def update(self, key):	
		dx,dy = dicionario_key_pressed[key]

		self.rect.x += dx
		self.rect.y += dy

		if self.rect.x < 0:
			self.rect.x = 0
		if self.rect.x + 2*SIZE > WIDTH:
			self.rect.x = WIDTH - 2*SIZE
		if self.rect.y < 0:
			self.rect.y = 0
		if self.rect.y + 2*SIZE > HEIGHT:
			self.rect.y = HEIGHT - 2*SIZE

		hits = pygame.sprite.spritecollide(self, self.enemies_sprites, dokill=False)
		for other in hits:
			if other != self:
				self.bateu = True

	
if __name__ == '__main__':

	pygame.init()
	FramePerSec = pygame.time.Clock()

	surface = pygame.display.set_mode((WIDTH,HEIGHT))
	pygame.display.set_caption('ANCHIETA CCHIIIPS')

	all_sprites = pygame.sprite.Group()
	
	enemy_sprites = pygame.sprite.Group()
	space_ship = SpaceShip(enemy_sprites)
	all_sprites.add(space_ship)

	shot_sprites = pygame.sprite.Group()	

	running = True
	while running:

		if len(enemy_sprites) == 0:
			num_enemies = np.random.randint(low=1,high=NUM_MAX_ENEMIES)
			for _ in range(0,num_enemies):
				enemy = Enemy(enemy_sprites, space_ship)
				enemy_sprites.add(enemy)
				all_sprites.add(enemy)

		eventos = pygame.event.get()
		for evento in eventos:
			if evento.type == QUIT:
				pygame.quit()
				sys.exit()
			if evento.type == KEYDOWN:
				if evento.key == K_SPACE:
					if len(shot_sprites) < NUM_MAX_SHOT:
						shot = Shot(space_ship.rect.x, space_ship.rect.y,enemy_sprites)
						shot_sprites.add(shot)	
						all_sprites.add(shot)

		keys_dicionario = list(dicionario_key_pressed.keys())
		key = pygame.key.get_pressed()
		for k in keys_dicionario: 
			if key[k]:
				space_ship.update(k)
	
		for _ in enemy_sprites:	
			_.update()
			if not _.estou_na_tela():
				all_sprites.remove(_)
				enemy_sprites.remove(_)

		for _ in shot_sprites:
			_.update()
			if not _.estou_na_tela():
				all_sprites.remove(_)
				shot_sprites.remove(_)

		surface.fill((0,0,0))
		all_sprites.draw(surface)
		pygame.display.flip()
		FramePerSec.tick(60)

		print(CONTADOR)
		if space_ship.bateu:
			time.sleep(10)
			all_sprites = pygame.sprite.Group()
			enemy_sprites = pygame.sprite.Group()
			space_ship = SpaceShip(enemy_sprites)
			all_sprites.add(space_ship)
			shot_sprites = pygame.sprite.Group()	

			CONTADOR = 0

