from punch.lib.application import View

from arcade import draw_sprite, SpriteSolidColor, SpriteCircle, Vec2, Camera2D
from arcade.future.input import ActionState
from arcade.clock import GLOBAL_FIXED_CLOCK

from punch.game.input import Input

from punch.core.combat import Direction, State, Fighter
from punch.core.physics import Stage

PLAYER_GROUND_SPEED = 2000.0  # How fast the player accelerates left and right
PLAYER_AIR_SPEED = 1200.0  # How fast the player accelerates left and right in the air
PLAYER_JUMP_SPEED = 1000.0  # The velocity impules the player recieves upwards
# The acceleration of the player due to gravity while they are falling
PLAYER_JUMP_FALL = 2000.0
PLAYER_JUMP_RELEASE = 1500.0  # The acceleration of the player due to gravity while they are rising, but not jumping
PLAYER_JUMP_HOLD = 1000.0  # The acceleration of the player due to gravity while they are rising and jumping
PLAYER_DRAG = 0.005  # how much the air drags on the player, assumes the player is 100kg so we only deal with acceleration no forces
PLAYER_FRICTION_HOLD = 0.04  # how much the ground resists player movement when they are travelling in that direction, assumes the player is 100kg so we only deal with acceleration no forces
PLAYER_FRICTION_RELEASE = 0.9  # how much the ground resists player movement, assumes the player is 100kg so we only deal with acceleration no forces

PLAYER_CAYOTE = 1 / 15.0  # ~4 frames

SQUISH_FACTOR = 1500

class RootView(View):

    def __init__(self):
        super().__init__()
        Input.initialise()

        # Player Input State
        self._player_jumping: bool = False
        self._player_direction: Direction = Direction.NONE

        self.stage = Stage(1, self.window.rect)
        self.player = self.stage.fighters[0]
        
        self.player.position = Vec2(*self.center)

        self.player_sprite: SpriteSolidColor = SpriteSolidColor(60, 80, self.center_x, self.center_y)
        self.direction_sprite: SpriteSolidColor = SpriteSolidColor(5, 5, -100, -100, (125, 255, 125), angle=45)


    def on_draw(self) -> None:
        self.clear()

        pos = (0.0, 0.0)
        d = Direction.horizontal(self.player.direction), Direction.vertical(self.player.direction)
        self.direction_sprite.position = self.player.position.x + d[0] * 40.0, self.player.position.y + d[1] * 50.0

        draw_sprite(self.direction_sprite)
        draw_sprite(self.player_sprite)
        

    def on_update(self, delta_time):
        Input.manager.update()
        h = Input.manager.axes_state["horizontal"]
        v = Input.manager.axes_state["vertical"]

        player_state_0 = self.stage.snapshots[0][-2]
        player_state_1 = self.stage.snapshots[0][-1]
        fraction = GLOBAL_FIXED_CLOCK.fraction

        self.player_sprite.position = player_state_0.position + fraction * (player_state_1.position - player_state_0.position)

        self.player_sprite.position = self.player.position

        self.player.direction = Direction.get(h, v)



    def on_fixed_update(self, delta_time):
        self.stage.process()

    def on_action(self, action: str, state: ActionState):
        match action:
            case "jump":
                self.player.jumped = state == ActionState.PRESSED
                if not self.player.jumped:
                    return
                self.player.jump_time = GLOBAL_FIXED_CLOCK.time
