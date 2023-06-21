import sys
import threading
import time
import types
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional


class Evaluation:
    def __init__(
        self,
        mh_name: str,
        solutions: List[Any],
        values: List[Any],
        total_evals: int,
        total_time: float,
        fail_msg: Optional[str],
    ):
        self.mh_name = mh_name
        self.solutions = solutions
        self.values = values
        self.iters = len(self.solutions)
        self.best_result = None if not self.solutions else self.solutions[-1]
        self.total_evals = total_evals
        self.total_time = total_time
        self.success = fail_msg is None
        self.fail_msg = fail_msg

    def __repr__(self) -> str:
        ans = (
            f"Evaluation of {self.mh_name}:\n"
            f"  best result --------------- {self.best_result}\n"
            f"  success ------------------- {self.success}\n"
            f"  iters --------------------- {self.iters}\n"
            f"  evals --------------------- {self.total_evals}\n"
            f"  time ---------------------- {self.total_time}\n"
        )
        if self.iters:
            ans += (
                f"  approx. evals per iter ---- {self.total_evals / self.iters}\n"
                f"  approx. iter time --------- {self.total_time / self.iters}\n"
            )
        if not self.success:
            ans += f"  fail reason: '{self.fail_msg}'\n"
        return ans

    def __str__(self) -> str:
        return repr(self)


class MetaHeuristic(ABC):
    @abstractmethod
    def solve(self, obj_fuc: Callable, *args, **kwargs) -> Any:
        """Solves a problem given an objective function"""
        raise NotImplementedError()

    def on_new_solution(self, sol: Any, val: Any):
        """This function is called every time a new solution is found"""

    def evaluate(
        self,
        obj_func: Callable,
        max_evals: Optional[int] = None,
        max_iters: Optional[int] = None,
        max_time: Optional[float] = None,
        check_every: float = 0.00001,
        verbose: bool = True,
        *args,
        **kwargs,
    ) -> Evaluation:
        if verbose:
            print(f"Evaluating {self.__class__.__name__}", flush=True)
        evals = 0
        solutions = []
        values = []
        fail_msg = None

        def _obj_func(*args, **kwargs):
            nonlocal evals
            nonlocal fail_msg

            if fail_msg is not None:
                sys.exit(0)

            if max_evals is not None and evals == max_evals:
                fail_msg = "Obj. function max evaluation exceeded."
                sys.exit(0)

            evals += 1
            return obj_func(*args, **kwargs)

        def _solve_func():
            nonlocal solutions
            nonlocal values
            nonlocal fail_msg
            sol = self.solve(_obj_func, *args, **kwargs)
            if isinstance(sol, types.GeneratorType):
                for s, v in sol:
                    if verbose:
                        print(" " * 100, end="\r")
                        print(
                            f"{time.time() - t0:.3f}s - Last value: {v} - Last solution: {s}",
                            end="\r",
                            flush=True,
                        )
                    self.on_new_solution(s, v)
                    solutions.append(s)
                    values.append(v)
                    if max_iters is not None and len(solutions) == max_iters:
                        fail_msg = "Max iterations exceeded."
                        sys.exit(0)
            elif isinstance(sol, tuple) and len(sol) == 2:
                solutions = [sol[0]]
                values = [sol[1]]
            else:
                raise ValueError(
                    "The 'solve' function must return tuples of size 2: (solution, value)."
                )
            print()

        proc = threading.Thread(target=_solve_func)

        t0 = time.time()
        proc.start()
        if max_time is not None:
            t1 = time.time()
            failed = True
            while t1 - t0 < max_time:
                if not proc.is_alive():
                    failed = False
                    break
                time.sleep(check_every)
                t1 = time.time()
            if failed:
                fail_msg = "Max time exceeded."
        else:
            proc.join()
            t1 = time.time()

        total_time = t1 - t0

        res = Evaluation(
            self.__class__.__name__,
            solutions=solutions,
            values=values,
            total_evals=evals,
            total_time=total_time,
            fail_msg=fail_msg,
        )
        return res
