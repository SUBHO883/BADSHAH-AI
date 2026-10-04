import asyncio
from datetime import datetime


async def _discover():

    from bleak import BleakScanner

    devices = await BleakScanner.discover(
        timeout=8.0
    )

    results = []

    for device in devices:

        results.append(
            {
                "name": device.name or "Unknown",
                "address": device.address,
                "details": str(
                    getattr(
                        device,
                        "details",
                        "",
                    )
                ),
                "metadata": str(
                    getattr(
                        device,
                        "metadata",
                        {},
                    )
                ),
            }
        )

    return results


def discover_bluetooth():

    try:

        devices = asyncio.run(
            _discover()
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "count": len(devices),
            "devices": devices,
        }

    except Exception as exc:

        return {
            "timestamp": datetime.now().isoformat(),
            "count": 0,
            "devices": [],
            "error": str(exc),
        }