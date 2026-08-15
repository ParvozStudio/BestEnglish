import os

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from db import Database
from keyboards import main_menu_kb, back_to_menu_kb

router = Router()

MAIN_MENU_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "logo.jpg")

WELCOME_TEXT = """
🎓 <b>BestEnglish o'quv markaziga xush kelibsiz!</b>

━━━━━━━━━━━━━━━━━━━━
🚀 <b>Asosiy qadriyatimiz — ta'lim sifati!</b>
👨‍🏫 Malakali va tajribali o'qituvchilar
👶 Kattalar va bolalar uchun alohida dasturlar
━━━━━━━━━━━━━━━━━━━━

📚 <b>Bizda mavjud yo'nalishlar:</b>
• 📖 Ona tili
• 🇬🇧 Ingliz tili (CEFR / IELTS)
• 🧒 Ingliz tili (Kids)
• ✏️ Ingliz tili (Grammatika)

✨ <i>Farzandingiz kelajagi bugun boshlanadi — biz bilan!</i>

👇 Quyidagi menyudan boshlang:
"""


async def send_main_menu(bot: Bot, chat_id: int, text: str = WELCOME_TEXT):
    """Bosh menyuni rasm bilan birga yuboradi, chiroyli ko'rinishi uchun."""
    if os.path.exists(MAIN_MENU_IMAGE_PATH):
        try:
            await bot.send_photo(
                chat_id,
                photo=FSInputFile(MAIN_MENU_IMAGE_PATH),
                caption=text,
                reply_markup=main_menu_kb()
            )
            return
        except Exception:
            pass
    await bot.send_message(chat_id, text, reply_markup=main_menu_kb())


@router.message(CommandStart())
async def cmd_start(message: Message, db: Database):
    user = message.from_user
    await db.add_user(
        telegram_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    await send_main_menu(message.bot, message.chat.id)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await send_main_menu(message.bot, message.chat.id, "🏠 <b>Bosh menyu</b>\n\nQuyidan kerakli bo'limni tanlang:")


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = """
ℹ️ <b>Bot haqida ma'lumot</b>

🤖 Bu bot <b>BestEnglish</b> o'quv markazi uchun yaratilgan.

<b>Mavjud buyruqlar:</b>
/start — Botni ishga tushirish
/menu — Bosh menyuga qaytish
/courses — Kurslar ro'yxati
/about — Biz haqimizda
/contact — Bog'lanish
/myapps — Mening arizalarim
/help — Yordam
    """
    await message.answer(text, reply_markup=back_to_menu_kb())


@router.message(Command("courses"))
async def cmd_courses(message: Message):
    from keyboards import courses_kb
    await message.answer(
        "📚 <b>Kurslar ro'yxati</b>\n\nQaysi yo'nalish sizni qiziqtiradi?",
        reply_markup=courses_kb()
    )


@router.message(Command("about"))
async def cmd_about(message: Message):
    from about import send_about
    await send_about(message.bot, message.chat.id)


@router.message(Command("contact"))
async def cmd_contact(message: Message):
    from contact import contact_text
    from keyboards import contact_kb
    await message.answer(contact_text(), reply_markup=contact_kb())


@router.message(Command("myapps"))
async def cmd_myapps(message: Message, db: Database):
    apps = await db.get_user_applications(message.from_user.id)
    if not apps:
        text = "📋 <b>Sizda hali arizalar yo'q.</b>\n\nKursga yozilish uchun menyudan foydalaning."
    else:
        text = "📋 <b>Sizning arizalaringiz:</b>\n\n"
        status_emoji = {"pending": "⏳", "accepted": "✅", "rejected": "❌"}
        for i, app in enumerate(apps, 1):
            emoji = status_emoji.get(app["status"], "📌")
            status_text = {"pending": "Ko'rib chiqilmoqda", "accepted": "Qabul qilindi", "rejected": "Rad etildi"}.get(app["status"], app["status"])
            text += f"{i}. {emoji} <b>{app['course_name']}</b>"
            if app["subcourse"]:
                text += f" — {app['subcourse']}"
            text += f"\n   📅 {app['created_at'][:10]} | {status_text}\n\n"
    await message.answer(text, reply_markup=back_to_menu_kb())


@router.callback_query(F.data == "main_menu")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.delete()
    except Exception:
        pass
    await send_main_menu(call.bot, call.message.chat.id, "🏠 <b>Bosh menyu</b>\n\nQuyidan kerakli bo'limni tanlang:")
