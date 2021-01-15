from termcolor import colored
from model import OrderInfo
from utlis import format_delivery_msg


class Courier(object):
    def __init__(self, delay_time: int, order_info: OrderInfo):
        self.delay_time = delay_time
        self.order_info = order_info

    async def deliver_order(self, wasted_orders: list) -> str:
        """
        deliver order:
        first, check if current order is on shelf
        second, check all orders on current shelf,remove decayed orders
        if current order is not decayed -> deliver
        :param wasted_orders:
        :return: msg
        """
        if not self.order_info:
            return colored('no order need to be deliver', 'yellow')

        if not self.order_info.is_on_shelf:
            return colored('order {0} not in shelf, do nothing'.format(self.order_info.order['id']), 'yellow')

        wasted_orders = await self.order_info.shelf.discard_decayed_orders(wasted_orders=wasted_orders, delay_time=self.delay_time)

        if self.order_info in wasted_orders:
            return colored('order {0} decayed,place to wasted'.format(self.order_info.order['id']), 'yellow')

        self.order_info.is_delivered = True
        self.order_info.is_on_shelf = False
        self.order_info.shelf.placed_orders.remove(self.order_info)
        self.order_info.shelf.remaining_cap = self.order_info.shelf.capacity - len(self.order_info.shelf.placed_orders)
        return format_delivery_msg(self.order_info)
