from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'main'
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'story': 'Прочитать страшную историю 🧛'
        # Добавить команду в меню можно так:
        # 'command': 'button text'

    })
#
#________________________________ЭХО_______________________
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode =='gpt':
        await gpt_dialog(update,context)
    if dialog.mode=='talk':
        await talk_dialog(update,context)
    if dialog.mode=='quiz':
        await quiz_dialog(update, context)
    if dialog.mode=='story':
        await send_text(update, context, update.callback_query.data)

    else:
        # text = update.message.text
        # print(text)
        await send_text(update,context, start)
# ____________________Рандомный факт________________________

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('random')
    message = load_message('random')
    await send_image(update,context,'random')
    await send_text(update, context, message)
    answer = await chat_gpt.send_question(prompt,'')
    await send_text_buttons(update, context,answer,random_map)
async def random_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    cb=update.callback_query.data
    if cb=="random_more":
        await random(update, context)

    else:
        await send_text(update,context,"Нажмите /start")


# _____________________________Вопрос GPT________________________________
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'gpt'
    prompt = load_prompt('gpt')
    message = load_message('gpt')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'gpt')
    await send_text(update, context, message)


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=update.message.text
    message=await send_text(update, context, "Думаю над вопросом...")
    answer = await chat_gpt.add_message(text)
    await message.edit_text(answer)

# ___________________________Разговор___________________________________________
async def talk(update:Update,context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'talk'
    message = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, message, talking_map)

async def talk_button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    companion = update.callback_query.data
    await send_image(update,context,companion)
    chat_gpt.set_prompt(load_prompt(companion) )
    await send_text(update,context,f'Начните разгвор с {talking_map.get(companion)}')

async def talk_dialog(update:Update, context:ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)

# _____________________________________КВИЗ_________________________________________
async def quiz(update:Update, context:ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'quiz'
    message = load_message('quiz')
    dialog.isStart=False
    dialog.count=0
    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, message, quiz_map)
    chat_gpt.set_prompt(load_prompt('quiz'))

async def quiz_button(update:Update, context:ContextTypes.DEFAULT_TYPE):


    await update.callback_query.answer()
    topic = update.callback_query.data
    if dialog.isStart is False:
        message = await send_text(update,context,f'Выбрана тема {quiz_map[topic]}')
        dialog.isStart=True
    else:
        message = await send_text(update, context, f'Продолжаем Квиз')
    answer = await chat_gpt.add_message(topic)
    await message.edit_text(answer)



async def quiz_dialog(update:Update, context:ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if answer =="Правильно!":
        dialog.count+=1
    await send_text_buttons(update, context, f'{answer} Привильных ответов {dialog.count}',{
        'quiz_more':"Задай еще вопрос"
    } )


# ____________Scary_story________________

async def story(update:Update, context:ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'story'
    prompt = load_prompt('story')
    await send_image(update,context,'story')
    chat_gpt.set_prompt(prompt)
    await send_text_buttons(update,context,'Сейчас я расскажу тебе страшную историю...',
    {'story_next': 'Давай колдун *чий '})

async def story_button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    answer = await chat_gpt.add_message(data)
    await send_text_buttons(update,context,answer,
                                      {'story_next': 'Продолжай колдун *чий',
                                       'story_end':'Страшно нахрен вырубай'})









talking_map = {
        'talk_Cobain': 'Курт Кобейн',
        'talk_queen': "Елизавета II",
        'talk_Tolkien':'Джон Толкиен',
        'talk_Nietzsche':'Фридрих Ницше',
        'talk_Hawking':'Стивен Хокинг'
    }


quiz_map={'quiz_prog':'Программирование на Python',
           'quiz_math':'Математическая теория',
           'quiz_biology':'Биология',
           }



random_map={
        'random_more':'Хочу ещё рандомный факт',
        'random_end':"Закончить"
    }












dialog = Dialog()
dialog.mode = None
dialog.count = 0
dialog.isStart =False

# Переменные можно определить, как атрибуты dialog

chat_gpt = ChatGptService(ChatGPT_TOKEN)

app = ApplicationBuilder().token(
    "7383138708:AAH7afwmbkXtfg_XVY7t5FDWRGa5xUcbVkA").build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random',random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('story', story))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND , text_handler))

# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))

# Зарегистрировать обработчик кнопки можно так:

# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(random_button, pattern='^random_.*'))
app.add_handler(CallbackQueryHandler(talk_button, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(quiz_button, pattern='^quiz_.*'))
app.add_handler(CallbackQueryHandler(story_button, pattern='^story_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
