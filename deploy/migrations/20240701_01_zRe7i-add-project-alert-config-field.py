"""
Add project alert config field
"""

from yoyo import step

__depends__ = {"20240627_03_4o7tH-agent-status-check-default-values"}
__transactional__ = False

steps = [
    step(
        "ALTER TABLE `project` ADD COLUMN `alert_actions` JSON NOT NULL",
        "ALTER TABLE `project` DROP COLUMN `alert_actions`",
    )
]
