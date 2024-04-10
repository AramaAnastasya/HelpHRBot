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
from handlers.keyboards.inline import get_callback_btns, sorted_keybordFirstI, sorted_keybordSecondI, init_quest, init_quest_d, init_transf, init_transf_d, init_zp, init_zp_d, init_diff, init_diff_d, init_gen_d, init_gen

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
table_position = Table('Position', metadata, autoload_with=engine)
table_division = Table('Division', metadata, autoload_with=engine)


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
	await message.answer("Выберите категорию", reply_markup=sorted_keybordFirstI)

@user_private_router.callback_query(F.data == "sort_appI")
async def sort_applic(callback: types.CallbackQuery, state:FSMContext):
	msg_id = callback.message.message_id
	await bot.delete_message(callback.message.chat.id, msg_id)
    
	await bot.send_message(callback.from_user.id, "Выберите тип заявки для вывода отправленных заявок", reply_markup=sorted_keybordSecondI, parse_mode="HTML")

# Вывод  заявок общей формы
@user_private_router.callback_query(F.data == "sort_app_generalI")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
	msg_id = callback.message.message_id
	await bot.delete_message(callback.message.chat.id, msg_id)
	session = Session()
	#поиск Id пользователя
	userData = session.query(table_Employee).filter(table_Employee.c.id_telegram == str(callback.from_user.id)).first()

	userId = userData[1]
	if userId == None:
		await callback.answer('Пользователь не найден', reply_markup=reply.main)
		return

	#Массив с заявками
	result = session.query(table_application).filter(table_application.c.ID_Initiator == userId, table_application.c.Date_actual_deadline == None,  table_application.c.ID_Class_application == 4).order_by(table_application.c.Date_planned_deadline).all()
	if result:
		for row in result:
			text = ""
			if row.Date_planned_deadline == None:
				text = ""
			else:
				text = f"\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}"
			# Выведите сообщение с найденными данными и инлайн кнопкой
			result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
			await callback.message.answer(
				f"<b>Заявка по общей форме</b>\n"
				f"<b>Номер заявки:</b> {row.id}\n"
							f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
							f"<b>Суть обращения: </b>{ row.Essence_question}\n"
							f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
				reply_markup=init_gen)
	else:
		await callback.message.answer(
					f"Заявок на данный момент нет",
					reply_markup=reply.main
					)
	# Закройте сессию
	session.close()

# Вывод заявок перевод на другой формат рабоыт
@user_private_router.callback_query(F.data == "sort_app_diffI")
async def go_app_diff(callback: types.CallbackQuery, state:FSMContext):
	msg_id = callback.message.message_id
	await bot.delete_message(callback.message.chat.id, msg_id)
	session = Session()
	#поиск Id пользователя
	userData = session.query(table_Employee).filter(table_Employee.c.id_telegram == str(callback.from_user.id)).first()

	userId = userData[1]
	if userId == None:
		await callback.answer('Пользователь не найден', reply_markup=reply.main)
		return

	#Массив с заявками
	result = session.query(table_application).filter(table_application.c.ID_Initiator == userId, table_application.c.Date_actual_deadline == None, table_application.c.ID_Class_application == 2).order_by(table_application.c.Date_planned_deadline).all()
	if result:
		for row in result:
			text = ""
			if row.Date_planned_deadline == None:
				text = ""
			else:
				text = f"\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}"
			# Выведите сообщение с найденными данными и инлайн кнопкой
			result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
			if(row.ID_Employee == 1):
				result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
				result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
				await callback.message.answer(
					f"<b>Заявка на перевод на другой формат работы</b>\n"
					f"<b>Номер заявки:</b> {row.id}\n"
								f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
								f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
								f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
								f"<b>Формат на переход:</b> {row.Future_work_format}\n"
								f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
					reply_markup=init_diff)
			else:
				result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
				await callback.message.answer(
					f"<b>Заявка на перевод на другой формат работы</b>\n"
					f"<b>Номер заявки:</b> {row.id}\n"
								f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
								f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
								f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
								f"<b>Формат на переход:</b> {row.Future_work_format}\n"
								f"<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
					reply_markup=init_diff)   
	else:
		await callback.message.answer(
					f"Заявок на перевод на другой формат работы на данный момент нет",
					reply_markup=reply.main
					) 
	# Закройте сессию
	session.close()

