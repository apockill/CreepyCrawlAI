from typing import Any

import numpy as np
import numpy.typing as npt
from tf_agents.environments.py_environment import PyEnvironment
from tf_agents.specs import array_spec


class CritterEnvironment(PyEnvironment):
    def __init__(
        self,
        input_radius: int,
        input_dtype: npt.DTypeLike,
        n_choices: int,
        n_layers: int,
    ):
        super().__init__()
        input_shape = (input_radius * 2 + 1, input_radius * 2 + 1, n_layers)
        self._observation_spec = array_spec.ArraySpec(
            shape=input_shape, dtype=input_dtype, name="observation"
        )

        # TODO: Figure out how to get len(AiCritterMixin.CHOICES)
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int_, minimum=0, maximum=n_choices - 1, name="action"
        )

    @property
    def batched(self) -> bool:
        """By saying we are batched, then when TFPyEnvironment wraps this class
        it won't bother re-wrapping this environment in a BatchedPyEnvironment.
        :return: True
        """
        return True

    @property
    def batch_size(self) -> int:
        """By saying we are batched, then when TFPyEnvironment wraps this class
        it won't bother re-wrapping this environment in a BatchedPyEnvironment.
        :return: A constant batch size of 1
        """
        return 1

    def observation_spec(self) -> array_spec.ArraySpec:
        """Defines the observations provided by the environment.

        May use a subclass of `ArraySpec` that specifies additional properties such
        as min and max bounds on the values.

        :return: An `ArraySpec`, or a nested dict, list or tuple of `ArraySpec`s.
        """

        return self._observation_spec

    def action_spec(self) -> array_spec.BoundedArraySpec:
        """Defines the actions that should be provided to `step()`.

        May use a subclass of `ArraySpec` that specifies additional properties such
        as min and max bounds on the values.

        :return: An `ArraySpec`, or a nested dict, list or tuple of `ArraySpec`s.
        """
        return self._action_spec

    def _step(self, action: Any) -> None:
        raise NotImplementedError

    def _reset(self) -> None:
        raise NotImplementedError

    def get_info(self) -> None:
        raise NotImplementedError

    def get_state(self) -> None:
        raise NotImplementedError

    def set_state(self, state: Any) -> None:
        raise NotImplementedError
