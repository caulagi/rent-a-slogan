'''
The client manager manages data in client table
'''
import asyncpg
from datetime import datetime

from const import connection_url


class ClientManager(object):
    async def init(self):
        conn = await asyncpg.connect(connection_url())
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS client (
                fd               INTEGER,
                identifier       TEXT,
                connected_on     TIMESTAMPTZ,
                active           BOOLEAN DEFAULT TRUE
            );
            CREATE INDEX ON client (active);
            CREATE INDEX ON client (identifier);
        ''')
        self._initialized = True

    async def create(self, fd, identifier):
        conn = await asyncpg.connect(connection_url())
        await conn.execute(
            'INSERT INTO client (fd, identifier, connected_on) values ($1, $2, $3)',
            fd, identifier, datetime.now())

    async def deactivate(self, identifier):
        conn = await asyncpg.connect(connection_url())
        await conn.execute('UPDATE client SET active = FALSE where identifier = $1', identifier)

    async def deactivate_all(self):
        conn = await asyncpg.connect(connection_url())
        await conn.execute('UPDATE client SET active = FALSE')

    async def list(self):
        'Return count of active clients'
        conn = await asyncpg.connect(connection_url())
        res = await conn.fetch('select fd, identifier from client where active = TRUE')
        return ['{}:{}'.format(p['fd'], p['identifier']) for p in res]
