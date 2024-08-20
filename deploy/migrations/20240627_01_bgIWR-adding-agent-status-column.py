"""
Adding agent status column
"""

from yoyo import step

__depends__ = {"20240605_01_vjN7f-initial-schema"}
__transactional__ = False

steps = [
    step(
        "ALTER TABLE `agent` ADD COLUMN `status` varchar(20) NOT NULL",
        "ALTER TABLE `agent` DROP COLUMN `status`",
    ),
]
