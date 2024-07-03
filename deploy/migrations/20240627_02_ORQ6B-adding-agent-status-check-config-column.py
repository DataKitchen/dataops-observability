"""
Adding agent status check config column
"""

from yoyo import step

__depends__ = {"20240627_01_bgIWR-adding-agent-status-column"}
__transactional__ = False

steps = [
    step(
        "ALTER TABLE `project` ADD COLUMN `agent_status_check_interval` INT NOT NULL",
        "ALTER TABLE `project` DROP COLUMN `agent_status_check_interval`",
    ),
]
