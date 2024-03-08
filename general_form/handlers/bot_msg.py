from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards import reply

router = Router()


@router.message(F.text == "Подать заявку")
async def request (message: Message):
    await message.answer ("Выберите тип заявки", reply_markup=reply.request)


# @router.message(F.text == "Задать вопрос")
# async def request (message: Message):
#     await message.answer ("Выберите тип заявки")


@router.message(F.text == "Отменить заявку")
async def cancel (message: Message, state: FSMContext):
    await message.answer ("Вы отменили заявку", reply_markup=reply.main, parse_mode="HTML")
    await state.clear()

