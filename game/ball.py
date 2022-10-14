# Pedro Morales
# CPSC 386-03
# 2022-04-23
# pedrom2@csu.fullerton.edu
# @pedromorales451
#
# Lab 05-00
#
# This file defines the Circle and Ball classes that contain the game logic.
#

"""A Ball class for the bouncing ball demo."""

import os.path
from random import randint
from math import isclose
import pygame
from game import rgbcolors


def random_velocity(min_val=1, max_val=3):
    """Generate a random velocity in a plane, return it as a Vector2"""
    random_x = randint(min_val, max_val)
    random_y = randint(min_val, max_val)

    if randint(0, 1):
        random_x *= -1
    if randint(0, 1):
        random_y *= -1
    return pygame.Vector2(random_x, random_y)


def random_color():
    """Return a random color."""
    return pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255))


# This is the class we discussed in class. You can have this as a standalone
# definition of a circle's geometry or you can fold the Circle and Ball classes
# together into a single class definition. Your choice.
class Circle:
    """Class representing a circle with a bounding rect."""

    def __init__(self, center_x, center_y, radius):
        self._center = pygame.Vector2(center_x, center_y)
        self._radius = radius

    @property
    def radius(self):
        """Return the circle's radius"""
        return self._radius

    @property
    def center(self):
        """Return the circle's center."""
        return self._center

    @property
    def rect(self):
        """Return bounding Rect; calculate it and create a new Rect instance"""
        left = self._center[0] - self.radius
        top = self._center[1] + self._radius
        return pygame.Rect(left, top, self.width, self.width)

    @property
    def width(self):
        """Return the width of the bounding box the circle is in."""
        return self._radius * 2

    @property
    def height(self):
        """Return the height of the bounding box the circle is in."""
        return self._radius * 2

    def squared_distance_from(self, other_circle):
        """Squared distance from self to other circle."""
        return (other_circle.center - self._center).squared_length()

    def distance_from(self, other_circle):
        """Distance from self to other circle"""
        return (other_circle.center - self._center).length()

    def move_ip(self, x, y):
        """Move circle in place, update the circle's center"""
        self._center = self._center + pygame.Vector2(x, y)

    def move(self, x, y):
        """Move circle, return a new Circle instance"""
        center = self._center = self._center + pygame.Vector2(x, y)

        return Circle(center[0], center[1], self._radius)

    def stay_in_bounds(self, xmin, xmax, ymin, ymax):
        """Update the position of the circle so that it remains within the rectangle defined by xmin, xmax, ymin, ymax."""
        (center_x, center_y) = self._center
        distance_from_xmin = center_x - self.radius
        distance_from_xmax = center_x + self.radius
        distance_from_ymin = center_y - self.radius
        distance_from_ymax = center_y + self.radius

        if distance_from_xmin <= xmin:
            self._center = pygame.Vector2(
                abs(distance_from_xmin) + center_x, center_y
            )
        elif distance_from_xmax >= xmax:
            new_x = center_x - (distance_from_xmax - xmax)
            self._center = pygame.Vector2(new_x, center_y)

        # update center_x
        center_x = self._center[0]

        if distance_from_ymin <= ymin:
            self._center = pygame.Vector2(
                center_x, abs(distance_from_ymin) + center_y
            )
        elif distance_from_ymax >= ymax:
            new_y = center_y - (distance_from_ymax - ymax)
            self._center = pygame.Vector2(center_x, new_y)


