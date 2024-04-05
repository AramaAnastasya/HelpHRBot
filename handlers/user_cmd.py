import os
from aiogram import F, types, Router, Bot,Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, as_marked_section, Bold,Spoiler #Italic, as_numbered_list и тд 
from aiogram.types import Message
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from avtorization.utils.states import FSMAdmin
from filters.chat_types import ChatTypeFilter
from keyboards import reply

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

from config import DATABASE_URI

engine = create_engine(DATABASE_URI)

# Создайте сессию для работы с базой данных
Session = sessionmaker(bind=engine)
metadata = MetaData()
table_Employee = Table('employee', metadata, autoload_with=engine)
table_application = Table('Applications', metadata, autoload_with=engine)
table_question = Table('Question', metadata, autoload_with=engine)


@user_private_router.message(CommandStart())
async def start_cmd(message:Message, state: FSMContext):
    # Получить информацию о члене чата (пользователе, отправившем сообщение)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    # Вывести имя пользователя
    await bot.send_message(message.chat.id, 
            f"Добрый день, <b>{chat_member.user.first_name}</b>! Я виртуальный HR-помощник.\nДля авторизации отправьте свой контактный номер телефона.",
            reply_markup=reply.start_kb        
            )
    await state.set_state(FSMAdmin.phone)

@user_private_router.message((F.text.lower() == "подать заявку"))
async def menu_cmd(message: types.Message):
    await message.answer(
        "Выберите вид заявки",
        reply_markup=reply.request
    )

@user_private_router.message(F.text.lower() == "отменить заявку ❌")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=reply.main
    )
    await message.answer(
        text="Выберите тип обращения"
    )



@user_private_router.message(F.text.lower() == "отправленные заявки")
async def transfer_cmd(message: types.Message):

	print(message.from_user.id)
	session = Session()
	#поиск Id пользователя
	userData = session.query(table_Employee).filter(table_Employee.c.id_telegram == str(message.from_user.id)).first()
	# userData 'то массив с данными пользователя surname = userData[2]


	userId = userData[1]
	print(userId)
	if userId == None:
		await message.answer('Пользователь не найден', reply_markup=reply.main)
		return
	
	#Массив с заявками
	aplikations = session.query(table_application).filter(table_application.c.ID_Initiator == userId, table_application.c.Date_actual_deadline == None).order_by(table_application.c.id).all()	
	print(aplikations)
	questions = session.query(table_question).filter(table_question.c.ID_Initiator == userId, table_question.c.Date_actual_deadline == None).order_by(table_question.c.id).all()	
	print(questions)
	firstName = userData[3][:1]
	MidName = userData[4][:1]
	# цикл берет отдельную заявку
	for item in aplikations:
		# item - одна заявка, item это массив с данными
		
		print(item)

		
		tempText = ''
		if item[3] == 4:
			tempText+=f'<b>Заявка по общей форме</b>\n'
			tempText+=f'<b>Номер заявки:</b> {item[0]}\n'
			tempText+=f'<b>Инициатор:</b> {userData[2]} {MidName}. {firstName}. \n'
			tempText+=f'<b>Суть:</b> {item[6]}\n'
			tempText+=f'<b>Дата:</b> {item[18]}'

		if item[3] == 1:
			tempText+=f'<b>Заявка на перевод</b>\n'
			tempText+=f'<b>Номер заявки:</b> {item[0]}\n'
			tempText+=f'<b>Инициатор:</b> {userData[2]} {MidName}. {firstName}. \n'
			tempText+=f'<b>Сотрудник:</b> {userData[2]} {userData[3]} {userData[4]}, {userData[5]}, {userData[6]}\n'
			tempText+=f'<b>Дата конца испытательного срока:</b> {item[4]}\n'
			tempText+=f'<b>Дата:</b> {item[18]}'

		if item[3] == 2:
			tempText+=f'<b>Заявка на перевод на другой формат работы</b>\n'
			tempText+=f'<b>Номер заявки:</b> {item[0]}\n'
			tempText+=f'<b>Инициатор:</b> {userData[2]} {MidName}. {firstName}. \n'
			tempText+=f'<b>Сотрудник:</b> {userData[2]} {userData[3]} {userData[4]}, {userData[5]}, {userData[6]}\n'
			tempText+=f'<b>Формат на данный момент:</b> {item[14]}\n'
			tempText+=f'<b>Формат на переход:</b> {item[15]}\n'
			tempText+=f'<b>Дата:</b> {item[18]}'

		if item[3] == 3:
			tempText+=f'<b>Заявка на согласование заработной платы</b>\n'
			tempText+=f'<b>Номер заявки:</b> {item[0]}\n'
			tempText+=f'<b>Инициатор:</b> {userData[2]} {MidName}. {firstName}. \n'
			tempText+=f'<b>Сотрудник:</b> {userData[2]} {userData[3]} {userData[4]}, {userData[5]}, {userData[6]}\n'
			tempText+=f'<b>Действующая сумма:</b> {item[12]}\n'
			tempText+=f'<b>Предлагаемая сумма:</b> {item[11]}\n'
			tempText+=f'<b>Дата:</b> {item[18]}'

		await message.answer(tempText, reply_markup=reply.main)


	for quwst in questions:
		tempText = ''
		tempText+=f'<b>Общий вопрос</b>\n'
		tempText+=f'<b>Номер вопроса:</b> {quwst[0]}\n'
		tempText+=f'<b>Инициатор:</b> {userData[2]} {MidName}. {firstName}. \n'
		tempText+=f'<b>Суть:</b> {quwst[3]}\n'
		tempText+=f'<b>Дата:</b> {quwst[5]}'


		await message.answer(tempText, reply_markup=reply.main)