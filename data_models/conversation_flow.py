# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from enum import Enum


class Question(Enum):
    NAME = 1
    AGE = 2
    MOOD = 3
    RELATIVE = 4
    NONE = 5


class ConversationFlow:
    def __init__(
        self, last_question_asked: Question = Question.NONE,
    ):
        self.last_question_asked = last_question_asked
