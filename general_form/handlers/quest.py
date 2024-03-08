from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.reply import cancel
from general_form.utils.states import Form
from general_form.keyboards import inline
from keyboards import reply

router = Router()

@router.message(F.text == "Общая форма")
async def fill_request(message: Message, state: FSMContext):
    if message.text == "Отменить заявку":
        await message.answer("Вы отменили заявку", reply_markup=reply.main)
        await state.clear()
    else:
        await state.set_state(Form.essence)
        await message.answer(
            "Введите <b>суть обращение</b>",
            reply_markup=cancel,
            parse_mode="HTML",

        )

@router.message(Form.essence)
async def fill_essence(message: Message, state: FSMContext):
    if message.text == "Отменить заявку":
        await message.answer("Вы отменили заявку", reply_markup=reply.main)
        await state.clear()
    else:
        await state.update_data(essence=message.text)
        await state.set_state(Form.expect)
        await message.answer("Введите <b>ожидаемый результат</b>", reply_markup=cancel, parse_mode="HTML")


@router.message(Form.expect)
async def fill_expect(message: Message, state: FSMContext):
    if message.text == "Отменить заявку":
        await message.answer("Вы отменили заявку", reply_markup=reply.main)
        await state.clear()
    else:
        await state.update_data(expect=message.text)
        data = await state.get_data()
        formatter_text = (f"Ваша заявка:\n<b>Суть обращения:</b> {data['essence']}\n<b>Ожидаемый результат:</b> {data['expect']}")
        await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=inline.yesno)


@router.message(F.text == "Задать вопрос")
async def fill_request(message: Message, state: FSMContext):
    if message.text == "Отменить заявку":
        await message.answer("Вы отменили заявку", reply_markup=reply.main)
        await state.clear()
    else:
        await state.set_state(Form.quiz)
        await message.answer(
            "Введите <b>суть вопроса</b>",
            reply_markup=cancel,
            parse_mode="HTML",

        )

@router.message(Form.quiz)
async def fill_essence(message: Message, state: FSMContext):
    if message.text == "Отменить заявку":
        await message.answer("Вы отменили заявку", reply_markup=reply.main)
        await state.clear()
    else:
        await state.update_data(quiz=message.text)
        await state.set_state(Form.resquiz)
        await message.answer("Введите <b>ожидаемый результат</b>", reply_markup=cancel, parse_mode="HTML")


@router.message(Form.resquiz)
async def fill_expect(message: Message, state: FSMContext):
    if message.text == "Отменить заявку":
        await message.answer("Вы отменили заявку", reply_markup=reply.main)
        await state.clear()
    else:
        await state.update_data(resquiz=message.text)
        data = await state.get_data()
        formatter_text = (f"Ваш вопрос:\n<b>Суть вопроса:</b> {data['quiz']}\n<b>Ожидаемый результат:</b> {data['resquiz']}")
        await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=inline.yesnoquiz)



