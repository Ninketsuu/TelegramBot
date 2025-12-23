import asyncio
import logging
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton, FSInputFile,
)
from dotenv import load_dotenv

from db import init_db, add_user_if_not_exists, add_water, add_sleep, add_steps, \
    log_mood, get_mood_stats, add_task, list_tasks, complete_task, \
    add_achievement, list_achievements

photo = FSInputFile('photos/бот.jpg')

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
router = Router()
dp.include_router(router)

# ========= Клавиатуры =========

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🏃‍♂️ Тело"),
                KeyboardButton(text="🧠 Душа"),
            ],
            [
                KeyboardButton(text="🚀 Развитие"),
            ],
        ],
        resize_keyboard=True,
    )

def body_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💧 Записать воду"),
             KeyboardButton(text="😴 Сон")],
            [KeyboardButton(text="🚶‍♂️ Шаги/спорт")],
            [KeyboardButton(text="💡 Советы по телу")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True,
    )

def soul_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆘 SOS (анти-стресс)")],
            [KeyboardButton(text="📓 Дневник настроения")],
            [KeyboardButton(text="🧭 Навигатор помощи")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True,
    )

def social_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏱ Pomodoro 25 мин")],
            [KeyboardButton(text="📝 Задачи на учебу")],
            [KeyboardButton(text="🧪 Мини-тест интересов")],
            [KeyboardButton(text="🗣 Софт-скиллы советы")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True,
    )

def mood_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="😀", callback_data="mood_5"),
                InlineKeyboardButton(text="🙂", callback_data="mood_4"),
                InlineKeyboardButton(text="😐", callback_data="mood_3"),
                InlineKeyboardButton(text="🙁", callback_data="mood_2"),
                InlineKeyboardButton(text="😢", callback_data="mood_1"),
            ]
        ]
    )

def sos_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🫁 Дыхание 4-7-8", callback_data="sos_breath")],
            [InlineKeyboardButton(text="🦶 Заземление 5-4-3-2-1", callback_data="sos_ground")],
        ]
    )

def help_nav_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤕 Буллинг", callback_data="help_bullying")],
            [InlineKeyboardButton(text="🏠 Конфликт с родителями", callback_data="help_parents")],
            [InlineKeyboardButton(text="📚 Стресс перед экзаменами", callback_data="help_exams")],
        ]
    )

def tasks_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить задачу", callback_data="task_add")],
            [InlineKeyboardButton(text="✅ Отметить выполненной", callback_data="task_done")],
            [InlineKeyboardButton(text="📋 Показать список", callback_data="task_list")],
        ]
    )

def pomodoro_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Старт 25 минут", callback_data="pomodoro_start")],
        ]
    )

def interests_test_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨‍🔬 Наука/медицина", callback_data="test_science"),
            ],
            [
                InlineKeyboardButton(text="🎨 Творчество", callback_data="test_art"),
            ],
            [
                InlineKeyboardButton(text="💻 Технологии", callback_data="test_it"),
            ],
            [
                InlineKeyboardButton(text="🤝 Помощь людям", callback_data="test_help"),
            ],
        ]
    )

# ========= /start =========

@router.message(CommandStart())
async def cmd_start(message: Message):
    await add_user_if_not_exists(message.from_user.id)
    text = (
        "Привет! ✨ Я бот «Я проектирую свое благополучие».\n\n"
        "Помогаю прокачивать баланс между телом, душой и развитием:\n"
        "🏃‍♂️ Тело — трекинг воды, сна, активности и мини-челленджи.\n"
        "🧠 Душа — дневник настроения, SOS-практики при стрессе.\n"
        "🚀 Развитие — тайм-менеджмент, задачи, мини-тест интересов.\n\n"
        "Выбери направление, с которого хочешь начать 👇"
    )
    await message.answer_photo(photo=photo, reply_markup=main_menu_kb(), caption=text)
    #await message.answer(text, reply_markup=main_menu_kb())

# ========= ГЛАВНОЕ МЕНЮ =========

@router.message(F.text == "🏃‍♂️ Тело")
async def body_menu(message: Message):
    await message.answer(
        "Блок «Тело» 💪\nВыбирай, что отслеживаем или улучшаем сегодня.",
        reply_markup=body_menu_kb(),
    )

@router.message(F.text == "🧠 Душа")
async def soul_menu(message: Message):
    await message.answer(
        "Блок «Душа» 💛\nПоддержка настроения и анти-стресс практики.",
        reply_markup=soul_menu_kb(),
    )

@router.message(F.text == "🚀 Развитие")
async def social_menu(message: Message):
    await message.answer(
        "Блок «Развитие» 🚀\nУчеба, планирование и самопознание.",
        reply_markup=social_menu_kb(),
    )

