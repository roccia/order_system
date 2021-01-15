import asyncio
from order import OrderSystem
from utlis import read_file

if __name__ == '__main__':
    config = read_file('config.json')
    od = OrderSystem(config)
    asyncio.run(od.run())
    print('delivered orders', [order_info.order['id'] for order_info in od.delivered_orders])
    print('wasted orders', [order_info.order['id'] for order_info in od.wasted_orders])
