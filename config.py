#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "330aa505-71bf-4e8e-8eb9-8954f3ec7cdd")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "AtLeastSixteenCharacters_0")