@router.message(F.text == "⬅️ В меню")
async def back_to_main(message: Message):
    await message.answer("Возвращаю в главное меню ⚖️", reply_markup=main_menu_kb())

# ========= БЛОК ТЕЛО =========

@router.message(F.text == "💧 Записать воду")
async def ask_water(message: Message):
    await message.answer("Сколько воды ты выпил(а) сегодня? Напиши в миллилитрах, например: 250")

@router.message(F.text.regexp(r"^\d{2,4}$"))
async def save_water(message: Message):
    amount = int(message.text)
    await add_water(message.from_user.id, amount)
    await message.answer(f"Записал 💧 {amount} мл. Так держать! 🚰")

@router.message(F.text == "😴 Сон")
async def ask_sleep(message: Message):
    await message.answer("Сколько часов ты спал(а) прошлой ночью? Напиши, например: 7.5")

@router.message(F.text.regexp(r"^\d{1,2}(\.\d)?$"))
async def save_sleep(message: Message):
    hours = float(message.text.replace(",", "."))
    await add_sleep(message.from_user.id, hours)
    comment = "Отлично, почти идеальный диапазон 😴" if 7 <= hours <= 9 else "Постарайся приблизиться к 7–9 часам сна 🌙"
    await message.answer(f"Записал сон: {hours} ч.\n{comment}")

@router.message(F.text == "🚶‍♂️ Шаги/спорт")
async def ask_steps(message: Message):
    await message.answer("Сколько шагов/минут активности у тебя сегодня? Напиши число, например: 8000")

@router.message(F.text.regexp(r"^\d{3,6}$"))
async def save_steps_handler(message: Message):
    steps = int(message.text)
    await add_steps(message.from_user.id, steps)
    badge = None
    if steps >= 10000:
        badge = "🏅 «Легенда шагов»"
    elif steps >= 5000:
        badge = "🎖 «Активный день»"
    if badge:
        await add_achievement(message.from_user.id, badge)
        await message.answer(f"Записал {steps} шагов/ед. активности.\nТы получаешь ачивку: {badge} 🎉")
    else:
        await message.answer(f"Записал {steps} шагов/ед. активности. Движение — это сила 💪")

@router.message(F.text == "💡 Советы по телу")
async def body_tips(message: Message):
    tips = [
        "Выбирай «умный перекус»: орехи, йогурт, фрукты — топ для мозга и энергии 🧠",
        "Старайся вставать и разминаться каждые 40–60 минут, если много сидишь за компом 🪑",
        "Вода > сладкие газировки. Начни день со стакана воды 💧",
    ]
    text = "Вот несколько идей для заботы о теле сегодня:\n\n" + "\n\n".join(f"• {t}" for t in tips)
    await message.answer(text)

# ========= БЛОК ДУША =========

@router.message(F.text == "📓 Дневник настроения")
async def mood_diary(message: Message):
    await message.answer(
        "Отметь, как ты сейчас себя чувствуешь 👇",
        reply_markup=mood_kb(),
    )

@router.callback_query(F.data.startswith("mood_"))
async def mood_chosen(callback: CallbackQuery):
    score = int(callback.data.split("_")[1])
    await log_mood(callback.from_user.id, score)
    reactions = {
        5: "Круто! Поделись этим настроением с кем-то ещё 🌞",
        4: "Отлично! Береги этот ресурс 💛",
        3: "Нормально. Можно добавить немного приятных мелочей сегодня ☕",
        2: "Немного тяжеловато. Поддержи себя чем-то маленьким и приятным 💌",
        1: "Грустно 🖤 Если хочется — напиши близкому человеку или специалисту.",
    }
    await callback.message.edit_text(
        f"Записал твой настрой. {reactions.get(score, '')}"
    )
    stats = await get_mood_stats(callback.from_user.id)
    if stats:
        avg, count = stats
        await callback.message.answer(
            f"В твоём дневнике уже {count} отметок. Среднее настроение: {avg:.1f}/5 📊"
        )
    await callback.answer()

@router.message(F.text == "🆘 SOS (анти-стресс)")
async def sos_menu(message: Message):
    await message.answer(
        "Выбери технику, чтобы немного снизить напряжение прямо сейчас 💛",
        reply_markup=sos_kb(),
    )

@router.callback_query(F.data == "sos_breath")
async def sos_breath(callback: CallbackQuery):
    text = (
        "Дыхание 4–7–8 ✨\n\n"
        "1) Вдохни через нос на 4 счёта.\n"
        "2) Задержи дыхание на 7 счётов.\n"
        "3) Медленно выдыхай через рот на 8 счётов.\n\n"
        "Сделай 4 цикла. Можно закрыть глаза и представить место, где тебе спокойно."
    )
    await callback.message.edit_text(text)
    await callback.answer("Попробуй сделать 4 цикла дыхания 🫁")

