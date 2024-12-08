from pyglet.input import get_controllers
from arcade.future.input import (
    InputManager,
    ActionState,
    Keys,
    MouseAxes,
    MouseButtons,
    ControllerAxes,
    ControllerButtons,
    Action,
    ActionMapping,
    Axis,
    AxisMapping,
)

__all__ = (
    "Input",
    "InputManager",
    "ActionState",
    "Keys",
    "MouseAxes",
    "MouseButtons",
    "Action",
    "ActionMapping",
    "Axis",
    "AxisMapping",
)


class Input:
    manager: InputManager = None

    @staticmethod
    def initialise():
        m: InputManager
        c = get_controllers()
        controller = None if not c else c[0]
        Input.manager = m = InputManager(controller=controller)

        # movement
        m.new_action("jump")
        m.new_action("left")
        m.new_action("right")

        # combat
        m.new_action("light")
        m.new_action("grab")
        m.new_action("parry")
        m.new_action("heavy")

        # aiming
        m.new_axis("horizontal")
        m.new_axis("vertical")


        m.add_action_input("left", Keys.A)
        m.add_action_input("right", Keys.D)
        m.add_action_input("jump", Keys.SPACE)

        m.add_axis_input("horizontal", Keys.A, scale=-1.0)
        m.add_axis_input("horizontal", Keys.D, scale=1.0)

        m.add_axis_input("vertical", Keys.W, scale=1.0)
        m.add_axis_input("vertical", Keys.S, scale=-1.0)

        m.add_action_input("light", Keys.J)
        m.add_action_input("grab", Keys.K)
        m.add_action_input("parry", Keys.L)
        m.add_action_input("heavy", Keys.I)

    @staticmethod
    def __get_item__(item):
        return Input.manager.actions
