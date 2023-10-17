"""
Module for generating array api code that works with Numba.
"""

from __future__ import annotations

from egglog import *
from egglog.exp.array_api import *

array_api_numba_module = Module([array_api_module])

# For these rules, we not only wanna rewrite, we also want to delete the original expression,
# so that the rewritten one is used, even if the original one is simpler.

# TODO: Add back delete and remove high cost if we can get that to work
# https://egraphs.zulipchat.com/#narrow/stream/375765-egglog/topic/replacing.20an.20expression.20with.20delete


# Rewrite mean(x, <int>, <expand dims>) to use sum b/c numba cant do mean with axis
# https://github.com/numba/numba/issues/1269
@array_api_numba_module.register
def _mean(y: NDArray, x: NDArray, i: Int):
    axis = OptionalIntOrTuple.some(IntOrTuple.int(i))
    res = sum(x, axis) / NDArray.scalar(Value.int(x.shape[i]))

    yield rule(eq(y).to(mean(x, axis, FALSE))).then(
        # delete(mean(x, axis, FALSE)),
        union(y).with_(res),
    )
    yield rule(eq(y).to(mean(x, axis, TRUE))).then(
        # delete(mean(x, axis, TRUE)),
        union(y).with_(expand_dims(res, i)),
    )
    # rewrite(mean(x, axis, FALSE)).to(res),
    # rewrite(mean(x, axis, TRUE)).to(expand_dims(res, i)),
    # ]


# Rewrite std(x, <int>) to use mean and sum b/c numba cant do std with axis


@array_api_numba_module.register
def _std(y: NDArray, x: NDArray, i: Int):
    axis = OptionalIntOrTuple.some(IntOrTuple.int(i))
    # https://numpy.org/doc/stable/reference/generated/numpy.std.html
    # "std = sqrt(mean(x)), where x = abs(a - a.mean())**2."
    yield rule(eq(y).to(std(x, axis))).then(
        # delete(std(x, axis)),
        union(y).with_(sqrt(mean(square(x - mean(x, axis, TRUE)), axis))),
    )
    # return [
    #     rewrite(std(x, axis)).to(
    #         sqrt(mean(square(abs(x - mean(x, axis, keepdims=TRUE))), axis))
    #     ),
    # ]