# Вывод заявок на смену ЗП
@user_private_router.callback_query(F.data == "sort_app_zpI")
async def go_app_zp(callback: types.CallbackQuery, state:FSMContext):
	msg_id = callback.message.message_id
	await bot.delete_message(callback.message.chat.id, msg_id)
	session = Session()
	#поиск Id пользователя
	userData = session.query(table_Employee).filter(table_Employee.c.id_telegram == str(callback.from_user.id)).first()
	userId = userData[1]
	if userId == None:
		await callback.answer('Пользователь не найден', reply_markup=reply.main)
		return

	#Массив с заявками
	result = session.query(table_application).filter(table_application.c.ID_Initiator == userId, table_application.c.Date_actual_deadline == None, table_application.c.ID_Class_application == 3).order_by(table_application.c.Date_planned_deadline).all()
	if result:
		for row in result:
			text = ""
			if row.Date_planned_deadline == None:
				text = ""
			else:
				text = f"\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}"
			# Выведите сообщение с найденными данными и инлайн кнопкой
			result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
			if(row.ID_Employee == 1):
				result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
				result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
				await callback.message.answer(
					f"<b>Заявка на согласование заработной платы</b>\n"
					f"<b>Номер заявки:</b> {row.id}\n"
						f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
						f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
						f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
						f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
						f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
					reply_markup=init_zp)
			else:
				result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
				await callback.message.answer(
					f"<b>Заявка на согласование заработной платы</b>\n"
					f"<b>Номер заявки:</b> {row.id}\n"
						f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
						f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
						f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
						f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
						f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
					reply_markup=init_zp)
	else:
		await callback.message.answer(
					f"Актуальных заявок на согласование заработной платы на данный момент нет",
					reply_markup=reply.main
					)
	session.close()

