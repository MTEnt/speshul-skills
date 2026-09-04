"""Payment capture with a subtle problem for review."""

import logging

log = logging.getLogger(__name__)


def capture(gateway, order_id: str, amount_cents: int) -> bool:
    try:
        gateway.capture(order_id, amount_cents)
        return True
    except Exception as exc:  # noqa: BLE001
        log.info("capture failed for %s: %s", order_id, exc)
        return True
