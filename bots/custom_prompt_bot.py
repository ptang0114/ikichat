# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datetime import datetime

from recognizers_number import recognize_number, Culture
from recognizers_date_time import recognize_datetime

from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    TurnContext,
    UserState,
    MessageFactory,
)

from data_models import ConversationFlow, Question, UserProfile
from data_models.sentiment import senti,ner


class ValidationResult:
    def __init__(
        self, is_valid: bool = False, value: object = None, message: str = None
    ):
        self.is_valid = is_valid
        self.value = value
        self.message = message


class CustomPromptBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        if conversation_state is None:
            raise TypeError(
                "[CustomPromptBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            raise TypeError(
                "[CustomPromptBot]: Missing parameter. user_state is required but None was given"
            )

        self.conversation_state = conversation_state
        self.user_state = user_state

        self.flow_accessor = self.conversation_state.create_property("ConversationFlow")
        self.profile_accessor = self.user_state.create_property("UserProfile")

    async def on_message_activity(self, turn_context: TurnContext):
        # Get the state properties from the turn context.
        profile = await self.profile_accessor.get(turn_context, UserProfile)
        flow = await self.flow_accessor.get(turn_context, ConversationFlow)

        await self._fill_out_user_profile(flow, profile, turn_context)

        # Save changes to UserState and ConversationState
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def _fill_out_user_profile(
        self, flow: ConversationFlow, profile: UserProfile, turn_context: TurnContext
    ):
        user_input = turn_context.activity.text.strip()

        # ask for name
        if flow.last_question_asked == Question.NONE:
            await turn_context.send_activity(
                MessageFactory.text("Hi, 本来想问你好吗？但是还是算了吧。")
            )
            await turn_context.send_activity(f"要不我来直接学习你吧😉")
            await turn_context.send_activity(f"我该怎么称呼你呀？")
            flow.last_question_asked = Question.NAME

        # validate name then ask for age
        elif flow.last_question_asked == Question.NAME:
            validate_result = self._validate_name(user_input)
            if not validate_result.is_valid:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
            else:
                profile.name = validate_result.value
                await turn_context.send_activity(
                    MessageFactory.text(f"很高兴认识你， {profile.name}。")
                )
                await turn_context.send_activity(
                    MessageFactory.text(f"你可以叫我iki，或者任何你想叫的名字~")
                )
                await turn_context.send_activity(
                    MessageFactory.text("你今年几岁了?")
                )
                flow.last_question_asked = Question.AGE

        # validate age then ask for date
        elif flow.last_question_asked == Question.AGE:
            validate_result = self._validate_age(user_input)
            if not validate_result.is_valid:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
            elif validate_result.value:
                profile.age = validate_result.value
                if profile.age < 30:
                    await turn_context.send_activity(
                        MessageFactory.text(f"{profile.age}岁的年纪，你的人生才刚刚开始呢。")
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"{profile.name}今天过的怎么样？能跟我聊聊吗？是开心的一天吗？")
                    )
                    flow.last_question_asked = Question.MOOD
                else:
                    await turn_context.send_activity(
                        MessageFactory.text(f"{profile.age}岁的年纪，你一定有很多故事可以和我分享吧。")
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"{profile.name}今天过的怎么样？能跟我聊聊吗？是开心的一天吗？")
                    )
                    flow.last_question_asked = Question.MOOD
            else:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
                await turn_context.send_activity(
                        MessageFactory.text(f"{profile.name}今天过的怎么样？能跟我聊聊吗？是开心的一天吗？")
                    )
                flow.last_question_asked = Question.MOOD



        # validate date and wrap it up
        elif flow.last_question_asked == Question.MOOD:
            validate_result = self._validate_mood(user_input)

            if not validate_result.is_valid:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
                await turn_context.send_activity(
                        MessageFactory.text(f"不如我们换个话题吧。")
                    )
                await turn_context.send_activity(
                        MessageFactory.text(f"{profile.name}喜欢收礼物吗？有没有收到过来自家人印象特别深刻的礼物？") 
                    )

                flow.last_question_asked = Question.RELATIVE

            elif validate_result.value:
                profile.mood = validate_result.value
                if profile.mood == 'positive':
                    await turn_context.send_activity(
                        MessageFactory.text(f"哇！听上去真好。很高兴能听到你这么说😊。")
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"一般有些什么事会让你觉得开心呢？")
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"对我来说，收到礼物最让我开心了！")
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"你有没有收到过来自家人印象特别深的礼物？")
                    )
                    flow.last_question_asked = Question.RELATIVE

                elif profile.mood == 'negative':
                    await turn_context.send_activity(
                        MessageFactory.text(f"真遗憾听到你这么说😔。")
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"不过有我在，我会一直陪着你的😌。") 
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"不如让我们说说开心的事吧！") 
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"对我来说，收到礼物最让我开心了！")
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"{profile.name}喜欢收礼物吗？有没有收到过来自家人印象特别深的礼物？") 
                    )
                    flow.last_question_asked = Question.RELATIVE
                    
                elif profile.mood == 'neutral':
                    await turn_context.send_activity(
                        MessageFactory.text(
                            f"我明白，有时候确实也不知道怎么描述自己的心情。不如我们换个话题吧！"
                        )
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(f"{profile.name}喜欢收礼物吗？有没有收到过来自家人印象特别深刻的礼物？") 
                    )

                    flow.last_question_asked = Question.RELATIVE
        
        elif flow.last_question_asked == Question.RELATIVE:
            validate_result = self._validate_relative(user_input)
            if not validate_result.is_valid:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
            else:
                profile.relative = validate_result.value
                await turn_context.send_activity(
                    MessageFactory.text(f"哇，这一定是你很珍惜的礼物吧！")
                )
                await turn_context.send_activity(
                    MessageFactory.text(f"{profile.relative}是你最喜欢的家人吗？")
                )
                
                flow.last_question_asked = Question.NONE

    def _validate_name(self, user_input: str) -> ValidationResult:
        if not user_input:
            return ValidationResult(
                is_valid=False,
                message="请至少输入一个字符。",
            )

        return ValidationResult(is_valid=True, value=user_input)

    def _validate_age(self, user_input: str) -> ValidationResult:
        # Attempt to convert the Recognizer result to an integer. This works for "a dozen", "twelve", "12", and so on.
        # The recognizer returns a list of potential recognition results, if any.
        results = recognize_number(user_input, Culture.Chinese)
        for result in results:
            if "value" in result.resolution:
                age = int(result.resolution["value"])
                if 1 <= age <= 100:
                    return ValidationResult(is_valid=True, value=age)
                elif age < 1 or age > 100:
                    return ValidationResult(
                        is_valid=False, message="要输入真实年龄(1-100之间)才能让我更好的了解你哦。"
                    )
        return ValidationResult(
            is_valid=True, message="年龄只是一个数字，你不想说也可以😌"
        )

    def _validate_mood(self, user_input: str) -> ValidationResult:
        result = senti(user_input)
        print (str(result))
        if "sentiment" in result:
            user_mood = result['sentiment']
            if user_mood == 'positive' or user_mood == 'negative' or user_mood == 'neutral':
                return ValidationResult(is_valid=True, value=user_mood)
            else:
                return ValidationResult(
                        is_valid=False, message="这对我暂时还有点难😣"
                    )

    def _validate_relative(self, user_input: str) -> ValidationResult:
        result = ner(user_input)
        if "person_type" in result:
            user_relative = result['person_type']
            return ValidationResult(is_valid=True, value=user_relative)
        else:
            return ValidationResult(
                        is_valid=False, message="那么你最喜欢的一位亲人是谁呢？"
                    )



    # def _validate_date(self, user_input: str) -> ValidationResult:
    #     try:
    #         # Try to recognize the input as a date-time. This works for responses such as "11/14/2018", "9pm",
    #         # "tomorrow", "Sunday at 5pm", and so on. The recognizer returns a list of potential recognition results,
    #         # if any.
    #         results = recognize_datetime(user_input, Culture.English)
    #         for result in results:
    #             for resolution in result.resolution["values"]:
    #                 if "value" in resolution:
    #                     now = datetime.now()

    #                     value = resolution["value"]
    #                     if resolution["type"] == "date":
    #                         candidate = datetime.strptime(value, "%Y-%m-%d")
    #                     elif resolution["type"] == "time":
    #                         candidate = datetime.strptime(value, "%H:%M:%S")
    #                         candidate = candidate.replace(
    #                             year=now.year, month=now.month, day=now.day
    #                         )
    #                     else:
    #                         candidate = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    #                     # user response must be more than an hour out
    #                     diff = candidate - now
    #                     if diff.total_seconds() >= 3600:
    #                         return ValidationResult(
    #                             is_valid=True,
    #                             value=candidate.strftime("%m/%d/%y"),
    #                         )

    #         return ValidationResult(
    #             is_valid=False,
    #             message="I'm sorry, please enter a date at least an hour out.",
    #         )
    #     except ValueError:
    #         return ValidationResult(
    #             is_valid=False,
    #             message="I'm sorry, I could not interpret that as an appropriate "
    #             "date. Please enter a date at least an hour out.",
    #         )
