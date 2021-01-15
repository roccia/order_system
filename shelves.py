import random
from termcolor import colored
from model import OrderInfo, Shelf


class Shelves(object):
    def __init__(self, order: object, ordinary_shelf: Shelf, overflow_shelf: Shelf, order_created_at: int):
        self.order = order
        self.order_created_at = order_created_at
        self.wasted_orders = []
        self.ordinary_shelf = ordinary_shelf
        self.ofs = overflow_shelf

    async def place2overflow(self, order_info: OrderInfo, wasted_orders: list) -> OrderInfo:
        """
         check overflow cap,
         first check is there any decayed order,if true place to waste
         second if no more room, remove random order from overflow to waste
         else place order to overflow
        :param order_info:
        :param wasted_orders:
        :return: OrderInfo
        """
        await self.ofs.discard_decayed_orders(wasted_orders=wasted_orders, delay_time=0)

        if self.ofs.remaining_cap == 0:
            random_order = random.choice(self.ofs.placed_orders)
            print(colored(
                '{0} shelf is full remove random order {1} and place to waste '.format(self.ofs.name,
                                                                                       random_order.order['id']),
                'yellow'))

            await self.ofs.remove(order_info=random_order)
            wasted_orders.append(random_order)
            order_info = OrderInfo(order=self.order, created_at=self.order_created_at, is_delivered=False,
                                   is_on_shelf=False)
            return order_info

        await self.ofs.add(order_info=order_info)
        order_info.shelf = self.ofs

        return order_info

    async def place2shelf(self, wasted_orders: list) -> OrderInfo:
        """
        place order to ordinary shelf,
        first check is there any decayed order,if true place to waste
        second check if current shelf is full,if true move order to overflow
        :param wasted_orders:
        :return: OrderInfo
        """
        await self.ordinary_shelf.discard_decayed_orders(wasted_orders=wasted_orders, delay_time=0)

        order_info = OrderInfo(order=self.order, created_at=self.order_created_at, shelf=self.ordinary_shelf)

        if self.ordinary_shelf.remaining_cap == 0:
            placed_orders = [order_info.order for order_info in self.ordinary_shelf.placed_orders]
            print(colored('{0} shelf is full place to overflow, current orders: \n{1} '.format(self.ordinary_shelf.name,
                                                                                               placed_orders),
                          'yellow'))
            order_info = await self.place2overflow(order_info=order_info, wasted_orders=wasted_orders)
            return order_info

        await self.ordinary_shelf.add(order_info=order_info)
        return order_info
