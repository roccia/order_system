import time
from termcolor import colored


class OrderInfo(object):
    def __init__(self, order: object,
                 created_at: int,
                 is_delivered=None,
                 is_on_shelf=None,
                 shelf=None,
                 decay_time=None,
                 courier_arrive_at=None):
        self.order = order
        self.created_at = created_at
        self.is_delivered = is_delivered
        self.shelf = shelf
        self.is_on_shelf = is_on_shelf
        self.courier_arrive_at = courier_arrive_at
        self.decay_time = decay_time


class Shelf(object):
    def __init__(self, capacity: int, name: str, decay_modifier: int):
        """

        :param capacity:
        :param name:
        :param decay_modifier:
        """
        self.capacity = capacity
        self.placed_orders = []
        self.remaining_cap = capacity
        self.name = name
        self.decay_modifier = decay_modifier

    async def add(self, order_info: OrderInfo):
        """
        add order to shelf
        :param order_info:
        :return:
        """
        self.placed_orders.append(order_info)
        self.remaining_cap = self.capacity - len(self.placed_orders)
        order_info.is_delivered = False
        order_info.is_on_shelf = True

    async def remove(self, order_info: OrderInfo):
        """
        remove order from shelf
        :param order_info:
        :return:
        """
        self.placed_orders.remove(order_info)
        self.remaining_cap = self.capacity - len(self.placed_orders)
        order_info.is_delivered = False
        order_info.is_on_shelf = False

    async def discard_decayed_orders(self, wasted_orders: list, delay_time: int) -> list:
        """
        discard decayed orders
        :param wasted_orders:
        :param delay_time:
        :return:
        """
        if len(self.placed_orders) > 0:
            for order_info in self.placed_orders:
                order_info.decay_time, order_info.courier_arrive_at = self.cal_decay_time(order_info, delay_time)
                if order_info.decay_time <= 0:
                    await self.remove(order_info)
                    wasted_orders.append(order_info)
                    print(colored(
                        'remove decayed order {0} on shelf {1} to waste '.format(order_info.order['id'], self.name),
                        'yellow'))
        return wasted_orders

    @staticmethod
    def cal_decay_time(order_info: OrderInfo, delay_time: int) -> (float, int):
        """
        :param order_info:
        :param delay_time:  could be current time or courier arriving time(2-6 sec)
        :return:
        """
        current_time = int(round(time.time() * 1000))
        # TODO courier_arrive_at is not a good variable name,
        #  when delay_time is 0, courier_arrive_at means the order queue is self-checking order age
        #  when delay_time > 0, courier_arrive_at represents what it meant to be
        courier_arrive_at = current_time + delay_time * 1000
        order_age = (current_time - order_info.created_at) / 1000.0 + delay_time

        decay_time = (order_info.order['shelfLife'] - order_age - order_info.order[
            'decayRate'] * order_age * order_info.shelf.decay_modifier) / order_info.order['shelfLife']
        return decay_time, courier_arrive_at


def init_shelves() -> object:
    shelf_mapping = {
        'hot': Shelf(capacity=10, name='hot', decay_modifier=1),
        'cold': Shelf(capacity=10, name='cold', decay_modifier=1),
        'frozen': Shelf(capacity=10, name='frozen', decay_modifier=1),
        'overflow': Shelf(capacity=15, name='overflow', decay_modifier=2),
    }
    return shelf_mapping