# Вывод заявок на перевод
@user_private_router.callback_query(F.data == "sort_app_transfI")
async def go_app_transf(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
	msg_id = callback.message.message_id
	await bot.delete_message(callback.message.chat.id, msg_id)
	session = Session()
	#поиск Id пользователя
	userData = session.query(table_Employee).filter(table_Employee.c.id_telegram == str(callback.from_user.id)).first()
	userId = userData[1]

	if userId == None:
		await callback.answer('Пользователь не найден', reply_markup=reply.main)
		return

	result = session.query(table_application).filter(table_application.c.ID_Initiator == userId,table_application.c.Date_actual_deadline == None, table_application.c.ID_Class_application == 1).order_by(table_application.c.Date_planned_deadline).all()
	if result:
		for row in result:
			# Выведите сообщение с найденными данными и инлайн кнопкой
			text = ""
			if row.Date_planned_deadline == None:
				text = ""
			else:
				text = f"\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}"
			# Выведите сообщение с найденными данными и инлайн кнопкой
			result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
			if(row.ID_Employee == 1):
				result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
				result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
				await callback.message.answer(
					f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
					f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
					reply_markup=init_transf
					)
			else:
				result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
				await callback.message.answer(
					f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
					f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
					reply_markup=init_transf)
	else:
		await callback.message.answer(
					f"Заявок на перевод на данный момент нет",
					reply_markup=reply.main
					)
	# Закройте сессию
	session.close()

# Вывод вопросов
@user_private_router.callback_query(F.data == "sort_questI")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
	msg_id = callback.message.message_id
	await bot.delete_message(callback.message.chat.id, msg_id)
	session = Session()
	#поиск Id пользователя
	userData = session.query(table_Employee).filter(table_Employee.c.id_telegram == str(callback.from_user.id)).first()

	userId = userData[1]
	if userId == None:
		await callback.answer('Пользователь не найден', reply_markup=reply.main)
		return
	
	result_Quest = session.query(table_question).filter(table_question.c.ID_Initiator == userId, table_question.c.Date_actual_deadline == None).order_by(table_question.c.id).all()
	if result_Quest:
		for row in result_Quest:
			if row.Date_planned_deadline == None:
				await callback.message.answer(
				f"<b>Вопрос</b>\n"
				f"<b>Номер вопроса:</b> {row.id}\n"
							f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
				reply_markup=init_quest)
			else:
				await callback.message.answer(
					f"<b>Вопрос</b>\n"
					f"<b>Номер вопроса:</b> {row.id}\n"
								f"<b>Суть обращения: </b>{ row.Essence_question}\n"
								f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
								f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
					reply_markup=init_quest)
	else:
		await callback.message.answer(  
					f"Вопросов на данный момент нет",
					reply_markup=reply.main
					)
# Вывод всех заявок и вопросов
@user_private_router.callback_query(F.data == "sort_allI")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
	msg_id = callback.message.message_id
	await bot.delete_message(callback.message.chat.id, msg_id)
	session = Session()
	userData = session.query(table_Employee).filter(table_Employee.c.id_telegram == str(callback.from_user.id)).first()

	userId = userData[1]
	if userId == None:
		await callback.answer('Пользователь не найден', reply_markup=reply.main)
		return
	# Выберите данные из таблицы с использованием фильтрации
	result = session.query(table_application).filter(table_application.c.ID_Initiator == userId, table_application.c.Date_actual_deadline == None).order_by(table_application.c.Date_application).all()
	result_Quest = session.query(table_question).filter(table_question.c.ID_Initiator == userId, table_question.c.Date_actual_deadline == None, ).order_by(table_question.c.Date_application).all()
	if result and result_Quest:
		for row in result:
			text = ""
			if row.Date_planned_deadline == None:
				text = ""
			else:
				text = f"\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}"
			# Выведите сообщение с найденными данными и инлайн кнопкой
			result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
			if(row.ID_Class_application == 1):
				if(row.ID_Employee == 1):
					result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
					result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
					await callback.message.answer(
						f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
						f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
					reply_markup=init_transf)
				else:
					result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
					await callback.message.answer(
						f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
						f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
						reply_markup=init_transf)
			if(row.ID_Class_application == 2):
				if(row.ID_Employee == 1):
					result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
					result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
					await callback.message.answer(
						f"<b>Заявка на перевод на другой формат работы</b>\n"
						f"<b>Номер заявки:</b> {row.id}\n"
									f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
									f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
									f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
									f"<b>Формат на переход:</b> {row.Future_work_format}\n"
									f"<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
						reply_markup=init_diff)
				else:
					result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
					await callback.message.answer(
						f"<b>Заявка на перевод на другой формат работы</b>\n"
						f"<b>Номер заявки:</b> {row.id}\n"
									f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
									f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
									f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
									f"<b>Формат на переход:</b> {row.Future_work_format}\n"
									f"<b>Дата:</b> {row.Date_application}", 
						reply_markup=init_diff)
			if(row.ID_Class_application == 3):
				if(row.ID_Employee == 1):
					result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
					result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
					await callback.message.answer(
						f"<b>Заявка на согласование заработной платы</b>\n"
						f"<b>Номер заявки:</b> {row.id}\n"
							f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
							f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
							f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
							f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
							f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
						reply_markup=init_zp)
				else:
					result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
					await callback.message.answer(
						f"<b>Заявка на согласование заработной платы</b>\n"
						f"<b>Номер заявки:</b> {row.id}\n"
							f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
							f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
							f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
							f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
							f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
						reply_markup=init_zp)
			if(row.ID_Class_application == 4):
				await callback.message.answer(
					f"<b>Заявка по общей форме</b>\n"
					f"<b>Номер заявки:</b> {row.id}\n"
								f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
								f"<b>Суть обращения: </b>{ row.Essence_question}\n"
								f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
					reply_markup=init_gen)
					
		for row in result_Quest:
			text = ""
			if row.Date_planned_deadline == None:
				text = ""
			else:
				text = f"\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}"
			result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
			await callback.message.answer(
				f"<b>Вопрос</b>\n"
				f"<b>Номер вопроса:</b> {row.id}\n"
							f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
							f"<b>Суть обращения: </b>{ row.Essence_question}\n"
							f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
				reply_markup=init_quest)
	elif result and not result_Quest:
			for row in result:
				text = ""
				if row.Date_planned_deadline == None:
					text = ""
				else:
					text = f"\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}"
			# Выведите сообщение с найденными данными и инлайн кнопкой
				result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
				if(row.ID_Class_application == 1):
					if(row.ID_Employee == 1):
						result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
						result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
							f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}{text}\n", 
						reply_markup=init_transf)
					else:
						result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
							f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}{text}\n", 
							reply_markup=init_transf)
				if(row.ID_Class_application == 2):
					if(row.ID_Employee == 1):
						result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
						result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на перевод на другой формат работы</b>\n"
							f"<b>Номер заявки:</b> {row.id}\n"
										f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
										f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
										f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
										f"<b>Формат на переход:</b> {row.Future_work_format}\n"
										f"<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
							reply_markup=init_diff)
					else:
						result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на перевод на другой формат работы</b>\n"
							f"<b>Номер заявки:</b> {row.id}\n"
										f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
										f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
										f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
										f"<b>Формат на переход:</b> {row.Future_work_format}\n"
										f"<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
							reply_markup=init_diff)
				if(row.ID_Class_application == 3):
					if(row.ID_Employee == 1):
						result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
						result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на согласование заработной платы</b>\n"
							f"<b>Номер заявки:</b> {row.id}\n"
								f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
								f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
								f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
								f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
								f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
							reply_markup=init_zp)
					else:
						result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на согласование заработной платы</b>\n"
							f"<b>Номер заявки:</b> {row.id}\n"
								f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
								f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
								f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
								f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
								f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
							reply_markup=init_zp)
				if(row.ID_Class_application == 4):
					await callback.message.answer(
						f"<b>Заявка по общей форме</b>\n"
						f"<b>Номер заявки:</b> {row.id}\n"
									f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
									f"<b>Суть обращения: </b>{ row.Essence_question}\n"
									f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
						reply_markup=init_gen)
	elif not result and result_Quest:
		for row in result_Quest:
			result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
			await callback.message.answer(
				f"<b>Вопрос</b>\n"
				f"<b>Номер вопроса:</b> {row.id}\n"
							f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
							f"<b>Суть обращения: </b>{ row.Essence_question}\n"
							f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
				reply_markup=init_quest)
	else:
			await callback.message.answer(  
					f"Отправленных заявок на данный момент нет",
					reply_markup=reply.main
					)
	# Закройте сессию
	session.close()


