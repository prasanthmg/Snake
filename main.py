import pygame 
import random
import os

GAME_NAME = "Snake"
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300
SCREEN_COLOR = (100, 100, 100)
SNAKE_LENGTH = 20
SNAKE_COLOR = (200, 200, 0)
FOOD_COLOR = (255, 255, 255)
PADDING = {'top': 5, 'bottom': 5, 'left': 5, 'right': 5}

class Game:
	def __init__(self):
		pygame.display.set_caption(GAME_NAME)
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.snake = Snake()
		self.food = Food()
		self.padding_top = Padding(side='T')
		self.padding_bottom = Padding(side='B')
		self.padding_left = Padding(side='L')
		self.padding_right = Padding(side='R')
		self.scoreboard = Scoreboard()
		self.clock = pygame.time.Clock()
		self.game_over = False
		self.paused = False
		self.resume_time = 0
		self.game_over_blanket = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
		self.replay_button = ReplayButton()
		# Sound source  : https://freesound.org/people/FartBiscuit1700/sounds/368691/
		self.game_start_sound = pygame.mixer.Sound(os.path.join('sounds','game_start.ogg'))

		# Sound source  : https://freesound.org/people/jeckkech/sounds/391666/
		self.eat_sound = pygame.mixer.Sound(os.path.join('sounds','eat.ogg'))

		# Sound source  : https://freesound.org/people/MentosLat/sounds/417486/
		self.game_over_sound = pygame.mixer.Sound(os.path.join('sounds','game_over.ogg'))
		self.all_sprites, self.padding_sprites = self.get_all_sprite_groups()

	def start(self):
		self.draw()
		self.pause()
		while True:
			event_queue = pygame.event.get()
			for event in event_queue:
				if event.type==pygame.QUIT:
					self.stop()
			if self.paused:
				if(pygame.time.get_ticks() >= self.resume_time):
					self.paused = False
					self.game_start_sound.play()
					pygame.mouse.set_visible(False)
			elif self.game_over:
				if self.replay_button.rect.collidepoint(pygame.mouse.get_pos()):
					self.replay_button.highlight()
				else:
					self.replay_button.reset()
				self.screen.blit(self.replay_button.image, self.replay_button.rect)
				pygame.display.flip()                
				for event in event_queue:
					if (event.type==pygame.MOUSEBUTTONDOWN) and (event.button==1) and (self.replay_button.rect.collidepoint(event.pos)):
						self.replay_button.mouse_down_flag = True
					elif (event.type==pygame.MOUSEBUTTONUP) and (event.button==1) and (self.replay_button.rect.collidepoint(event.pos)) and self.replay_button.mouse_down_flag:
						self.play_again()
						self.replay_button.reset()
						break
			else:
				if self.snake_collide_with_boundary() or self.snake_eats_self():
					self.game_over_sound.play()
					self.draw_game_over()
					self.game_over = True
					continue
				if self.snake_eats_food():
					self.eat_sound.play()
					self.scoreboard.increment_score()
					self.all_sprites.add(self.snake.grow())
					self.food.randomize(self.snake)
				for event in event_queue:
					if event.type==pygame.KEYDOWN:
						self.snake.turn(event.key)
				self.snake.move()
				self.draw()
				self.clock.tick(40)

	def get_all_sprite_groups(self):
		padding_sprites = pygame.sprite.Group()
		padding_sprites.add(self.padding_top, self.padding_bottom, self.padding_left, self.padding_right)
		all_sprites = padding_sprites.copy()
		all_sprites.add(self.scoreboard)
		all_sprites.add(self.snake.sprites())
		all_sprites.add(self.food)
		return all_sprites, padding_sprites


	def draw(self):
		self.screen.fill(SCREEN_COLOR)
		self.all_sprites.draw(self.screen)
		pygame.display.flip()

	def stop(self):
		pygame.quit()
		quit()

	def snake_collide_with_boundary(self):
		return pygame.sprite.spritecollideany(self.snake.get_head(), self.padding_sprites)

	def snake_eats_self(self):
		return pygame.sprite.spritecollideany(self.snake.get_head(), self.snake.get_tail())

	def snake_eats_food(self):
		return self.food.rect.colliderect(self.snake.get_head().rect)

	def draw_game_over(self):
		score_dialogue = pygame.font.SysFont('monospace', 40, bold=True).render('Your Score:'+ str(self.scoreboard.score), 1, (0, 0, 0),)
		self.game_over_blanket.fill((200, 255, 255, 150))
		self.game_over_blanket.blit(score_dialogue, ((SCREEN_WIDTH - score_dialogue.get_width())/2, SCREEN_HEIGHT/2 - score_dialogue.get_height()))        
		self.game_over_blanket.blit(self.replay_button.image, self.replay_button.rect)
		self.screen.blit(self.game_over_blanket,(0,0))
		pygame.display.flip()
		pygame.mouse.set_visible(True)

	def pause(self):
		self.resume_time = pygame.time.get_ticks() + 1000
		self.paused = True

	def play_again(self):
		self.game_over = False
		self.scoreboard.reset()
		self.all_sprites.remove(self.snake.sprites())
		self.snake.reset()
		self.all_sprites.add(self.snake.sprites())
		self.draw()
		self.pause()

