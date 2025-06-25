import asyncio
import sys
import cv2
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT
from .jump_detector import JumpDetector
from .leaderboard_utils import save_score, get_high_score, format_leaderboard

from .entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window


class Flappy:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
        )
        self.jump_detector = JumpDetector(threshold=0.03)
        self.player_name = "Player"

    def get_player_name(self):
        name = ""
        input_active = True
        font = pygame.font.SysFont("Arial", 28)
        input_box = pygame.Rect(50, 200, 200, 40)

        while input_active:
            self.config.screen.fill((0, 0, 0))
            prompt = font.render("Enter Your Name:", True, (255, 255, 255))
            self.config.screen.blit(prompt, (50, 150))

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 12:
                            name += event.unicode

            pygame.draw.rect(self.config.screen, (255, 255, 255), input_box, 2)
            name_surface = font.render(name, True, (255, 255, 255))
            self.config.screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
            pygame.display.update()
            self.config.clock.tick(30)

        return name.strip() or "Player"

    async def start(self):
        self.player_name = self.get_player_name()
        while True:
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.player = Player(self.config)
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            self.score = Score(self.config)
            await self.splash()
            await self.play()
            await self.game_over()

    async def splash(self):
        self.player.set_mode(PlayerMode.SHM)

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)

            start_signal, cam_frame = self.jump_detector.detect_start_gesture()
            cv2.imshow("Setup Pose: Raise Left Hand to Start", cam_frame)
            cv2.moveWindow("Setup Pose: Raise Left Hand to Start", 700, 100)

            if cv2.waitKey(1) & 0xFF == 27:
                pygame.quit()
                self.jump_detector.release()
                sys.exit()

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.welcome_message.tick()

            high_name, high_score = get_high_score()
            font = pygame.font.SysFont("Arial", 24)
            text = font.render(f"High Score: {high_name} - {high_score}", True, (255, 255, 255))
            self.config.screen.blit(text, (60, 470))

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

            if start_signal:
                print("Start gesture detected! Countdown starting...")
                for i in range(5, 0, -1):
                    self.background.tick()
                    self.floor.tick()
                    self.player.tick()
                    self.welcome_message.tick()
                    font = pygame.font.SysFont("Arial", 36)
                    text_surface = font.render(f"Starting in {i}...", True, (255, 255, 255))
                    self.config.screen.blit(text_surface, (80, 250))
                    pygame.display.update()
                    await asyncio.sleep(1)

                cv2.destroyWindow("Setup Pose: Raise Left Hand to Start")
                self.jump_detector.previous_hip_y = None
                return

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            cv2.destroyAllWindows()
            self.jump_detector.release()
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    async def play(self):
        self.jump_detector.previous_hip_y = None
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)

        while True:
            if self.player.collided(self.pipes, self.floor):
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                self.check_quit_event(event)

            jump, cam_frame = self.jump_detector.detect_jump()
            cv2.imshow("Jump View", cam_frame)
            cv2.moveWindow("Jump View", 700, 100)

            if cv2.waitKey(1) & 0xFF == 27:
                pygame.quit()
                self.jump_detector.release()
                sys.exit()

            if jump or any(self.is_tap_event(e) for e in pygame.event.get()):
                self.player.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def game_over(self):
        self.player.set_mode(PlayerMode.CRASH)
        self.pipes.stop()
        self.floor.stop()

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)

            start_signal, cam_frame = self.jump_detector.detect_start_gesture()
            cv2.imshow("Restart Pose: Raise Left Hand Again", cam_frame)
            cv2.moveWindow("Restart Pose: Raise Left Hand Again", 700, 100)

            if cv2.waitKey(1) & 0xFF == 27:
                pygame.quit()
                self.jump_detector.release()
                sys.exit()

            if start_signal and self.player.y + self.player.h >= self.floor.y - 1:
                score_value = getattr(self.score, "score", 0)
                save_score(self.player_name, score_value)
                cv2.destroyWindow("Restart Pose: Raise Left Hand Again")
                return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.game_over_message.tick()

            font = pygame.font.SysFont("Arial", 24)
            text = font.render("Raise hand again to restart!", True, (255, 255, 255))
            self.config.screen.blit(text, (40, 400))

            high_name, high_score = get_high_score()
            leaderboard_font = pygame.font.SysFont("Arial", 20)
            top_scores = format_leaderboard()
            for idx, line in enumerate(top_scores[:5]):
                score_text = leaderboard_font.render(line, True, (255, 255, 255))
                self.config.screen.blit(score_text, (60, 100 + idx * 25))

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)
            asyncio.sleep(0)


