import pygame
import sys

from persistence import load_settings, save_settings, save_score
from racer       import GameWorld, WIN_W, WIN_H
from ui          import (screen_main_menu, screen_username,
                          screen_settings, screen_game_over,
                          screen_leaderboard)

def run_game(screen, clock, player_name: str, settings: dict) -> tuple:
    
    world = GameWorld(player_name, settings)

    while True:
        coins_this_frame = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    world.player.move_left()
                elif event.key == pygame.K_RIGHT:
                    world.player.move_right()
                elif event.key == pygame.K_ESCAPE:
                    return world.score, world.distance, world.coins

        result = world.update(coins_this_frame)

        world.draw_road(screen)
        world.draw_entities(screen)
        world.draw_hud(screen)

        pygame.display.flip()
        clock.tick(60)

        if result == "dead":
            return world.score, world.distance, world.coins

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("TSIS 3 – Racer")
    clock    = pygame.time.Clock()
    settings = load_settings()

    player_name = ""

    while True:
        action = screen_main_menu(screen, clock)

        if action == "quit":
            pygame.quit()
            sys.exit()

        elif action == "leaderboard":
            screen_leaderboard(screen, clock)

        elif action == "settings":
            settings = screen_settings(screen, clock, settings)
            save_settings(settings)

        elif action == "play":
            if not player_name:
                player_name = screen_username(screen, clock)

            score, distance, coins = run_game(
                screen, clock, player_name, settings)

            save_score(player_name, score, distance, coins)

            result = screen_game_over(screen, clock, score, distance, coins)

            if result == "retry":
                score, distance, coins = run_game(
                    screen, clock, player_name, settings)
                save_score(player_name, score, distance, coins)

if __name__ == "__main__":
    main()
