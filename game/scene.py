# Pedro Morales
# CPSC 386-03
# 2022-04-23
# pedrom2@csu.fullerton.edu
# @pedromorales451
#
# Lab 05-00
#
# This file contains different scenes for Bouncing Balls.
#

"""Scene objects for making games with PyGame."""

from random import randint
import pygame
from more_itertools import grouper
from game import rgbcolors
from game.ball import Ball
from game.ball import random_velocity
from game.animation import Explosion


class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(self, screen, background_color, soundtrack=None):
        """Scene initializer"""
        self._screen = screen
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
        self._render_updates = None

    def draw(self):
        """Draw the scene."""
        self._screen.blit(self._background, (0, 0))

    def process_event(self, event):
        """Process a game event by the scene."""
        if event.type == pygame.QUIT:
            print("Good Bye!")
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("Bye bye!")
            self._is_valid = False

    def is_valid(self):
        """Is the scene valid? A valid scene can be used to play a scene."""
        return self._is_valid

    def render_updates(self):
        """Render all sprite updates."""
        pass

    def update_scene(self):
        """Update the scene state."""
        pass

    def start_scene(self):
        """Start the scene."""
        if self._soundtrack:
            try:
                pygame.mixer.music.load(self._soundtrack)
                pygame.mixer.music.set_volume(0.1)
            except pygame.error as pygame_error:
                print("Cannot open the mixer?")
                raise SystemExit("broken!!") from pygame_error
            pygame.mixer.music.play(-1)

    def end_scene(self):
        """End the scene."""
        if self._soundtrack and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.stop()

    def frame_rate(self):
        """Return the frame rate the scene desires."""
        return self._frame_rate


class EmptyPressAnyKeyScene(Scene):
    """Empty scene where it will invalidate when a key is pressed."""

    def process_event(self, event):
        """Process game events."""
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            self._is_valid = False


