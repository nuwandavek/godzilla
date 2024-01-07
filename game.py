import random
import copy
import pygame
import time
from constants import DIESIDE, MAX_HEALTH, VICTORY_PTS_WIN, DIE_COUNT, PlayerState, CARD_WIDTH, CARD_HEIGHT, CARD_PADDING, CARD_BORDER_RADIUS, PIXEL_UNICODE

class Game:
    def __init__(self, player_strategies=[], start_idx=0, visualize=False):
        self.players = [PlayerState() for _ in range(2)]
        self.player_strategies = player_strategies
        assert len(self.player_strategies) == len(self.players)
        self.winner = -1
        self.current_player_idx = start_idx
        self.visualize = visualize
        if self.visualize:
            pygame.init()
            self.screen = pygame.display.set_mode((1000, 400))
            pygame.display.set_caption("King of Tokyo")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font('Pixel-UniCode.ttf', 36)

    @property
    def n_players(self):
        return len(self.players)

    @property
    def current_player(self):
        return self.players[self.current_player_idx]

    @property
    def other_player_idx(self):
        return (self.current_player_idx + 1) % self.n_players

    @property
    def other_player(self):
        return self.players[self.other_player_idx]

    @property
    def tokyo_player_idx(self):
        players_in_tokyo = [player.in_tokyo for player in self.players]
        return players_in_tokyo.index(True)

    def other_player_yields_tokyo(self, dice):
        return self.player_strategies[self.other_player_idx].yield_tokyo(copy.deepcopy(self.other_player), copy.deepcopy(self.current_player), copy.deepcopy(dice))

    def start_turn(self):
        if self.current_player.in_tokyo:
            self.current_player.victory_points += 2

    def roll_n_dice(self, n):
        return [random.choice([DIESIDE.ATTACK, DIESIDE.HEAL, DIESIDE.ONE, DIESIDE.TWO, DIESIDE.THREE]) for _ in range(n)]

    def roll_dice(self):
        dice_results = self.roll_n_dice(DIE_COUNT)
        if self.visualize:
            self.draw_game_state(dice_results, 1)
        for i in range(2):
            keep_mask = self.player_strategies[self.current_player_idx].keep_dice(copy.deepcopy(self.current_player), copy.deepcopy(self.other_player), copy.deepcopy(dice_results), reroll_n=i)
            dice_results = [dice_results[i] for i in range(DIE_COUNT) if keep_mask[i]] + self.roll_n_dice(DIE_COUNT - sum(keep_mask))
            if self.visualize:
                self.draw_game_state(dice_results, i + 2)
        return dice_results

    def resolve_victory_point_dice(self, dice):
        for dieside in [DIESIDE.ONE, DIESIDE.TWO, DIESIDE.THREE]:
          cnt = sum([x == dieside for x in dice])
          if cnt >= 3:
            self.current_player.victory_points += int(dieside)
            self.current_player.victory_points += cnt - 3

    def resolve_health_dice(self, dice):
        heals = sum([x == DIESIDE.HEAL for x in dice])
        if not self.current_player.in_tokyo:
          self.current_player.health  = min(MAX_HEALTH, self.current_player.health + heals)

    def resolve_attack_dice(self, dice):
        attack = sum([x == DIESIDE.ATTACK for x in dice])
        if self.current_player.in_tokyo:
          self.other_player.health  = self.other_player.health - attack
        elif self.other_player.in_tokyo:
          self.other_player.health  = self.other_player.health - attack
          if attack > 0 and self.other_player_yields_tokyo(dice):
            self.current_player.in_tokyo = True
            self.other_player.in_tokyo = False
        else:
            self.current_player.in_tokyo = True
            self.current_player.victory_points += 1


    def resolve_dice(self, dice):
        self.resolve_victory_point_dice(dice)
        self.resolve_health_dice(dice)
        self.resolve_attack_dice(dice)

    def check_winner(self):
        for i, player in enumerate(self.players):
            if player.health <= 0:
                self.winner = (i + 1) % self.n_players
            if player.victory_points >= VICTORY_PTS_WIN:
                self.winner = i

    def draw_game_state(self, dice=None, turn=0):
        self.screen.fill((0, 0, 0))
        for i, player in enumerate(self.players):
            self.draw_player_info(player, i)
        self.draw_dice(dice, turn)
        pygame.display.flip()
        self.clock.tick(5)

    def draw_player_info(self, player, player_idx):
        player_x, player_y = 50, player_idx * (CARD_HEIGHT + CARD_PADDING) + CARD_PADDING

        pygame.draw.rect(self.screen, (30, 30, 30), (player_x, player_y, CARD_WIDTH, CARD_HEIGHT), border_radius=CARD_BORDER_RADIUS)

        name = self.player_strategies[player_idx].__class__.__module__
        agent_text = self.font.render(f"{name}{' (tokyo)' if player.in_tokyo else ''}", True, (255, 255, 255))
        agent_text_rect = agent_text.get_rect(center=(player_x + CARD_WIDTH // 2, player_y + 25))
        self.screen.blit(agent_text, agent_text_rect)

        heart_text = PIXEL_UNICODE[DIESIDE.HEAL]  # Unicode for heart symbol
        health_text = self.font.render(f"{heart_text} {player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (player_x + 10, player_y + 60))

        star_text = PIXEL_UNICODE['VP']  # Unicode for star symbol
        vp_text = self.font.render(f"{star_text} {player.victory_points}", True, (255, 255, 255))
        self.screen.blit(vp_text, (player_x + 10, player_y + 100))

    def draw_dice(self, dice, turn):
        dice = ['EMPTY'] * DIE_COUNT if dice is None else dice
        pygame.draw.rect(self.screen, (30, 30, 30), (400, CARD_PADDING, 550, CARD_HEIGHT), border_radius=CARD_BORDER_RADIUS)
        for i, dieside in enumerate(dice):
            die_x, die_y = 500 + i * (50 + CARD_PADDING), 50
            die_text = self.font.render(PIXEL_UNICODE[dieside], True, (0, 0, 0))
            die_text_rect = die_text.get_rect(center=(die_x + 25, die_y + 25))

            pygame.draw.rect(self.screen, (255, 255, 255), (die_x, die_y, 50, 50), border_radius=CARD_BORDER_RADIUS)
            self.screen.blit(die_text, die_text_rect)
        player = self.player_strategies[self.current_player_idx].__class__.__module__
        player_text = self.font.render(f"{player}'s turn {turn}", True, (255, 255, 255))
        player_text_rect = player_text.get_rect(center=(675, CARD_HEIGHT - 25))
        self.screen.blit(player_text, player_text_rect)

    def step(self):
        if self.visualize:
            self.draw_game_state()
        self.start_turn()
        dice = self.roll_dice()
        self.resolve_dice(dice)
        self.check_winner()
        self.current_player_idx = (self.current_player_idx + 1) % self.n_players

    def __str__(self):
        return (f'GAME STATE: player {self.tokyo_player_idx} is in tokyo \n' +
                f'Players 0 has {self.players[0].health} health and {self.players[0].victory_points} victory points \n' +
                f'Players 1 has {self.players[1].health} health and {self.players[1].victory_points} victory points')


if __name__ == '__main__':
  import importlib
  import sys
  if len(sys.argv) != 3:
    print('Example usage: python game.py random_agent random_agent')
    sys.exit(1)
  _, strategy_one, strategy_two =sys.argv
  module_one = importlib.import_module(strategy_one)
  module_two = importlib.import_module(strategy_two)
  GAMES_N = 1
  winners = []
  for i in range(GAMES_N):
    game = Game(player_strategies=[module_one.PlayerStrategy(), module_two.PlayerStrategy()],
                start_idx=i%2, visualize=True)
    while game.winner == -1:
      game.step()
    winners.append(game.winner)
    if game.visualize:
      game.draw_game_state()
      time.sleep(5)
      pygame.quit()
  player_0_wins = sum([x == 0 for x in winners])
  print(f'{strategy_one} won {player_0_wins}/{GAMES_N} games against {strategy_two}')
