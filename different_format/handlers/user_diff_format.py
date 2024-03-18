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
    await state.update_data(reason = message.text)
    await diff_format(message, state)       

@router.message(FormTransf.timework2)
async def timeworkedit2(message: Message, state: FSMContext):
    await state.update_data(timework = message.text)
    await diff_format(message, state)       


@router.message(FormTransf.city2)
async def cityedit2(message: Message, state: FSMContext):
    await state.update_data(city = message.text)
    await diff_format(message, state)       


@router.message(FormTransf.reason2)
async def reasonedit2(message: Message, state: FSMContext):
    await state.update_data(reason = message.text)
    await diff_format(message, state)

async def diff_format(message: Message, state:FSMContext):
    data = await state.get_data()
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b>\n<b>Сотрудник:</b> {name}, {division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
    await message.answer("Запрос введен верно?", reply_markup=inline.yesnotransfer)