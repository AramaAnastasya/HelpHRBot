
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot, types
from aiogram.types import Message
from general_form.keyboards.inline import yesno, hr, change, changequiz, yesnoquiz
from general_form.utils.states import Form
from keyboards.reply import cancel, main

router = Router()

@router.callback_query(F.data == 'yes')
async def yes(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    if call.message.text == 'Отменить заявку':
        await bot.send_message(call.from_user.id,"Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, "Отправить заявку в HR?", reply_markup=hr)
        await call.message.edit_reply_markup()
        await state.clear()

@router.callback_query(F.data == 'no')
async def no(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    if call.message.text == 'Отменить заявку':
        await bot.send_message(call.from_user.id, "Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, "Выберите пункт для изменения:", reply_markup=change)
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

@router.callback_query(F.data == 'essenseedi')
async def essenseedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    if call.message.text == 'Отменить заявку':
        await bot.send_message(call.from_user.id,"Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, f"Изменение пункта суть обращения")
        await call.message.edit_reply_markup()
        await bot.send_message(call.from_user.id, "Введите <b>суть обращения</b>", parse_mode='HTML', reply_markup=cancel)
        await state.set_state(Form.essence2)

@router.message(Form.essence2)
async def essenseedi2(message: Message, state: FSMContext):
    if message.text == 'Отменить заявку':
        await message.answer("Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await state.update_data(essence = message.text)
        data = await state.get_data()
        await message.answer(f"Ваша заявка:\n<b>Суть обращения:</b> {data['essence']}\n<b>Ожидаемый результат:</b> {data['expect']}", parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=yesno)


@router.callback_query(F.data == 'expectedi')
async def expectedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    if call.message.text == 'Отменить заявку':
        await bot.send_message(call.from_user.id,"Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, f"Изменение пункта ожидаемый результат")
        await call.message.edit_reply_markup()
        await bot.send_message(call.from_user.id, "Введите <b>ожидаемый результат</b>", parse_mode='HTML', reply_markup=cancel)
        await state.set_state(Form.expect2)

@router.message(Form.expect2)
async def expectedi2(message: Message, state: FSMContext):
    if message.text == 'Отменить заявку':
        await message.answer("Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await state.update_data(expect = message.text)
        data = await state.get_data()
        await message.answer(f"Ваша заявка:\n<b>Суть обращения:</b> {data['essence']}\n<b>Ожидаемый результат:</b> {data['expect']}", parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=yesno)













@router.callback_query(F.data == 'noquiz')
async def noquiz(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    if call.message.text == 'Отменить заявку':
        await bot.send_message(call.from_user.id, "Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, "Выберите пункт для изменения:", reply_markup=changequiz)
        await call.message.edit_reply_markup()


@router.callback_query(F.data == 'quizedit')
async def quizedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    if call.message.text == 'Отменить заявку':
        await bot.send_message(call.from_user.id,"Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, f"Изменение пункта суть вопроса")
        await call.message.edit_reply_markup()
        await bot.send_message(call.from_user.id, "Введите <b>суть вопроса</b>", parse_mode='HTML', reply_markup=cancel)
        await state.set_state(Form.quiz2)

@router.message(Form.quiz2)
async def quizedit2(message: Message, state: FSMContext):
    if message.text == 'Отменить заявку':
        await message.answer("Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await state.update_data(quiz = message.text)
        data = await state.get_data()
        await message.answer(f"Ваш вопрос:\n<b>Суть вопроса:</b> {data['quiz']}\n<b>Ожидаемый результат:</b> {data['resquiz']}", parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=yesnoquiz)



@router.callback_query(F.data == 'resquizedit')
async def resquizedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    if call.message.text == 'Отменить заявку':
        await bot.send_message(call.from_user.id,"Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, f"Изменение пункта ожидаемый результат")
        await call.message.edit_reply_markup()
        await bot.send_message(call.from_user.id, "Введите <b>ожидаемый результат</b>", parse_mode='HTML', reply_markup=cancel)
        await state.set_state(Form.resquiz2)

@router.message(Form.resquiz2)
async def quizedit2(message: Message, state: FSMContext):
    if message.text == 'Отменить заявку':
        await message.answer("Вы отменили заявку", reply_markup=main)
        await state.clear()
    else:
        await state.update_data(resquiz = message.text)
        data = await state.get_data()
        await message.answer(f"Ваш вопрос:\n<b>Суть вопроса:</b> {data['quiz']}\n<b>Ожидаемый результат:</b> {data['resquiz']}", parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=yesnoquiz)