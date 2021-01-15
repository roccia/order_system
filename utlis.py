import datetime
import json
from termcolor import colored

from model import OrderInfo


def read_file(file_path: str) -> object:
    return json.load(open(file_path))


def millsecond2Datetime(mills: int) -> datetime:
    return datetime.datetime.fromtimestamp(mills / 1000.0)


def format_delivery_msg(order_info: OrderInfo) -> str:
    placed_orders = [order.__dict__ for order in order_info.shelf.placed_orders]
    msg = colored(order_info.order['id'], 'green') + \
          '\ndelivered: ' + colored(order_info.is_delivered, 'green') + \
          '\ncourier arrived at: ' + colored(millsecond2Datetime(order_info.courier_arrive_at), 'green') + \
          '\ndecay time: ' + colored(order_info.decay_time, 'green') + \
          '\nshelf_info: ' + colored('{0} -- {1}'.format(order_info.shelf.name, placed_orders), 'green')

    return msg


def format_process_msg(order_info: OrderInfo) -> str:
    if not order_info.shelf:
        msg = colored(order_info.order['id'], 'red') + ' has been placed to: ' + \
              colored('wasted', 'red') + ' at ' + colored(millsecond2Datetime(order_info.created_at), 'red')
    else:
        msg = colored(order_info.order['id'], 'red') + ' has been placed to: ' + \
              colored(order_info.shelf.name, 'red') + ' shelf at ' + \
              colored(millsecond2Datetime(order_info.created_at), 'red')
    return msg



