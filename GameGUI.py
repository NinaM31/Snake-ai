import pygame
from Constants import *
from Menu import *
from GameController import GameController
from GA import *
import sys


class GameGUI:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.SCREEN_UPDATE = pygame.USEREVENT

        self.speed = 110
        self.speed_up = 80

        pygame.time.set_timer(self.SCREEN_UPDATE, self.speed)

        self.controller = GameController()

        self.running, self.playing = True, False
        self.UPKEY, self.DOWNKEY, self.START, self.BACK = False, False, False, False

        self.SIZE = CELL_SIZE * NO_OF_CELLS
        self.display = pygame.Surface((self.SIZE, self.SIZE))
        self.window = pygame.display.set_mode((self.SIZE, self.SIZE))

        self.font_name = 'SquareAntiqua-Bold.ttf'

        self.main_menu = MainMenu(self)
        self.GA = GAMenu(self, self.controller)
        self.curr_menu = self.main_menu

        self.load_model = False
        self.view_path = False

    def game_loop(self):
        while self.playing:
            self.event_handler()

            if self.BACK:
                self.playing = False

            self.display.fill(WINDOW_COLOR)
            if self.controller.algo != None:
                self.draw_elements()
            self.window.blit(self.display, (0, 0))

            pygame.display.update()
            self.clock.tick(60)
            self.reset_keys()

    def draw_elements(self):
        # draw banner and stats
        self.draw_banner()
        self.draw_game_stats()

        if self.curr_menu.state != 'GA' or self.controller.model_loaded:  # Path Ai or trained GA
            fruit = self.controller.get_fruit_pos()
            snake = self.controller.snake

            self.draw_fruit(fruit)
            self.draw_snake(snake)
            self.draw_score()

            if not self.controller.model_loaded:
                self.draw_path()  # only path Ai has a path

        else:  # training a GA model
            self.draw_all_snakes_GA()

    def draw_game_stats(self):
        if self.curr_menu.state != 'GA':  # path Ai algo
            instruction = 'Space to view Ai path, W to speed up, Q to go back'

        elif self.controller.model_loaded:  # trained model
            instruction = 'W to speed up, Q to go back'

        else:  # training model GA algo
            instruction = 'Space to hide all snakes, W to speed up, Q to go back'
            curr_gen = str(self.controller.curr_gen())
            best_score = str(self.controller.best_GA_score())

            stats_gen = f'Generation: {curr_gen}/{GA.generation}'
            stats_score = f'Best score: {best_score}'
            stats_hidden_node = f'Hidden nodes {Population.hidden_node}'

            # draw stats
            self.draw_text(
                stats_gen, size=20,
                x=3*CELL_SIZE, y=CELL_SIZE - 10,
            )
            self.draw_text(
                stats_score, size=20,
                x=3*CELL_SIZE, y=CELL_SIZE + 20,
            )
            self.draw_text(
                stats_hidden_node, size=20,
                x=self.SIZE / 2, y=CELL_SIZE - 30,
                color=SNAKE_COLOR
            )

        # instruction
        self.draw_text(
            instruction, size=20,
            x=self.SIZE/2, y=(CELL_SIZE * NO_OF_CELLS) - NO_OF_CELLS,
            color=WHITE
        )

        # current Algo Title
        self.draw_text(
            self.curr_menu.state, size=30,
            x=self.SIZE/2, y=CELL_SIZE,
        )

    def draw_all_snakes_GA(self):
        if not self.view_path:  # have all snakes visible by default

            for snake in self.controller.snakes:  # for each snake in list
                self.draw_snake(snake)

                # fruit of each snake
                self.draw_fruit(snake.get_fruit())

    def draw_path(self):
        if self.controller.algo != None and self.view_path:
            for path in self.controller.algo.path:  # for each {x,y} in path
                x = int(path.x * CELL_SIZE)
                y = int(path.y * CELL_SIZE)

                path_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                shape_surf = pygame.Surface(path_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(shape_surf, PATHCOLOR, shape_surf.get_rect())

                pygame.draw.rect(self.display, BANNER_COLOR, path_rect, 1)
                self.display.blit(shape_surf, path_rect)

    def draw_snake_head(self, snake):
        head = snake.body[0]
        self.draw_rect(head, color=SNAKE_HEAD_COLOR)

    def draw_snake_body(self, body):
        self.draw_rect(body, color=SNAKE_COLOR, border=True)

    def draw_rect(self, element, color, border=False):
        x = int(element.x * CELL_SIZE)
        y = int(element.y * CELL_SIZE)

        body_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.display, color, body_rect)

        if border:
            pygame.draw.rect(self.display, WINDOW_COLOR, body_rect, 3)

    def draw_snake(self, snake):
        self.draw_snake_head(snake)  # draw head

        for body in snake.body[1:]:
            self.draw_snake_body(body)  # draw body

    def draw_fruit(self, fruit):
        x = int(fruit.x * CELL_SIZE)
        y = int(fruit.y * CELL_SIZE)

        fruit_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.display, FRUIT_COLOR, fruit_rect)

    def draw_banner(self):
        banner = pygame.Rect(0, 0, self.SIZE, BANNER_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.display, BANNER_COLOR, banner)

    def draw_score(self):
        score_text = 'Score: ' + str(self.controller.get_score())
        score_x = self.SIZE - (CELL_SIZE + 2*len(score_text))
        score_y = CELL_SIZE
        self.draw_text(score_text, 20, score_x, score_y, WINDOW_COLOR)

    def game_over(self):
        again = False

        while not again:
            for event in pygame.event.get():
                if self.is_quit(event):
                    again = True
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        again = True
                        break
                    if event.key == pygame.K_s:
                        again = True
                        self.controller.save_model()
                        break

            self.display.fill(MENU_COLOR)

            # training model results
            if self.curr_menu.state == 'GA' and self.controller.model_loaded == False:
                best_score = self.controller.best_GA_score()
                best_gen = self.controller.best_GA_gen()

                high_score = f'Best snake Score: {best_score} in generation {best_gen}'
                save = 'Press S to save best snake'

                self.draw_text(
                    save, size=30,
                    x=self.SIZE/2, y=self.SIZE/2 + 3*CELL_SIZE,
                    color=FRUIT_COLOR
                )
            else:
                # Path ai or trained model results
                high_score = f'High Score: {self.controller.get_score()}'

            to_continue = 'Enter to Continue'

            self.draw_text(
                high_score, size=35,
                x=self.SIZE/2, y=self.SIZE/2,
            )

            self.draw_text(
                to_continue, size=30,
                x=self.SIZE/2, y=self.SIZE/2 + 2*CELL_SIZE,
                color=WHITE
            )

            self.window.blit(self.display, (0, 0))
            pygame.display.update()
        self.controller.reset()

    def is_quit(self, event):
        # user presses exit icon
        if event.type == pygame.QUIT:
            self.running, self.playing = False, False
            self.curr_menu.run_display = False
            return True
        return False

    def event_handler(self):
        for event in pygame.event.get():
            if self.is_quit(event):
                print('Bye :)')
                pygame.quit()
                sys.exit()

            # user event that runs every self.speed milisec
            elif self.playing and event.type == pygame.USEREVENT:

                if self.load_model:  # user load model
                    self.controller.load_model()
                    self.load_model = False

                self.controller.ai_play(self.curr_menu.state)  # play

                if self.controller.end == True:  # Only path ai and trained model
                    self.playing = False
                    self.game_over()  # show game over stats

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:  # on Enter
                    self.START = True
                    self.view_path = False

                elif event.key == pygame.K_q:  # on q return
                    self.BACK = True
                    self.controller.reset()

                elif event.key == pygame.K_SPACE:  # space view path or hide training snakes
                    self.view_path = not self.view_path

                elif event.key == pygame.K_DOWN:
                    self.DOWNKEY = True
                elif event.key == pygame.K_UP:
                    self.UPKEY = True

                elif event.key == pygame.K_w:  # speed up/down by self.speed_up
                    self.speed_up = -1 * self.speed_up
                    self.speed = self.speed + self.speed_up
                    pygame.time.set_timer(self.SCREEN_UPDATE, self.speed)

    def reset_keys(self):
        self.UPKEY, self.DOWNKEY, self.START, self.BACK = False, False, False, False

    def draw_text(self, text, size, x, y, color=WINDOW_COLOR):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)
