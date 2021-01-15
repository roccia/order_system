import asyncio
import random
import time
import nest_asyncio
from courier import Courier
from model import init_shelves
from shelves import Shelves
from utlis import read_file, format_process_msg
from termcolor import colored


class OrderSystem(object):
    def __init__(self, config):
        self.data = read_file(config['file_path'])
        self.processing_num = config['processing_num']
        self.delay_rate = config['delay_rate']
        self.deliver_time_range = config['deliver_time_range']
        self.wasted_orders = []
        self.delivered_orders = []
        self.shelf_mapping = init_shelves()  # initialize shelf object
        self.loop = asyncio.new_event_loop()
        nest_asyncio.apply(self.loop)
        asyncio.set_event_loop(self.loop)
        self.order_queue = asyncio.Queue(maxsize=len(self.data))

    async def consumer(self):
        """
        consume order from queue, terminated the program if all orders in queue have been processed,
        :return:
        """
        try:
            while True:
                order_info = await self.order_queue.get()
                if not order_info:
                    continue

                if order_info == 'finished':
                    self.order_queue.task_done()
                    break

                print('\n########## consume order queue #############')
                courier_delay_time = random.randint(self.deliver_time_range[0], self.deliver_time_range[1])
                print(colored('consumer get {0} ,start dispatching to courier in: {1} seconds'.
                              format(order_info.order['id'], courier_delay_time), 'green'))

                await asyncio.sleep(courier_delay_time)
                try:
                    courier = Courier(delay_time=courier_delay_time, order_info=order_info)
                    deliver_msg = await courier.deliver_order(wasted_orders=self.wasted_orders)
                    print('\n&&&&&&&&&&&& deliver info &&&&&&&&&&&&')
                    print(deliver_msg)
                    self.delivered_orders.append(order_info)
                except Exception as e:
                    print(colored("Catch Exception {0}".format(e)), 'red')
                    raise
                finally:
                    self.order_queue.task_done()
        except asyncio.CancelledError:
            print("worker is being cancelled")
            raise
        finally:
            print('\n########## all orders have been processed,system terminated #############')

    async def producer(self):
        """
        produce order by defined policy, the last element in order_queue is a stop single-->'finished', to
        indicate all orders have been inserted
        :return:
        """
        for i in range(0, len(self.data), self.processing_num):
            orders = self.data[i:i + self.processing_num]
            order_created_at = int(round(time.time() * 1000))
            print('\n--------- order placing -----------')
            await self._placing_order(orders=orders, order_created_at=order_created_at)
            await asyncio.sleep(self.delay_rate)

        await self.order_queue.put('finished')
        await self.order_queue.join()

    async def _placing_order(self, orders: list, order_created_at: int):
        """
         insert single order to queue, then place order to shelf,before placing, shelves objects need to be initialized
        :param orders:
        :param order_created_at:
        :return:
        """
        for order in orders:
            if not order:
                await self.order_queue.put(None)
            else:
                ordinary_shelf = self.shelf_mapping[order['temp']]
                overflow_shelf = self.shelf_mapping['overflow']
                shelves = Shelves(order=order, ordinary_shelf=ordinary_shelf, overflow_shelf=overflow_shelf,
                                  order_created_at=order_created_at)
                order_info = await shelves.place2shelf(wasted_orders=self.wasted_orders)
                print('#######', order_info.__dict__)
                placing_msg = format_process_msg(order_info=order_info)
                print(placing_msg)
                await self.order_queue.put(order_info)

    async def run(self):
        await asyncio.gather(self.producer(), self.consumer(), return_exceptions=True)
