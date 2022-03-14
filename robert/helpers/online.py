import typing as t
from wallex import Wallex

from retry import retry


@retry()
def canceler(wl: Wallex, order: t.Union[t.Text, t.Dict]) -> t.Dict:
    if type(order) == dict:
        _ = wl.cancel_order(
            order.get('clientOrderId'),
        )
    elif type(order) == str:
        _ = wl.cancel_order(
            order,
        )
    else:
        raise TypeError(f'{type(order)} is not a valid type for canceler')

    return _
