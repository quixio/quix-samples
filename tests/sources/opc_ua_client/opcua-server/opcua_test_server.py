#!/usr/bin/env python3
"""
OPC UA Test Server for integration testing.

Creates a simple OPC UA server with simulated machine data:
- Machine1 with Temperature, Pressure, and Status parameters
- Updates values every 2 seconds to simulate real sensor data
"""
import asyncio
import logging
from asyncua import Server, ua

async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Create and initialize server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # Set server name
    server.set_server_name("Quix Test OPC UA Server")

    # Register custom namespace (matches OPC_NAMESPACE env var)
    uri = "http://quix.test.opcua.io"
    idx = await server.register_namespace(uri)

    logger.info(f"Registered namespace: {uri} with index {idx}")

    # Create a machine object
    machine1 = await server.nodes.objects.add_object(idx, "Machine1")

    # Create test parameters (variables) under the machine
    temp_var = await machine1.add_variable(idx, "Temperature", 20.0)
    pressure_var = await machine1.add_variable(idx, "Pressure", 100.0)
    status_var = await machine1.add_variable(idx, "Status", True)

    # Make variables writable (so they can be updated)
    await temp_var.set_writable()
    await pressure_var.set_writable()
    await status_var.set_writable()

    logger.info("Created Machine1 with Temperature, Pressure, and Status nodes")

    # Start server and simulate changing values
    async with server:
        logger.info("OPC UA Test Server started on opc.tcp://0.0.0.0:4840/freeopcua/server/")

        counter = 0
        while True:
            await asyncio.sleep(2)
            counter += 1

            # Update values to simulate real sensor data
            new_temp = 20.0 + (counter % 10)
            new_pressure = 100.0 + (counter * 2)
            new_status = counter % 2 == 0

            await temp_var.write_value(new_temp)
            await pressure_var.write_value(new_pressure)
            await status_var.write_value(new_status)

            logger.info(f"Updated values: Temp={new_temp}, Pressure={new_pressure}, Status={new_status}")

if __name__ == "__main__":
    asyncio.run(main())