# Вывод всех заявок
@user_private_router.callback_query(F.data == "sort_app_allI")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
	msg_id = callback.message.message_id
	await bot.delete_message(callback.message.chat.id, msg_id)

	session = Session()
	userData = session.query(table_Employee).filter(table_Employee.c.id_telegram == str(callback.from_user.id)).first()

	userId = userData[1]
	if userId == None:
		await callback.answer('Пользователь не найден', reply_markup=reply.main)
		return

	# Выберите данные из таблицы с использованием фильтрации
	result = session.query(table_application).filter(table_application.c.ID_Initiator == userId, table_application.c.Date_actual_deadline == None).order_by(table_application.c.Date_application).all()
	if result:
			for row in result:
				text = ""
				if row.Date_planned_deadline == None:
					text = ""
				else:
					text = f"\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}"
			# Выведите сообщение с найденными данными и инлайн кнопкой
				result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
				if(row.ID_Class_application == 1):
					if(row.ID_Employee == 1):
						result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
						result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
							f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}{text}\n", 
						reply_markup=init_transf)
					else:
						result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
							f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}{text}\n", 
							reply_markup=init_transf)
				if(row.ID_Class_application == 2):
					if(row.ID_Employee == 1):
						result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
						result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на перевод на другой формат работы</b>\n"
							f"<b>Номер заявки:</b> {row.id}\n"
										f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
										f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
										f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
										f"<b>Формат на переход:</b> {row.Future_work_format}\n"
										f"<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
							reply_markup=init_diff)
					else:
						result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на перевод на другой формат работы</b>\n"
							f"<b>Номер заявки:</b> {row.id}\n"
										f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
										f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
										f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
										f"<b>Формат на переход:</b> {row.Future_work_format}\n"
										f"<b>Дата подачи заявки:</b> {row.Date_application}{text}", 
							reply_markup=init_diff)
				if(row.ID_Class_application == 3):
					if(row.ID_Employee == 1):
						result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
						result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на согласование заработной платы</b>\n"
							f"<b>Номер заявки:</b> {row.id}\n"
								f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
								f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
								f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
								f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
								f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
							reply_markup=init_zp)
					else:
						result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
						await callback.message.answer(
							f"<b>Заявка на согласование заработной платы</b>\n"
							f"<b>Номер заявки:</b> {row.id}\n"
								f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
								f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
								f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
								f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
								f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
							reply_markup=init_zp)
				if(row.ID_Class_application == 4):
					await callback.message.answer(
						f"<b>Заявка по общей форме</b>\n"
						f"<b>Номер заявки:</b> {row.id}\n"
									f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
									f"<b>Суть обращения: </b>{ row.Essence_question}\n"
									f"<b>Дата подачи заявки:</b> {row.Date_application}{text}",
						reply_markup=init_gen)

	else:
			await callback.message.answer(  
					f"Отправленных заявок на данный момент нет",
					reply_markup=reply.main
					)
	# Закройте сессию
	session.close()