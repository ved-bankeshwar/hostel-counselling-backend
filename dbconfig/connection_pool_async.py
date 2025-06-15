import psycopg_pool
from configparser import ConfigParser
import logging
import const_configs
# Configure logging
logger = logging.getLogger(__name__)

connection_pool_async = None

# async def init_connection_pool_async(minconn, maxconn, filename='database.ini', section='postgresql'):
#     global connection_pool_async
#     parser = ConfigParser()
#     parser.read(filename)
#     db_config = {}
#     if parser.has_section(section):
#         params = parser.items(section)
#         for param in params:
#             db_config[param[0]] = param[1]
#     else:
#         raise Exception('Section {0} not found in the {1} file'.format(section, filename))

#     conninfo = f'host={db_config["host"]} port={db_config["port"]} dbname={db_config["database"]} user={db_config["user"]} password={db_config["password"]}'

#     # Create the connection pool
#     connection_pool_new = psycopg_pool.AsyncConnectionPool(min_size=minconn, max_size=maxconn, conninfo=conninfo, num_workers=5)
#     await connection_pool_new.open()
#     connection_pool_async = connection_pool_new
#     return connection_pool_new


async def init_connection_pool_async(minconn=1, maxconn=20, filename='database.ini', section='postgresql'):
    global connection_pool_async
    parser = ConfigParser()
    parser.read(filename)
    db_config = {}
    if const_configs.global_setup == "local":
        section = "postgresql_local"
    elif const_configs.global_setup == "dev":
        section = "postgresql_dev"
    elif const_configs.global_setup == "prod":
        section = "postgresql_prod"
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_config[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))

    # options_value = f"-c search_path={db_config['schema']}"
    # encoded_options = urllib.parse.quote(options_value)
    # conninfo = f'postgresql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["database"]}?options={encoded_options}'
    conninfo = f'postgresql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["database"]}'

    logger.info(
        f"Initializing connection pool with min_size={minconn}, max_size={maxconn}"
    )

    # Create the connection pool
    connection_pool_new = psycopg_pool.AsyncConnectionPool(
        min_size=minconn,
        max_size=maxconn,
        conninfo=conninfo,
        num_workers=5,
        kwargs={
            # Enable TCP keepalives (libpq expects 1 for on, 0 for off)
            "keepalives": 1,
            "keepalives_idle": 60,  # Seconds of inactivity before sending a keepalive probe
            "keepalives_interval": 10,  # Seconds between keepalive probes if no ACK is received
            # Number of unacknowledged probes before considering connection dead
            "keepalives_count": 5,
            # Set a reasonable connection timeout to avoid hanging
            "connect_timeout": 10,
        },
        # Connection checking
        check=psycopg_pool.AsyncConnectionPool.check_connection,
        timeout=5.0,
        max_lifetime=3600.0,  # 1 hour
        max_idle=300.0,  # 5 minutes
        reconnect_timeout=5.0,
        open=False,
    )

    try:
        await connection_pool_new.open()
        connection_pool_async = connection_pool_new
        logger.info("Connection pool successfully initialized")
        return connection_pool_new
    except Exception as e:
        logger.error(f"Failed to initialize connection pool: {str(e)}")
        raise


async def get_connection_pool_async():
    global connection_pool_async
    if connection_pool_async is None:
        # Reduced pool size to more reasonable defaults
        await init_connection_pool_async(5, 20)
    return connection_pool_async


async def close_connection_pool_async():
    global connection_pool_async
    if connection_pool_async:
        logger.info("Closing connection pool")
        await connection_pool_async.close()
        connection_pool_async = None