class SplashScene(EmptyPressAnyKeyScene):
    """A splash screen with a message."""

    def __init__(self, screen, message, soundtrack=None):
        """Init the splash screen."""
        super().__init__(screen, rgbcolors.snow, soundtrack)
        self._message = message
        self._words_per_line = 5

    def _split_message(self):
        """Given a message, split it up according to how many words per line."""
        lines = [
            " ".join(x).rstrip()
            for x in grouper(self._message.split(), self._words_per_line, "")
        ]
        for line in lines:
            yield line

    def draw(self):
        super().draw()
        (width, height) = self._screen.get_size()
        press_any_key_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        press_any_key = press_any_key_font.render(
            "Press any key.", True, rgbcolors.black
        )
        press_any_key_pos = press_any_key.get_rect(
            center=(width / 2, height - 50)
        )

        font = pygame.font.Font(pygame.font.get_default_font(), 25)
        start_pos = (height / 2) - (
            (len(self._message.split()) // self._words_per_line) * 30
        )
        offset = 0
        for line in self._split_message():
            line = font.render(line, True, rgbcolors.black)
            line_pos = line.get_rect(center=(width / 2, start_pos + offset))
            offset += 30
            self._screen.blit(line, line_pos)
        self._screen.blit(press_any_key, press_any_key_pos)


class BlinkingTitle(EmptyPressAnyKeyScene):
    """A scene with blinking text."""

    def __init__(
        self, screen, message, color, size, background_color, soundtrack=None
    ):
        super().__init__(screen, background_color, soundtrack)
        self._message_color = color
        self._message_complement_color = (
            255 - color[0],
            255 - color[1],
            255 - color[2],
        )
        self._size = size
        self._message = message
        self._t = 0.0
        self._delta_t = 0.01

    def _interpolate(self):
        # This can be done with pygame.Color.lerp
        self._t += self._delta_t
        if self._t > 1.0 or self._t < 0.0:
            self._delta_t *= -1
        c = rgbcolors.sum_color(
            rgbcolors.mult_color(
                (1.0 - self._t), self._message_complement_color
            ),
            rgbcolors.mult_color(self._t, self._message_color),
        )
        return c

    def draw(self):
        super().draw()
        presskey_font = pygame.font.Font(
            pygame.font.get_default_font(), self._size
        )
        presskey = presskey_font.render(
            self._message, True, self._interpolate()
        )
        (width, height) = self._screen.get_size()
        presskey_pos = presskey.get_rect(center=(width / 2, height / 2))
        press_any_key_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        press_any_key = press_any_key_font.render(
            "Press any key.", True, rgbcolors.black
        )
        (width, height) = self._screen.get_size()
        press_any_key_pos = press_any_key.get_rect(
            center=(width / 2, height - 50)
        )
        self._screen.blit(presskey, presskey_pos)
        self._screen.blit(press_any_key, press_any_key_pos)


class BouncingBallsScene(Scene):
    """Bounding balls demo."""

    def __init__(
        self, num_balls, screen, background_color, frame_rate, soundtrack=None
    ):
        super().__init__(screen, background_color, soundtrack)
        self._pause_game = False
        self._num_balls = num_balls
        self._frame_rate = frame_rate
        self._screen = screen
        self._boundary_rect = screen.get_rect()
        self._balls = []
        self._render_updates = pygame.sprite.RenderUpdates()
        Explosion.containers = self._render_updates
        self._explosions_on = True

    def start_scene(self):
        super().start_scene()

        (width, height) = self._screen.get_size()

        x_min = 0 + (Ball.default_radius * 2)
        x_max = width - (Ball.default_radius * 2)
        y_min = 0 + (Ball.default_radius * 2)
        y_max = height - (Ball.default_radius * 2)
        self._balls.append(Ball("0", width / 2, height / 2))

        for i in range(1, self._num_balls):
            point_too_close = True
            x_coord = randint(x_min, x_max)
            y_coord = randint(y_min, y_max)
            while point_too_close:
                point_too_close = False
                x_coord = randint(x_min, x_max)
                y_coord = randint(y_min, y_max)
                for ball in self._balls:
                    point_too_close = point_too_close or ball.too_close(
                        x_coord, y_coord, Ball.default_radius * 2
                    )
            self._balls.append(Ball(str(i), x_coord, y_coord))

        velocity = random_velocity(5, 10)
        self._balls[0].set_velocity(velocity.x, velocity.y)

    def end_scene(self):
        super().end_scene()

    def _draw_boundaries(self):
        (width, height) = self._screen.get_size()
        pygame.draw.rect(
            self._screen,
            rgbcolors.yellow,
            self._boundary_rect,
            (width // 100),
            (width // 200),
        )

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            # toggle text annotations for all balls
            for ball in self._balls:
                ball.toggle_draw_text()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            # toggle explosion animation
            if self._explosions_on:
                self._explosions_on = False
            else:
                self._explosions_on = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            # pause the scene (scene stops updating)
            if self._pause_game:
                self._pause_game = False
            else:
                self._pause_game = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            # toggle sound effects
            for ball in self._balls:
                ball.toggle_sound()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            if self._soundtrack and pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)
                pygame.mixer.music.stop()
            else:
                if self._soundtrack:
                    try:
                        pygame.mixer.music.load(self._soundtrack)
                    except pygame.error as pygame_error:
                        print("Cannot open the mixer?")
                        raise SystemExit("broken!!") from pygame_error
                    pygame.mixer.music.play(-1)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            # exit the scene to the next scene
            self._is_valid = False

    def render_updates(self):
        if self._render_updates:
            self._render_updates.clear(self._screen, self._background)
            self._render_updates.update()
            dirty = self._render_updates.draw(self._screen)

    def draw(self):
        super().draw()
        self._draw_boundaries()
        (width, height) = self._screen.get_size()
        for ball in self._balls:
            ball.circle.stay_in_bounds(0, width, 0, height)
            ball.draw(self._screen)

    def update_scene(self):
        if not self._pause_game:
            super().update_scene()
            for ball in self._balls:
                ball.update()
            for ball in self._balls:
                (width, height) = self._screen.get_size()
                ball.wall_reflect(0, width, 0, height)
            for index, ball in enumerate(self._balls):
                for other_ball in self._balls[index + 1 :]:
                    if ball.collide_with(other_ball):
                        (width, height) = self._screen.get_size()
                        ball.separate_from(other_ball)
                        ball.bounce(other_ball)
                        other_ball.bounce(ball)

                        if not ball.is_alive and self._explosions_on:
                            Explosion(ball)

                        if not other_ball.is_alive and self._explosions_on:
                            Explosion(other_ball)