@router.callback_query(F.data == "sos_ground")
async def sos_ground(callback: CallbackQuery):
    text = (
        "Техника заземления 5-4-3-2-1 🌍\n\n"
        "Оглянись вокруг и назови:\n"
        "• 5 вещей, которые ты видишь\n"
        "• 4 вещи, которые можешь потрогать\n"
        "• 3 звука, которые слышишь\n"
        "• 2 запаха\n"
        "• 1 вкус\n\n"
        "Это помогает вернуть внимание в «здесь и сейчас»."
    )
    await callback.message.edit_text(text)
    await callback.answer("Сконцентрируйся на чувствах здесь и сейчас 💛")

@router.message(F.text == "🧭 Навигатор помощи")
async def help_navigator(message: Message):
    await message.answer(
        "Выбери ситуацию, в которой сейчас нуждаешься в подсказке 👇",
        reply_markup=help_nav_kb(),
    )

@router.callback_query(F.data == "help_bullying")
async def help_bullying(callback: CallbackQuery):
    text = (
        "Буллинг — это не норма.\n\n"
        "• Ты имеешь право на безопасность и уважение.\n"
        "• Зафиксируй случаи (скриншоты, сообщения).\n"
        "• Обратись к взрослому, которому доверяешь: классный руководитель, школьный психолог, родитель.\n"
        "• Если есть риск опасности — звони в экстренные службы своего региона.\n\n"
        "Важно: ты не виноват(а) в том, что тебя травят."
    )
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "help_parents")
async def help_parents(callback: CallbackQuery):
    text = (
        "Конфликты с родителями — частая история.\n\n"
        "• Выбери момент, когда эмоции утихли, и говори о чувствах («Я-сообщения»).\n"
        "• Чётко сформулируй, что для тебя важно и чего бы ты хотел(а).\n"
        "• Если не получается договориться, можно привлечь медиатора: школьного психолога, классного руководителя.\n"
        "• Помни: твои чувства и границы имеют значение."
    )
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "help_exams")
async def help_exams(callback: CallbackQuery):
    text = (
        "Стресс перед экзаменами — это нормальная реакция.\n\n"
        "• Разбей подготовку на маленькие блоки по 25–40 минут с перерывами.\n"
        "• Отрабатывай типовые задания, а не «всё подряд».\n"
        "• Высыпайся: недосып сильно снижает концентрацию.\n"
        "• Если тревога мешает вообще садиться за учёбу — стоит обсудить это со специалистом (психологом).\n"
    )
    await callback.message.edit_text(text)
    await callback.answer()

# ========= БЛОК РАЗВИТИЕ =========

@router.message(F.text == "⏱ Pomodoro 25 мин")
async def pomodoro_menu(message: Message):
    await message.answer(
        "Метод Pomodoro: 25 минут фокусной работы + 5 минут отдыха.\nНажми старт, чтобы запустить сессию 👇",
        reply_markup=pomodoro_inline(),
    )

@router.callback_query(F.data == "pomodoro_start")
async def pomodoro_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "Таймер Pomodoro запущен на 25 минут ⏱\nСфокусируйся на одной задаче без отвлечений."
    )
    await callback.answer("По окончании я напомню 🛎")

    async def notify():
        await asyncio.sleep(25 * 60)  # для теста можно поставить 10
        try:
            await callback.message.answer(
                "⏰ Время! Pomodoro завершён.\nСделай небольшой перерыв 5 минут ☕"
            )
        except Exception:
            pass

    asyncio.create_task(notify())

@router.message(F.text == "📝 Задачи на учебу")
async def tasks_menu(message: Message):
    await message.answer(
        "Задачи на учёбу: фиксируй, что хочешь сделать сегодня или на неделю.\n"
        "Выбери действие 👇",
        reply_markup=tasks_menu_inline(),
    )

@router.callback_query(F.data == "task_add")
async def task_add(callback: CallbackQuery):
    await callback.message.edit_text(
        "Напиши одну задачу для учебы или развития.\nНапример: «Выучить 10 слов по английскому»."
    )
    # следующий текст-сообщение пользователя будет пойман ниже
    await callback.answer()

@router.message(F.text.startswith("Задача:"))
async def task_add_from_text(message: Message):
    # Этот хендлер можно не использовать, если обрабатывать любые тексты
    pass

# простой вариант: любое текстовое сообщение после нажатия task_add будет задачей
last_task_request = {}  # user_id -> bool

@router.callback_query(F.data == "task_add")
async def task_add_request(callback: CallbackQuery):
    last_task_request[callback.from_user.id] = True
    await callback.message.edit_text(
        "Напиши задачу, я её запомню 📌"
    )
    await callback.answer()

