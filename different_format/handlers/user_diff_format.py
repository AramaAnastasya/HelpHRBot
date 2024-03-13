from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.reply import cancel
from different_format.utils.states import FormTransf
from different_format.keyboards import inline
from keyboards import reply

router = Router()

@router.message(FormTransf.timework)
async def fill_timework(message: Message, state: FSMContext):
    await state.update_data(timework = message.text)
    await state.set_state(FormTransf.city)
    await message.answer("Введите <b>город</b>", reply_markup=cancel, parse_mode="HTML")


@router.message(FormTransf.city)
async def fill_city(message: Message, state: FSMContext):
    await state.update_data(city = message.text)
    await state.set_state(FormTransf.reason)
    await message.answer("Введите <b>причину перевода</b>", reply_markup=cancel, parse_mode="HTML")



@router.message(FormTransf.reason)
async def fill_transferend(message: Message, state: FSMContext):
    await state.update_data(reason=message.text)
    data = await state.get_data()
    formatter_text = (f"Ваша заявка:\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
    await message.answer("Запрос введен верно?", reply_markup=inline.yesnotransfer)


@router.message(FormTransf.timework2)
async def timeworkedit2(message: Message, state: FSMContext):
    await state.update_data(timework = message.text)
    data = await state.get_data()
    formatter_text = (f"Ваша заявка:\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
    await message.answer("Запрос введен верно?", reply_markup=inline.yesnotransfer)


@router.message(FormTransf.city2)
async def cityedit2(message: Message, state: FSMContext):
    await state.update_data(city = message.text)
    data = await state.get_data()
    formatter_text = (f"Ваша заявка:\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
    await message.answer("Запрос введен верно?", reply_markup=inline.yesnotransfer)


@router.message(FormTransf.reason2)
async def reasonedit2(message: Message, state: FSMContext):
    await state.update_data(reason = message.text)
    data = await state.get_data()
    formatter_text = (f"Ваша заявка:\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
    await message.answer("Запрос введен верно?", reply_markup=inline.yesnotransfer)


