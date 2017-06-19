'''
rent-a-slogan server

    * listens on port 25001 and opens a socket for each new client
'''
import argparse
import asyncio
import gc
import uvloop

from slogan_manager import SloganManager


CLRF = '\r\n'


class SloganProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        print('new connection: {}'.format(transport.get_extra_info('socket')))
        self.transport = transport
        self.slogan_manager = SloganManager()

    def connection_lost(self, exc):
        print('closed connection: {}'.format(self.transport.get_extra_info('socket')))
        self.transport = None
        self.slogan_manager = None

    def data_received(self, data):
        data = data.decode()
        try:
            cmd, rest = data.split('::')
        except ValueError:
            cmd, rest = (data, '')
        cmd, rest = cmd.strip(), rest.strip()
        self.run_cmd(cmd, rest)

    async def status(self):
        return await self.slogan_manager.list()

    def handle_status_result(self, task):
        res = task.result()
        self.transport.write('Slogans:'.encode('utf-8'))
        self.transport.write(CLRF.join(res).encode('utf-8'))
        self.transport.write(CLRF.encode('utf-8'))
        task = asyncio.async(self.status_clients())
        task.add_done_callback(self.handle_status_clients_result)

    async def status_clients(self):
        return await self.client_manager.list()

    def handle_status_clients_result(self, task):
        res = task.result()
        self.transport.write('Clients:'.encode('utf-8'))
        self.transport.write(CLRF.join(res).encode('utf-8'))
        self.transport.write(CLRF.encode('utf-8'))

    async def rent(self):
        sock = self.transport.get_extra_info('socket')
        return await self.slogan_manager.rent(sock.fileno())

    def handle_rent_result(self, task):
        _, res = task.result()
        self.transport.write(res.encode('utf-8'))
        self.transport.write(CLRF.encode('utf-8'))

    async def add(self, slogan):
        return await self.slogan_manager.create(slogan)

    def handle_add_result(self, task):
        _, res = task.result()
        self.transport.write(res.encode('utf-8'))
        self.transport.write(CLRF.encode('utf-8'))

    def run_cmd(self, cmd, slogan=None):
        cmd = cmd.lower()
        if cmd == 'add':
            task = asyncio.async(self.add(slogan))
            task.add_done_callback(self.handle_add_result)
        elif cmd == 'status':
            task = asyncio.async(self.status())
            task.add_done_callback(self.handle_status_result)
        elif cmd == 'rent':
            task = asyncio.async(self.rent())
            task.add_done_callback(self.handle_rent_result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=25001, type=int)
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()

    loop = uvloop.new_event_loop()
    print('using UVLoop')
    asyncio.set_event_loop(loop)

    loop.set_debug(args.debug)

    print('serving on: 127.0.0.1:{}'.format(args.port))
    coro = loop.create_server(SloganProtocol, *('127.0.0.1', args.port))
    srv = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        gc.collect()
        if args.debug:
            loop.print_debug_info()
        loop.close()