class Ball:
    """A class representing a moving ball."""

    default_radius = 25

    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, "data")
    # Feel free to change the sounds to something else.
    # Make sure you have permssion to use the sound effect file and document
    # where you retrieved this file, who is the author, and the terms of
    # the license.
    bounce_sound = os.path.join(data_dir, "Boing.aiff")
    reflect_sound = os.path.join(data_dir, "Monkey.aiff")

    def __init__(self, name, center_x, center_y, sound_on=True):
        """Initialize a bouncing ball."""
        # The name can be any string. The best choice is an integer.
        self._name = name
        # Yes, we could define the details about our geometry in the Ball
        # class or we can define the geometry in an instance variable.
        # It is up to you if you want to separate them out or integrate them
        # together.
        self._circle = Circle(center_x, center_y, Ball.default_radius)
        self._color = random_color()
        self._velocity = random_velocity()
        self._sound_on = sound_on
        self._bounce_count = randint(5, 10)
        self._is_alive = True
        self._draw_text = False
        font = pygame.font.SysFont(None, Ball.default_radius)
        self._name_text = font.render(str(self._name), True, rgbcolors.black)
        try:
            self._bounce_sound = pygame.mixer.Sound(Ball.bounce_sound)
            self._bounce_channel = pygame.mixer.Channel(2)
        except pygame.error as pygame_error:
            print(f"Cannot open {Ball.bounce_sound}")
            raise SystemExit(1) from pygame_error
        try:
            self._reflect_sound = pygame.mixer.Sound(Ball.reflect_sound)
            self._reflect_channel = pygame.mixer.Channel(3)
        except pygame.error as pygame_error:
            print(f"Cannot open {Ball.reflect_sound}")
            raise SystemExit(1) from pygame_error

    def toggle_draw_text(self):
        """Toggle the debugging text where each circle's name is drawn."""
        self._draw_text = not self._draw_text

    def draw(self, surface):
        """Draw the circle to the surface."""
        pygame.draw.circle(surface, self.color, self.center, self.radius)
        if self._draw_text:
            surface.blit(
                self._name_text,
                self._name_text.get_rect(center=self._circle.center),
            )

    def wall_reflect(self, xmin, xmax, ymin, ymax):
        """Reflect the ball off of a wall, play a sound if the sound flag is on."""
        if (
            self.center[0] - self.radius <= xmin
            or self.center[0] + self.radius >= xmax
        ):
            self.set_velocity(self._velocity.x * -1, self._velocity.y)

            if self._sound_on and self._is_alive:
                self._reflect_sound.play()

        if (
            self.center[1] - self.radius <= ymin
            or self.center[1] + self.radius >= ymax
        ):
            self.set_velocity(self._velocity.x, self._velocity.y * -1)

            if self._sound_on and self._is_alive:
                self._reflect_sound.play()

    def bounce(self, other_ball):
        """Bounce the ball off of another ball, play a sound if the ball is no alive."""
        if self._sound_on:
            self._bounce_sound.play()

        if self._name != "0" and self._bounce_count > 0:
            self._bounce_count -= 1

            normal = other_ball.center - self.center

            self._velocity = self._velocity.reflect(normal)
        elif self._name == "0":
            normal = other_ball.center - self.center

            self._velocity = self._velocity.reflect(normal)

        if self._bounce_count == 0 and self.is_alive and self._name != "0":
            distance_between_balls = self.circle.distance_from(other_ball)
            seperating_distance = (self.radius * 2.0) + (self.radius * 0.25)
            reverse_velocity_self = -self.velocity
            reverse_velocity_other = -other_ball.velocity

            while distance_between_balls <= self.radius * 2 or isclose(
                distance_between_balls, self.radius * 2
            ):
                delta = seperating_distance - distance_between_balls
                half_delta = delta / 2.0

                if other_ball.is_alive:
                    self._circle.move_ip(*(half_delta * reverse_velocity_self))
                    self.update()
                    other_ball.circle.move_ip(
                        *(half_delta * reverse_velocity_other)
                    )
                    other_ball.update()
                else:
                    self._circle.move_ip(
                        *(half_delta * reverse_velocity_self * 2)
                    )
                    self.update()

                distance_between_balls = self.circle.distance_from(other_ball)
                reverse_velocity_self = self.velocity
                reverse_velocity_other = other_ball.velocity

            self._color = rgbcolors.white
            self._is_alive = False
            self.stop()

    def collide_with(self, other_ball):
        """Return true if self collides with other_ball."""
        return self._circle.distance_from(other_ball.circle) <= (
            self.radius + other_ball.radius
        )

    def separate_from(self, other_ball):
        """Separate a ball from the other ball so they are no longer overlapping."""
        overlap_distance = (self.radius + other_ball.radius) - (
            self._circle.distance_from(other_ball.circle)
        )

        half_overlap_distance = overlap_distance / 2

        reverse_velocity = self._velocity * -1

        factor = 0

        if not other_ball.is_alive:
            factor = 2
        else:
            factor = 1

        self._circle.move_ip(
            *(reverse_velocity * half_overlap_distance * factor)
        )

        reverse_velocity = other_ball.velocity * -1

        if not self.is_alive:
            factor = 2
        else:
            factor = 1

        other_ball.circle.move_ip(
            *(reverse_velocity * half_overlap_distance * factor)
        )

    @property
    def name(self):
        """Return the ball's name."""
        return self._name

    @property
    def rect(self):
        """Return the ball's rect."""
        return self._circle.rect

    @property
    def circle(self):
        """Return the ball's circle."""
        return self._circle

    @property
    def center(self):
        """Return the ball's center."""
        return self._circle.center

    @property
    def radius(self):
        """Return the ball's radius"""
        return self._circle.radius

    @property
    def color(self):
        """Return the color of the ball."""
        return self._color

    @property
    def velocity(self):
        """Return the velocity of the ball."""
        return self._velocity

    @property
    def is_alive(self):
        """Return true if the ball is still alive."""
        return self._is_alive

    def toggle_sound(self):
        """Turn off the sound effects."""
        if self._sound_on:
            self._sound_on = False
        else:
            self._sound_on = True

    def too_close(self, x, y, min_dist):
        """Is the ball too close to some point by some min_dist?"""
        point = pygame.Vector2(x, y)
        distance = (self.center - point).length()
        return distance <= min_dist

    def stop(self):
        """Stop the ball from moving."""
        self._velocity = pygame.Vector2(0, 0)

    def set_velocity(self, x, y):
        """Set the ball's velocity."""
        self._velocity = pygame.Vector2(x, y)

    def update(self):
        """Update the ball's position"""
        self._circle.move_ip(*self._velocity)

    def __str__(self):
        """Ball stringify."""
        return f"Ball({self._name}, {self._circle.center}, {self._velocity}, {self._color})"
