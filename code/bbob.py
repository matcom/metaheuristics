from __future__ import annotations

import logging
import random
from collections import namedtuple
from typing import Callable, Optional, Tuple

import numpy as np
from scipy.stats import cauchy


def _ensure_ndarray(func):
    def wrapper(x, *args, **kwargs):
        if isinstance(x, float):
            x = [x]
        x = np.array(x)
        return func(x, *args, **kwargs)

    return wrapper


def _reset_rngs(func):
    def wrapper(self: BBOB, *args, seed: Optional[int] = None, **kwargs):
        self.reset_rngs(seed=seed)
        return func(self, *args, **kwargs)

    return wrapper


class BBOBFunc:
    def __init__(
        self,
        name: str,
        dim: int,
        x_opt: np.ndarray,
        f_opt: float,
        func: Callable,
    ):
        self.name = name
        self.dim = dim
        self.x_opt = x_opt
        self.f_opt = f_opt
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self) -> str:
        ans = f"BBOB {self.name} function instance:\n"
        ans += f"  dim:    {self.dim}\n"
        ans += f"  x_opt:  {self.x_opt}\n"
        ans += f"  f_opt:  {self.f_opt}"
        return ans

    def __str__(self) -> str:
        return repr(self)

    def _plot_1d(self, show: bool = True):
        import matplotlib.pyplot as plt

        X = np.linspace(-5, 5, 200)
        Y = [self.func(np.array([x])) for x in X]
        plt.plot(X, Y)
        plt.plot([self.x_opt], [self.f_opt], "ro")
        if show:
            plt.show()

    def _plot_2d(self, show: bool = True):
        import matplotlib.pyplot as plt

        x = np.linspace(-5, 5, 200)
        X, Y = np.meshgrid(x, x)
        Z = np.array([[self.func(np.array([x1, x2])) for x1 in x] for x2 in x])
        ax = plt.figure().add_subplot(projection="3d")
        min_loc = list(self.x_opt)
        min_loc.append(self.f_opt)
        ax.plot(*min_loc, "ro")
        ax.plot_surface(
            X, Y, Z, cmap="viridis_r", alpha=0.9, linewidth=0, edgecolor="none"
        )
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        plt.tight_layout()
        if show:
            plt.show()

    def plot(self, show: bool = True):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logging.error(
                "Function plot failed. Matplotlib library not found. "
                "You can install it by doing: 'pip install matplotlib'."
            )
            return
        if self.dim == 1:
            self._plot_1d(show)
        elif self.dim == 2:
            self._plot_2d(show)
        else:
            raise ValueError("Can not plot functions where D > 2")


