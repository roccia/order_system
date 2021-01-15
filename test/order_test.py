import time
import pytest
from courier import Courier
from order import OrderSystem
from shelves import Shelves


class TestOrderSystem:
    def setup(self):
        config = {
            'file_path': 'test/test.json',
            'processing_num': 2,  # num of orders to process
            'delay_rate': 1,  # order processing rate in second
            'deliver_time_range': [0, 1]  # courier start delivery seconds
        }
        self.od = OrderSystem(config)

    @pytest.mark.asyncio
    async def test_placing_order(self):
        order_created_at = int(round(time.time() * 1000))
        await self.od._placing_order(self.od.data, order_created_at)
        assert len(self.od.data) == self.od.order_queue.qsize()

    async def setup_order_info(self, wasted_orders, ordinary_shelf, overflow_shelf):
        order = self.od.data[0]
        order_created_at = int(round(time.time() * 1000))
        shelves = Shelves(order=order, ordinary_shelf=ordinary_shelf, overflow_shelf=overflow_shelf,
                          order_created_at=order_created_at)
        order_info = await shelves.place2shelf(wasted_orders=wasted_orders)
        return order, order_info

    @pytest.mark.asyncio
    async def test_place2shelf_success(self):
        ordinary_shelf = self.od.shelf_mapping['frozen']
        overflow_shelf = self.od.shelf_mapping['overflow']
        order, order_info = await self.setup_order_info([], ordinary_shelf, overflow_shelf)
        assert order_info.shelf.name == 'frozen'
        assert order_info.order['id'] == order['id']

    @pytest.mark.asyncio
    async def test_place2overflow_success(self):
        ordinary_shelf = self.od.shelf_mapping['frozen']
        overflow_shelf = self.od.shelf_mapping['overflow']
        ordinary_shelf.remaining_cap = 0  # frozen if full
        order, order_info = await self.setup_order_info([], ordinary_shelf, overflow_shelf)
        assert order_info.shelf.name == 'overflow'
        assert order_info.order['id'] == order['id']

    @pytest.mark.asyncio
    async def test_place2waste_success(self):
        # insert one order to frozen
        wasted_orders = []
        ordinary_shelf = self.od.shelf_mapping['frozen']
        overflow_shelf = self.od.shelf_mapping['overflow']
        order2waste = self.od.data[0]
        order, order_info = await self.setup_order_info(wasted_orders, ordinary_shelf, overflow_shelf)

        overflow_shelf.placed_orders.append(order_info)
        ordinary_shelf.remaining_cap = 0  # set frozen  full
        overflow_shelf.remaining_cap = 0  # set overflow  full
        order2waste_created_at = int(round(time.time() * 1000))

        shelves = Shelves(order=order2waste, ordinary_shelf=ordinary_shelf, overflow_shelf=overflow_shelf,
                          order_created_at=order2waste_created_at)
        await shelves.place2shelf(wasted_orders=wasted_orders)

        assert wasted_orders[0].order['id'] == order2waste['id']

    @pytest.mark.asyncio
    async def test_discard_orders_on_shelf(self):
        ordinary_shelf = self.od.shelf_mapping['frozen']
        overflow_shelf = self.od.shelf_mapping['overflow']
        order, order_info = await self.setup_order_info([], ordinary_shelf, overflow_shelf)
        wasted_orders = await ordinary_shelf.discard_decayed_orders([], 100)
        assert wasted_orders != []
        assert wasted_orders[0].order['id'] == order['id']

    @pytest.mark.asyncio
    async def test_deliver_order_success(self):
        ordinary_shelf = self.od.shelf_mapping['frozen']
        overflow_shelf = self.od.shelf_mapping['overflow']
        order, order_info = await self.setup_order_info([], ordinary_shelf, overflow_shelf)
        courier = Courier(delay_time=2, order_info=order_info)
        msg = await courier.deliver_order([])
        print(msg)
        assert 'delivered: \x1b[32mTrue\x1b[0m' in msg

    @pytest.mark.asyncio
    async def test_deliver_order_fail(self):
        ordinary_shelf = self.od.shelf_mapping['frozen']
        overflow_shelf = self.od.shelf_mapping['overflow']
        order, order_info = await self.setup_order_info([], ordinary_shelf, overflow_shelf)
        order_info.is_on_shelf = False
        courier = Courier(delay_time=2, order_info=order_info)
        msg = await courier.deliver_order(wasted_orders=[])
        print(msg)
        assert 'not in shelf' in msg
