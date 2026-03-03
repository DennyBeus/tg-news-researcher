from aiogram.fsm.state import State, StatesGroup


class ChannelStates(StatesGroup):
    waiting_for_channel = State()


class InterestStates(StatesGroup):
    waiting_for_interest = State()


class StyleStates(StatesGroup):
    waiting_for_style = State()


class DigestTimeStates(StatesGroup):
    waiting_for_digest_time = State()


class GeneratePostStates(StatesGroup):
    waiting_for_post_ids = State()
