"""
Set project alert config default
"""

from yoyo import step

__depends__ = {"20240701_01_zRe7i-add-project-alert-config-field"}

steps = [
    step("UPDATE `project` SET `alert_actions` = JSON_ARRAY()"),
]
