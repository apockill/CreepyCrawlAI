from pathlib import Path

new_instance_id = 1


class Input:
    pass


class Node:
    def __init__(self):
        global new_instance_id
        self._instance_id = new_instance_id
        new_instance_id += 1

    def get_instance_id(self):
        return self._instance_id

    def add_child(self, node):
        assert isinstance(node, Node)

    def set_position(self, vector2):
        assert isinstance(vector2, Vector2)
        assert vector2
        self._position = vector2

    def queue_free(self):
        return


class Node2D(Node):
    pass


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Sprite(Node2D):
    pass


class ResourceLoader:
    @staticmethod
    def load(resource_path: str):
        """Verify the resource path exists"""
        resource_path = resource_path.replace("res://", "")
        assert Path(resource_path).is_file()

        class Unloaded:
            def instance(self):
                return Sprite()

        return Unloaded()


class InputEventMouseButton:
    pass


BUTTON_LEFT = 1
