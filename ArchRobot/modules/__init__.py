#
# Copyright (c) 2024–2026 ArchBots
#
# This file is part of the ArchRobot project.
# Repository: https://github.com/ArchBots/ArchRobot
#
# Licensed under the MIT License.
# You may obtain a copy of the License in the LICENSE file
# distributed with this source code.
#
# This software is provided "as is", without warranty of any kind,
#

import os

ALL_MODULES = []

for module in os.listdir(os.path.dirname(__file__)):
    if module.endswith(".py") and not module.startswith("_"):
        ALL_MODULES.append(module[:-3])