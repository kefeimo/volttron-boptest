# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2022 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===
# }}}

"""Configuration for the pytest test suite (for agents)."""

import sys
import os
from pathlib import Path

# # to make sure src/ is included in the path for pytest
# if "src" not in sys.path:
#     sys.path.insert(0, "src")
#
# if __name__ == "__main__":
#     print("something")
#     print(sys.path)

p = Path(__file__)
if p.parent.parent.resolve().as_posix() not in sys.path:
    src_path = os.path.join(p.parent.parent.resolve().as_posix(), "src")
    sys.path.insert(0, src_path)

# if __name__ == "__main__":
#     print(sys.path)
#     print(p.parent.parent.parent)
#     print(p.parent.parent)

