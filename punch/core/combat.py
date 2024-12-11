from __future__ import annotations
from dataclasses import dataclass
from typing import NamedTuple
from enum import Enum, auto

from arcade import Vec2, Sprite

class Direction(Enum):
    NONE = auto()
    UP = auto()
    LEFT = auto()
    DOWN = auto()
    RIGHT = auto()
    UP_LEFT = auto()
    DOWN_LEFT = auto()
    DOWN_RIGHT = auto()
    UP_RIGHT = auto()

    @staticmethod
    def horizontal(direction: Direction) -> float:
        if direction in {Direction.RIGHT, Direction.DOWN_RIGHT, Direction.UP_RIGHT}:
            return 1.0
        elif direction in {Direction.LEFT, Direction.DOWN_LEFT, Direction.UP_LEFT}:
            return -1.0
        else:
            return 0.0
        
    @staticmethod
    def vertical(direction: Direction) -> float:
        if direction in {Direction.UP, Direction.UP_LEFT, Direction.UP_RIGHT}:
            return 1.0
        elif direction in {Direction.DOWN, Direction.DOWN_LEFT, Direction.DOWN_RIGHT}:
            return -1.0
        else:
            return 0.0
        
    @staticmethod
    def get(h: float, v: float) -> Direction:
        if h < 0.0 and v == 0.0:
            return Direction.LEFT
        elif 0.0 < h and v == 0.0:
            return Direction.RIGHT
        elif h == 0.0 and v < 0.0:
            return Direction.DOWN
        elif h == 0.0 and 0.0 < v:
            return Direction.UP
        elif h < 0.0 and v < 0.0:
            return Direction.DOWN_LEFT
        elif h < 0.0 and 0.0 < v:
            return Direction.UP_LEFT
        elif 0.0 < h and v < 0.0:
            return Direction.DOWN_RIGHT
        elif 0.0 < h and 0.0 < v:
            return Direction.UP_RIGHT
        else: 
            return Direction.NONE

class State(Enum):
    IDLE = auto() # no inputs
    MOVING = auto() # has a direction held
    DASHING = auto() # has dashing button held (uncontrollable ~kinda)
    JUMPING = auto() # Jumping button is pressed (controllable)
    FALLING = auto() # In the air (controllable)
    GRABBED = auto() # Is being hit by a grab attack and motion and position are determined by the attacker
    LIGHT = auto() # doing a light attack and motion and position are determined by the attack
    HEAVY = auto() # doing a heavy/finisher and motion and position are determined by the attack 
    GRAB = auto() # doing a grab and motion and position are determined by the grab and direction
    PARRY = auto() # doing a parry and motion and position are determined by the parry and direction
    RECOVERING = auto() # Is recovering from being hit/attacking and has limited direction control

@dataclass
class Fighter:
    code: int
    position: Vec2 = Vec2()
    velocity: Vec2 = Vec2()
    state: State = State.IDLE
    direction: Direction = Direction.NONE
    is_grounded: bool = False
    on_wall: bool = False
    jumped: bool = False
    jump_count: int = 0

    jump_time: float = 0.0
    ground_time: float = 0.0

    def snapshot(self) -> FighterSnapshot:
        return FighterSnapshot(self.position, self.velocity, self.state, self.direction, self.is_grounded, self.jumped, self.jump_count)
    
    def can_jump(self) -> bool:
        # TODO
        return self.state in {State.IDLE, State.MOVING}
    
    def is_kinematic(self) -> bool:
        return self.state not in {State.IDLE, State.MOVING, State.JUMPING, State.FALLING}
    
    def is_dynamic(self) -> bool:
        return self.state in {State.IDLE, State.MOVING, State.JUMPING, State.FALLING}
    
class FighterSnapshot(NamedTuple):
    position: Vec2 = Vec2()
    velocity: Vec2 = Vec2()
    state: State = State.IDLE
    direction: Direction = Direction.NONE
    is_grounded: bool = False
    jumped: bool = False
    jump_count: int = 0

@dataclass
class Attack:
    owner: int

