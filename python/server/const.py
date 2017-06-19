PG_USERNAME = 'postgres'
PG_DATABASE = 'rent-slogan'
PG_PASSWORD = '1234'


def connection_url():
    return 'postgresql://{}:{}@localhost/{}'.format(PG_USERNAME, PG_PASSWORD,
                                                    PG_DATABASE)