@router.message()
async def catch_task_or_route(message: Message):
    # если пользователь только что нажал «добавить задачу»
    if last_task_request.get(message.from_user.id):
        title = message.text.strip()
        if len(title) < 3:
            await message.answer("Сделай формулировку чуть конкретнее, хотя бы 3 символа 🙂")
            return
        await add_task(message.from_user.id, title)
        last_task_request[message.from_user.id] = False
        await message.answer(f"Задача сохранена: «{title}» ✅", reply_markup=social_menu_kb())
        return

    # остальные сообщения игнорировать или вернуть в меню, если не подошли другие хендлеры выше
    # Если текст совпадает с уже обработанными ранее (меню/команды), сюда он не попадёт.


@router.callback_query(F.data == "task_list")
async def task_list_cb(callback: CallbackQuery):
    tasks = await list_tasks(callback.from_user.id)
    if not tasks:
        await callback.message.edit_text("Пока задач нет. Добавь хотя бы одну 📌")
    else:
        lines = []
        for t in tasks:
            status = "✅" if t["done"] else "❗"
            lines.append(f"{status} {t['id']}. {t['title']}")
        await callback.message.edit_text("Твои задачи:\n\n" + "\n".join(lines))
    await callback.answer()

@router.callback_query(F.data == "task_done")
async def task_done_cb(callback: CallbackQuery):
    await callback.message.edit_text(
        "Напиши номер задачи, которую выполнил(а).\nНомер можно посмотреть в списке задач."
    )
    last_task_request[callback.from_user.id] = False  # сбрасываем флаг добавления
    # следующий текст будем трактовать как номер задачи
    # Сделаем отдельный флаг
    global waiting_done
    try:
        waiting_done[callback.from_user.id] = True
    except NameError:
        waiting_done = {callback.from_user.id: True}
    await callback.answer()

@router.message(F.text.regexp(r"^\d+$"))
async def mark_task_done(message: Message):
    global waiting_done
    if "waiting_done" in globals() and waiting_done.get(message.from_user.id):
        task_id = int(message.text)
        ok = await complete_task(message.from_user.id, task_id)
        waiting_done[message.from_user.id] = False
        if ok:
            await message.answer(f"Задача №{task_id} отмечена выполненной ✅")
            await add_achievement(message.from_user.id, "🎓 «Фокус и дисциплина»")
        else:
            await message.answer("Не нашёл такую задачу. Проверь номер ещё раз 🙂")

@router.message(F.text == "🧪 Мини-тест интересов")
async def test_interests(message: Message):
    await message.answer(
        "Выбери, что сейчас тебе ближе по духу 👇",
        reply_markup=interests_test_kb(),
    )

@router.callback_query(F.data.startswith("test_"))
async def test_result(callback: CallbackQuery):
    data = callback.data
    if data == "test_science":
        text = (
            "Тебе может заходить направление, связанное с наукой и медициной 👨‍⚕️🔬\n"
            "Обрати внимание на профессии: врач, биотехнолог, исследователь, преподаватель."
        )
    elif data == "test_art":
        text = (
            "Похоже, тебе близко творчество 🎨\n"
            "Профессии: дизайнер, иллюстратор, музыкант, режиссёр, контент-креатор."
        )
    elif data == "test_it":
        text = (
            "Тебя тянет к технологиям 💻\n"
            "Профессии: программист, аналитик данных, тестировщик, системный админ, разработчик игр."
        )
    else:
        text = (
            "Тебе важно помогать людям 🤝\n"
            "Профессии: психолог, педагог, социальный работник, врач, ментор."
        )
    await callback.message.edit_text(text)
    await callback.answer()

@router.message(F.text == "🗣 Софт-скиллы советы")
async def soft_skills(message: Message):
    tips = [
        "Перед выступлением проговори первые 2–3 фразы вслух — это снижает волнение 🎤",
        "Научись задавать уточняющие вопросы: «Правильно ли я понял(а), что…?» — это улучшает общение 🤝",
        "Делай маленькие шаги: включайся в обсуждения на 1–2 реплики, а не сразу веди весь диалог 💬",
    ]
    await message.answer("Несколько идей по софт-скиллам:\n\n" + "\n\n".join(f"• {t}" for t in tips))

# ========= Ачивки (опциональная команда) =========

@router.message(Command("achievements"))
async def show_achievements(message: Message):
    ach = await list_achievements(message.from_user.id)
    if not ach:
        await message.answer("У тебя пока нет ачивок. Всё впереди! ⭐")
    else:
        text = "Твои ачивки:\n\n" + "\n".join(f"• {a['title']} ({a['created_at']})" for a in ach)
        await message.answer(text)


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("Не найден BOT_TOKEN в .env")
    await init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
