import os

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile
from keyboards import back_to_menu_kb

router = Router()

ABOUT_VIDEO_PATH = os.path.join(os.path.dirname(__file__), "about_video.mp4")


def about_text() -> str:
    return """
🎓 <b>BestEnglish o'quv markazi haqida</b>

━━━━━━━━━━━━━━━━━━━━
🏆 <b>Bizning afzalliklarimiz:</b>

🚀 <b>Sifat</b> — Asosiy qadriyatimiz ta'lim sifati!
👨‍🏫 Malakali va tajribali o'qituvchilar
👶 Kattalar va bolalar uchun alohida yondashuv
🕐 Qulay dars jadvali

━━━━━━━━━━━━━━━━━━━━
📚 <b>Kurslar ro'yxati:</b>

📖 <b>Ona tili</b>
🇬🇧 <b>Ingliz tili</b> — CEFR va IELTS yo'nalishlari
🧒 <b>Ingliz tili (Kids)</b> — bolalar uchun
✏️ <b>Ingliz tili (Grammatika)</b>

━━━━━━━━━━━━━━━━━━━━
✨ <i>Farzandingiz kelajagi bugun boshlanadi!</i>
    """


async def send_about(bot: Bot, chat_id: int):
    """Video va markaz haqidagi ma'lumot BITTA xabar sifatida yuboriladi —
    video pastida (caption) ma'lumot va orqaga tugmasi joylashadi."""
    text = about_text()
    if os.path.exists(ABOUT_VIDEO_PATH):
        try:
            await bot.send_video(
                chat_id,
                video=FSInputFile(ABOUT_VIDEO_PATH),
                caption=text,
                reply_markup=back_to_menu_kb()
            )
            return
        except Exception:
            pass
    await bot.send_message(chat_id, text, reply_markup=back_to_menu_kb())


@router.callback_query(F.data == "about")
async def show_about(call: CallbackQuery):
    try:
        await call.message.delete()
    except Exception:
        pass
    await send_about(call.bot, call.message.chat.id)
