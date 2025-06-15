import logging
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
import const_configs
import sys
import os
import asyncio

# Add parent directory to path to import from parent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dbconfig
from api import (
    users_router,
    blocks_router,
    floors_router,
    rooms_router,
    friends_router,
    allotments_router,
    tenants_router,
    create_response
)
from api.response_models import (
    RootResponse,
    HealthCheckResponse,
    SystemTimeResponse
)

# Set event loop policy for Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    try:
        import uvloop
        uvloop.install()
    except:  # noqa: E722
        pass

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Hostel Counselling API",
    description="API for Hostel Counselling Backend with CRUD operations",
    version="1.0.0",
    default_response_class=ORJSONResponse,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


async def startup_event():
    """Initialize the connection pool on startup."""
    connection_pool_async = await dbconfig.init_connection_pool_async(10, 50)
    dbconfig.connection_pool_async = connection_pool_async
    logging.info("Database connection pool initialized")


app.add_event_handler("startup", startup_event)

# Include all CRUD API routers
app.include_router(users_router)
app.include_router(blocks_router)
app.include_router(floors_router)
app.include_router(rooms_router)
app.include_router(friends_router)
app.include_router(allotments_router)
app.include_router(tenants_router)


@app.get("/", response_model=RootResponse)
async def root():
    """Root endpoint."""
    return create_response(
        success=True,
        message="Hostel Counselling API is running",
        data={"version": "1.0.0", "status": "healthy"}
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        connection_pool = await dbconfig.get_connection_pool_async()
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                await cur.fetchone()
        
        return create_response(
            success=True,
            message="Service is healthy",
            data={"database": "connected", "status": "healthy"}
        )
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return create_response(
            success=False,
            error="Service is unhealthy",
            data={"database": "disconnected", "status": "unhealthy"}
        )


@app.post("/get_system_time", response_model=SystemTimeResponse)
async def get_system_time():
    """Get current system time."""
    try:
        system_time = const_configs.get_system_time()
        return create_response(data=system_time)
    except Exception as e:
        return create_response(error=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