class Food(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.size = 5
		self.image = pygame.Surface((2*self.size, 2*self.size))
		self.image.fill(SCREEN_COLOR)
		pygame.draw.circle(self.image, FOOD_COLOR, (self.size, self.size), self.size)
		topleft = (random.randint(PADDING['left'] +2, SCREEN_WIDTH - PADDING['right'] - 2*self.size -2), random.randint(PADDING['top'] +2, SCREEN_HEIGHT - PADDING['bottom'] - 2*self.size -2))
		self.rect = self.image.get_rect(topleft=topleft)

	def randomize(self, snake):
		while pygame.sprite.spritecollideany(self, snake):
			topleft = (random.randint(PADDING['left'] +2, SCREEN_WIDTH - PADDING['right'] - 2*self.size -2), random.randint(PADDING['top'] +2, SCREEN_HEIGHT - PADDING['bottom'] - 2*self.size -2))
			self.rect = self.image.get_rect(topleft=topleft)

class Snake(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.starting_position = (PADDING['left']+10, SCREEN_HEIGHT/2)
		self.direction = 'right'
		self.speed = SnakePixel().size
		self.head = SnakePixel(self.starting_position)
		self.tail = pygame.sprite.Group()
		for i in range(1,SNAKE_LENGTH):
			self.tail.add(SnakePixel((self.starting_position[0]-i*self.speed, self.starting_position[1])))
		self.add(self.head)
		self.add(self.tail.sprites())

	def get_head(self):
		return self.head

	def get_tail(self):
		return self.tail

	def turn(self, key):
		if (key==pygame.K_UP) and (self.direction!='down'):
			self.direction = 'up'
		elif (key==pygame.K_DOWN) and (self.direction!='up'):
			self.direction = 'down'
		elif (key==pygame.K_RIGHT) and (self.direction!='left'):
			self.direction = 'right'
		elif (key==pygame.K_LEFT) and (self.direction!='right'):
			self.direction = 'left'

	def advance_head(self):
		if self.direction=='up':
			self.head.rect.move_ip(0, -self.speed)
		elif self.direction=='down':
			self.head.rect.move_ip(0, self.speed)
		elif self.direction=='right':
			self.head.rect.move_ip(self.speed, 0)
		elif self.direction=='left':
			self.head.rect.move_ip(-self.speed, 0)
		
	def move(self):
		topleft = self.head.rect.topleft
		self.advance_head()
		for tail_sprite in self.tail.sprites():
			tail_sprite.rect.topleft, topleft = topleft, tail_sprite.rect.topleft

	def grow(self):
		topleft = self.head.rect.topleft
		self.advance_head()
		new_tail_sprite = SnakePixel(topleft)
		new_tail = pygame.sprite.Group()
		new_tail.add(new_tail_sprite)
		new_tail.add(self.tail.sprites())
		self.tail = new_tail
		self.add(new_tail_sprite)
		return new_tail_sprite

	def reset(self):
		self.empty()
		self.head.rect.topleft = self.starting_position
		self.tail.empty()
		for i in range(1,SNAKE_LENGTH):
			self.tail.add(SnakePixel((self.starting_position[0]-i*self.speed, self.starting_position[1])))
		self.add(self.head)
		self.add(self.tail.sprites())
		self.direction = 'right'

class SnakePixel(pygame.sprite.Sprite):
	def __init__(self, topleft=(0,0)):
		super().__init__()
		self.size = 6
		self.image = pygame.Surface((self.size, self.size))
		self.image.fill(SNAKE_COLOR)
		self.rect = self.image.get_rect(topleft=topleft)

class Scoreboard(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.font_color = (200,200,200)
		self.font_name = 'monospace'
		self.font_height = 40
		self.font = pygame.font.SysFont(self.font_name, self.font_height)
		self.score = 0
		self.image = self.font.render(str(self.score), 1, self.font_color)
		topleft = (SCREEN_WIDTH - PADDING['right'] - self.image.get_width() -2, PADDING['top'])
		self.rect = self.image.get_rect(topleft=topleft)

	def update(self, score):
		self.score = score
		self.image = self.font.render(str(self.score), 1, self.font_color)
		topleft = (SCREEN_WIDTH - PADDING['right'] - self.image.get_width() -2, PADDING['top']) 
		self.rect = self.image.get_rect(topleft=topleft)

	def reset(self):
		self.update(0)

	def increment_score(self):
		self.update(self.score + 1)

class Padding(pygame.sprite.Sprite):
	def __init__(self, side):
		super().__init__()
		self.color = (160, 160, 160)
		if side=='L':
			self.image = pygame.Surface((PADDING['left'], SCREEN_HEIGHT - PADDING['top'] - PADDING['bottom']))
			self.image.fill(self.color)
			self.topleft = (0, PADDING['top'])
		elif side=='R':
			self.image = pygame.Surface((PADDING['right'], SCREEN_HEIGHT - PADDING['top'] - PADDING['bottom']))
			self.image.fill(self.color)
			self.topleft = (SCREEN_WIDTH - PADDING['right'], PADDING['top'])
		elif side=='T':
			self.image = pygame.Surface((SCREEN_WIDTH, PADDING['top']))
			self.image.fill(self.color)
			self.topleft = (0, 0)
		else:
			self.image = pygame.Surface((SCREEN_WIDTH, PADDING['bottom']))
			self.image.fill(self.color)
			self.topleft = (0, SCREEN_HEIGHT - PADDING['bottom'])
		self.rect = self.image.get_rect(topleft=self.topleft)

class ReplayButton():
	def __init__(self):
		self.font_name = 'monospace'
		self.font_height = 20
		self.image = pygame.font.SysFont(self.font_name, self.font_height, bold=True).render('>>Play again<<', 1, (200, 200, 0), (255, 0, 0))
		self.topleft = ((SCREEN_WIDTH - self.image.get_width())/2, SCREEN_HEIGHT/2)
		self.rect = self.image.get_rect(topleft=self.topleft)
		self.mouse_down_flag = False

	def highlight(self):
		self.image = pygame.font.SysFont(self.font_name, self.font_height, bold=True).render('>>Play again<<', 1, (255, 255, 0), (200, 0, 0))

	def reset(self):
		self.image = pygame.font.SysFont(self.font_name, self.font_height, bold=True).render('>>Play again<<', 1, (200, 200, 0), (255, 0, 0))
		self.mouse_down_flag = False

pygame.init()
Game().start()




