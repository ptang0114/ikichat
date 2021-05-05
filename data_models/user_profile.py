# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class UserProfile:
    def __init__(self, name: str = None, age: int = 0, mood: str = None, relative: str = None):
        self.name = name
        self.age = age
        self.mood = mood
        self.relative = relative
