from math import copysign

from arcade import Rect, Vec2
from arcade.clock import GLOBAL_FIXED_CLOCK

from punch.core.combat import Fighter, FighterSnapshot, Attack, State, Direction

FIGHTER_WIDTH = 60
FIGHTER_H_WIDTH = FIGHTER_WIDTH / 2.0
FIGHTER_HEIGHT = 80
FIGHTER_H_HEIGHT = FIGHTER_HEIGHT / 2.0

FIGHTER_GROUND_SPEED = 2000.0  # How fast fighters accelerate left and right
FIGHTER_AIR_SPEED = 1200.0  # How fast fighters accelerates left and right in the air
FIGHTER_JUMP_SPEED = 1000.0  # The velocity impules the player recieves upwards
# The acceleration of the player due to gravity while they are falling
FIGHTER_JUMP_FALL = 2000.0
FIGHTER_JUMP_RELEASE = 1500.0  # The acceleration of the player due to gravity while they are rising, but not jumping
FIGHTER_JUMP_HOLD = 1000.0  # The acceleration of the player due to gravity while they are rising and jumping
FIGHTER_DRAG = 0.005  # how much the air drags on the player, assumes the player is 100kg so we only deal with acceleration no forces
FIGHTER_FRICTION_HOLD = 0.04  # how much the ground resists player movement when they are travelling in that direction, assumes the player is 100kg so we only deal with acceleration no forces
FIGHTER_FRICTION_RELEASE = 0.9  # how much the ground resists player movement, assumes the player is 100kg so we only deal with acceleration no forces

FIGHTER_CAYOTE = 1 / 15.0  # ~4 frames

SQUISH_FACTOR = 1500

class Stage:

    def __init__(self, no_fighters: int, scene_bounds: Rect):
        self.fighters = [Fighter(code) for code in range(no_fighters)]
        self.snapshots: list[list[FighterSnapshot]] = [[] for _ in range(no_fighters)]
        self.attacks: list[Attack] = []
        self.bounds: Rect = scene_bounds

        self.gravity = Vec2(0.0, -1.0)

    def process(self):
        # Fighters don't actually interact they can go through each other, only attack hitboxes actually cause them to contact.
        for fighter in self.fighters:
            self._process_fighter(fighter)
            self.snapshots[fighter.code].append(fighter.snapshot())


    def _process_fighter(self, fighter: Fighter):
        # TODO: Attacks

        # When the fighter is being controlled by an attack we don't calculate gravity (sometimes shush)
        if fighter.is_dynamic():
            # Acceleration
            if fighter.velocity.y >= 0.0:
                fall_acceleration = FIGHTER_JUMP_HOLD if fighter.state == State.JUMPING else FIGHTER_JUMP_RELEASE
            else:
                fall_acceleration = FIGHTER_JUMP_FALL
            fighter.velocity = fighter.velocity + self.gravity * fall_acceleration * GLOBAL_FIXED_CLOCK.delta_time

            horizontal = Direction.horizontal(fighter.direction)
            fighter.velocity += Vec2(horizontal * GLOBAL_FIXED_CLOCK.delta_time * (FIGHTER_GROUND_SPEED if fighter.is_grounded else FIGHTER_AIR_SPEED), 0.0)

            v_length_sqr = fighter.velocity.length_squared()
            v_dir = fighter.velocity.normalize()

            # Drag
            fighter.velocity = fighter.velocity + 0.5 * v_length_sqr * FIGHTER_DRAG * GLOBAL_FIXED_CLOCK.delta_time * -v_dir # Air Resistance

            holding = copysign(fighter.velocity.x, horizontal) == fighter.velocity.x if horizontal else 0.0
            drag = FIGHTER_FRICTION_HOLD if holding else FIGHTER_FRICTION_RELEASE
            fighter.velocity += Vec2(drag * FIGHTER_JUMP_FALL * GLOBAL_FIXED_CLOCK.delta_time * -v_dir.x, 0)

        is_grounded, on_wall = self._process_fighter_bounds_check(fighter)

        can_jump = fighter.can_jump()
        if is_grounded and can_jump and (fighter.jumped or GLOBAL_FIXED_CLOCK.time_since(fighter.jump_time) < FIGHTER_CAYOTE):
            fighter.velocity += Vec2(0.0, FIGHTER_JUMP_SPEED)
        fighter.jumped = False

        if not is_grounded and fighter.is_grounded:
            # Left the ground this frame
            fighter.ground_time = GLOBAL_FIXED_CLOCK.time
        fighter.is_grounded = is_grounded
        fighter.on_wall = on_wall

        # TODO calculate the state oh god
        
        # Apply velocity
        fighter.position += fighter.velocity * GLOBAL_FIXED_CLOCK.delta_time

    def _process_fighter_bounds_check(self, fighter: Fighter) -> tuple[bool, bool]:
        # Bounds Collision
        x, y, w, h = self.bounds.xywh
        l, r, b, t = self.bounds.lrbt
        fx, fy = fighter.position
        fl, fr, fb, ft = fx - FIGHTER_H_WIDTH, fx + FIGHTER_H_WIDTH, fy - FIGHTER_H_HEIGHT, fy + FIGHTER_H_HEIGHT

        is_grounded = False
        on_wall = False
        if (r < fr or fl < l or t < ft or fb < b):
            dx = 2.0 * (fx - x) / (w - FIGHTER_WIDTH)
            dy = 2.0 * (fy - y) / (h - FIGHTER_HEIGHT)

            if dy >= 1.0:
                # Hit top of bounds
                normal = Vec2(0.0, -1.0)
                collision_depth = abs(y - fy) - 0.5 * (h - FIGHTER_HEIGHT)
            elif dy <= -1.0:
                # Hit ground
                normal = Vec2(0.0, 1.0)
                collision_depth = abs(y - fy) - 0.5 * (h - FIGHTER_HEIGHT)
                is_grounded = True
            else:
                normal = Vec2()
                collision_depth = 0.0    
            
            # Apply vertical impulse
            impulse = -1 * normal.dot(fighter.velocity)
            fighter.velocity += max(0.0, impulse) * normal
            fighter.position += collision_depth * normal

            if dx >= 1.0:
                # Hit left wall
                normal = Vec2(-1.0, 0.0)
                collision_depth = abs(x - fx) - 0.5 * (w - FIGHTER_WIDTH)
                on_wall = True
            elif dx <= -1.0:
                # Hit Right wall
                normal = Vec2(1.0, 0.0)
                collision_depth = abs(x - fx) - 0.5 * (w - FIGHTER_WIDTH)
                on_wall = True
            else:
                normal = Vec2()
                collision_depth = 0.0
      
            # Apply horizontal impulse
            impulse = -1 * normal.dot(fighter.velocity)
            fighter.velocity += max(0.0, impulse) * normal
            fighter.position += collision_depth * normal
        return is_grounded, on_wall
