
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot, types
from aiogram.types import Message
from different_format.keyboards.inline import hr, placenowkb, placewillkb, yesnotransfer,changetr, placenowkbedi, placewillkbedi
from different_format.utils.states import FormTransf
from keyboards.reply import cancel, main
from utils.states import Employee
 
router = Router()

@router.callback_query(F.data == 'officenow')
async def fill_officenow(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите  <b>формат работы на переход</b>", reply_markup=placewillkb, parse_mode="HTML")
    await state.update_data(placenow = "Офис")
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'hybridnow')
async def fill_hybridnow(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите  <b>формат работы на переход</b>", reply_markup=placewillkb, parse_mode="HTML")
    await state.update_data(placenow = "Гибрид")
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'remotelynow')
async def fill_remotelynow(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите  <b>формат работы на переход</b>", reply_markup=placewillkb, parse_mode="HTML")
    await state.update_data(placenow = "Удаленно")
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'officewill')
async def fill_officewill(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Введите <b>часы работы</b>", parse_mode="HTML", reply_markup=cancel)
    await state.update_data(placewill = "Офис")
    await state.set_state(FormTransf.timework)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'hybridwill')
async def fill_hybridwill(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Введите <b>часы работы</b>", parse_mode="HTML", reply_markup=cancel)
    await state.update_data(placewill = "Гибрид")
    await state.set_state(FormTransf.timework)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'remotelywill')
async def fill_remotelywill(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Введите <b>часы работы</b>", parse_mode="HTML", reply_markup=cancel)
    await state.update_data(placewill = "Удаленно")
    await state.set_state(FormTransf.timework)
    await call.message.edit_reply_markup()


@router.callback_query(F.data == 'yestr')
async def yestr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Отправить заявку в HR?", reply_markup=hr)
    await call.message.edit_reply_markup()


@router.callback_query(F.data == 'notr')
async def notr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите пункт для изменения:", reply_markup=changetr)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'yeshr')
async def yeshr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Заявка успешно отправлена!")
    await bot.send_message(call.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=main)
    await call.message.edit_reply_markup()
    await state.clear()

@router.callback_query(F.data == 'nohr')
async def nohr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Ну ладно...", reply_markup=main)
    await call.message.edit_reply_markup()
    await state.clear()



@router.callback_query(F.data == 'placenowedi')
async def placenowedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Формат на данный момент", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Выберите  <b>формат на данный момент</b>", parse_mode='HTML', reply_markup=placenowkbedi)




@router.callback_query(F.data == 'officenowedi')
async def fill_officenowedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placenow = "Офис")
    data = await state.get_data()
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b>\n<b>Сотрудник:</b> {name}, {division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'hybridnowedi')
async def fill_hybridnowedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placenow = "Гибрид")
    data = await state.get_data()
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b>\n<b>Сотрудник:</b> {name}, {division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'remotelynowedi')
async def fill_remotelynowedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placenow = "Удаленно")
    data = await state.get_data()
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b>\n<b>Сотрудник:</b> {name}, {division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()




@router.callback_query(F.data == 'placewilledi')
async def placewilledit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Формат на переход", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Выберите  <b>формат на переход</b>", parse_mode='HTML', reply_markup=placewillkbedi)




@router.callback_query(F.data == 'officewilledi')
async def fill_officewilledit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placewill = "Офис")
    data = await state.get_data()
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b>\n<b>Сотрудник:</b> {name}, {division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'hybridwilledi')
async def fill_hybridwilledit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placewill = "Гибрид")
    data = await state.get_data()
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b>\n <b>Сотрудник:</b> {name}, {division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'remotelywilledi')
async def fill_remotelywilledit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placewill = "Удаленно")
    data = await state.get_data()
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b>\n<b>Сотрудник:</b> {name}, {division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()




@router.callback_query(F.data == 'timeworkedi')
async def timeworkedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Часы работы", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>часы работы</b>", parse_mode='HTML')
    await state.set_state(FormTransf.timework2)




@router.callback_query(F.data == 'cityedi')
async def cityedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Город", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>город</b>", parse_mode='HTML')
    await state.set_state(FormTransf.city2)



@router.callback_query(F.data == 'reasonedi')
async def reasonedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Причина перевода", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>причину перевода</b>", parse_mode='HTML')
    await state.set_state(FormTransf.reason2)


