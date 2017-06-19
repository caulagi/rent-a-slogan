'''
The slogan manager is the interface between python
and sqlite for the slogan table
'''
import asyncpg
import hashlib
from datetime import datetime, timedelta


class SloganManager(object):
    '''
    The slogan table has -
        title (text) - the actual slogan
        md5 (text) - used to ensure uniqueness
        rented_on (datetime) - if the slogan is rented, the datetime field
        rented_by (text) - socket identifier
    '''

    EXPIRE_AFTER_SECONDS = 15
    PG_USERNAME = 'postgres'
    PG_DATABASE = 'rent-slogan'
    PG_PASSWORD = '1234'

    @classmethod
    def connection_url(cls):
        return 'postgresql://{}:{}@localhost/{}'.format(
            cls.PG_USERNAME, cls.PG_PASSWORD, cls.PG_DATABASE)

    async def init(self):
        conn = await asyncpg.connect(self.connection_url())
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS slogan (
                id serial PRIMARY KEY,
                title TEXT,
                md5 TEXT UNIQUE,
                rented_on TIME NULL,
                rented_by INTEGER UNIQUE NULL
            );
        ''')
        self._initialized = True

    @staticmethod
    def get_md5(title):
        h = hashlib.md5()
        h.update(title.encode('utf-8'))
        return h.hexdigest()

    async def create(self, title):
        'Store the slogan identified by the title to database.  Return a tuple of (status, title)'
        conn = await asyncpg.connect(self.connection_url())
        try:
            await conn.execute(
                'INSERT INTO slogan (title, md5, rented_by, rented_on) VALUES ($1, $2, $3, $4)',
                title, self.get_md5(title), None, None)
        except asyncpg.PostgresError as e:
            print(e)
            return (False, 'error: slogan already exists')
        finally:
            await conn.close()
        return (True, title)

    async def _expire_slogans(self, conn):
        async with conn.transaction():
            await conn.execute(
                'UPDATE slogan SET rented_on = NULL, rented_by = NULL WHERE rented_on < $1',
                datetime.now() - timedelta(seconds=self.EXPIRE_AFTER_SECONDS))

    async def _find_rent(self, conn, rented_by):
        async with conn.transaction():
            await conn.execute(
                'UPDATE slogan SET rented_on = $1, rented_by = $2 WHERE id = (SELECT id FROM slogan WHERE rented_on IS NULL LIMIT 1)',
                datetime.now(), rented_by)
            return await conn.fetchrow('SELECT title FROM slogan WHERE rented_by = $1', rented_by)

    async def rent(self, rented_by):
        'Find any available slogan to rent. Return a tuple of (status, title)'
        conn = await asyncpg.connect(self.connection_url())
        await self._expire_slogans(conn)
        rent_exists = await conn.fetchrow('SELECT 1 FROM slogan WHERE rented_by = $1', rented_by)
        if rent_exists:
            return (False, 'error: You can rent only one slogan per client')
        row = await self._find_rent(conn, rented_by)
        return (True, row['title'])

    async def list(self):
        results = []
        conn = await asyncpg.connect(self.connection_url())
        raw = await conn.fetch('select title, rented_on, rented_by from slogan')
        for row in raw:
            status = 'not rented' if not row[1] else 'rented by {}'.format(row[2])
            results.append('{} - {}'.format(row[0], status))
        return results
