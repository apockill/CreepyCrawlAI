import sys

# Do an import hack to replace the godot libraries with mocks for testing
import tests.godot_mock

sys.modules["godot"] = tests.godot_mock