class BBOB:
    def __init__(self, seed=None):
        self.seed = seed
        self.np_rng = np.random.default_rng(seed)
        self.rng = random.Random(seed)

    def reset_rngs(self, seed: Optional[int] = None):
        seed = self.seed if seed is None else seed
        self.np_rng = np.random.default_rng(seed)
        self.rng = random.Random(seed)

    def _random_x_opt(self, dim, min_x=-5, max_x=5):
        return self.np_rng.random(dim) * (max_x - min_x) + min_x

    def _random_f_opt(self) -> float:
        val = round(cauchy.rvs(loc=0.0, scale=100, random_state=self.seed), 2)
        val = min(1_000, val)
        val = max(-1_000, val)
        return val

    def _get_vars(
        self, dim: Optional[int], min_dim: int = 1
    ) -> Tuple[int, np.ndarray, float]:
        if dim is None:
            dim = self.rng.randint(min_dim, 20)
        x_opt = self._random_x_opt(dim)
        f_opt = self._random_f_opt()

        return dim, x_opt, f_opt

    def _tosz_transf(self, x: np.ndarray) -> np.ndarray:
        x_c1 = x * np.where(x > 0, 10, 5.5)
        x_c2 = x * np.where(x > 0, 7.9, 3.1)
        non_zeros = np.abs(x) > 1e-5
        x_hat = np.log(np.abs(x) * non_zeros, where=non_zeros)
        return np.sign(x) * np.exp(x_hat + 0.049 * (np.sin(x_c1) + np.sin(x_c2)))

    def _tasy_transf(self, x: np.ndarray, beta: float) -> np.ndarray:
        D = x.shape[0]
        idx = np.where(x > 0)
        _x = x[idx]
        x[idx] = np.power(_x, np.sqrt(_x) * beta * idx / (D - 1) + 1)
        return x

    def _diag_matrix(self, alpha: float, D: int) -> np.ndarray:
        A = np.zeros((D, D))
        idx = np.diag_indices(D)
        A[idx] = alpha
        A[idx] = np.power(A[idx], 0.5 * np.arange(0, D) / (D - 1))
        return A

    def _f_pen(self, x: np.ndarray) -> float:
        return sum([max(0, abs(x_i) - 5) ** 2 for x_i in x])

    @_reset_rngs
    def sphere_func(
        self,
        dim: Optional[int] = None,
    ) -> BBOBFunc:
        D, x_opt, f_opt = self._get_vars(dim)

        @_ensure_ndarray
        def _func(x: np.ndarray) -> float:
            return float(np.linalg.norm(x - x_opt)) ** 2 + f_opt

        return BBOBFunc("sphere", D, x_opt, f_opt, _func)

    @_reset_rngs
    def ellipsodial_func(
        self,
        dim: Optional[int] = None,
    ) -> BBOBFunc:
        D, x_opt, f_opt = self._get_vars(dim)

        @_ensure_ndarray
        def _func(x: np.ndarray) -> float:
            z = self._tosz_transf(x - x_opt)
            ans = 0
            for i in range(D):
                ans += z[i] ** 2 * 10 ** (6 * i / D - 1)
            return ans + f_opt

        return BBOBFunc("ellipsodial", D, x_opt, f_opt, _func)

    @_reset_rngs
    def rastrigin_func(
        self,
        dim: Optional[int] = None,
    ) -> BBOBFunc:
        D, x_opt, f_opt = self._get_vars(dim, min_dim=2)

        assert D > 1, "dim value must be grater thatn 1 for this function"

        @_ensure_ndarray
        def _func(x: np.ndarray) -> float:
            A = self._diag_matrix(alpha=10, D=D)
            z = np.dot(
                A,
                self._tasy_transf(
                    self._tosz_transf(x - x_opt),
                    beta=0.2,
                ),
            )
            return (
                10 * (D - np.sum(np.cos(2 * np.pi * z)))
                + np.linalg.norm(z) ** 2
                + f_opt
            )

        return BBOBFunc("rastrigin", D, x_opt, f_opt, _func)

    @_reset_rngs
    def buche_rastrigin_func(
        self,
        dim: Optional[int] = None,
    ) -> BBOBFunc:
        D, x_opt, f_opt = self._get_vars(dim)

        assert D > 1, "dim value must be grater thatn 1 for this function"

        mask = np.zeros(D, dtype=bool)
        mask[np.arange(0, D, 2)] = True

        @_ensure_ndarray
        def _func(x: np.ndarray) -> float:
            s = np.array((D,))
            s.fill(10)
            s = np.power(s, np.arange(0, D) * 0.5 / (D - 1))
            s[mask] *= 10
            z = s * self._tosz_transf(x - x_opt)
            return (
                10 * (D - np.sum(np.cos(2 * np.pi * z)))
                + np.sum(z**2)
                + 100 * self._f_pen(x)
                + f_opt
            )

        return BBOBFunc("buche-rastrigin", D, x_opt, f_opt, _func)

    @_reset_rngs
    def linear_slpoe_func(
        self,
        dim: Optional[int] = None,
    ) -> BBOBFunc:
        D, _, f_opt = self._get_vars(dim)

        assert D > 1, "dim value must be grater thatn 1 for this function"

        x_opt = self.np_rng.random(D) - 0.5
        x_opt[x_opt >= 0] = 1
        x_opt[x_opt < 0] = -1
        x_opt *= 5

        mask = np.zeros(D, dtype=bool)
        mask[np.arange(0, D, 2)] = True

        @_ensure_ndarray
        def _func(x: np.ndarray) -> float:
            s = np.array((D,))
            s.fill(10)
            s = np.power(s, np.arange(0, D) / (D - 1))
            s *= np.sign(x_opt)
            s[mask] *= 10
            z = np.array([x[i] if x_opt[i] * x[i] < 25 else x_opt[i] for i in range(D)])
            return np.sum(5 * np.abs(s) - s * z) + f_opt

        return BBOBFunc("linear slope", D, x_opt, f_opt, _func)
