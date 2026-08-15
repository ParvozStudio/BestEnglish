from aiogram import Router, F
from aiogram.types import CallbackQuery

from db import Database
from keyboards import courses_kb, back_to_courses_kb
from utils import safe_edit

router = Router()

# Bu bo'lim faqat KO'RISH uchun — fanlar shu yerda ko'rsatiladi,
# lekin "yozilish" tugmasi yo'q. Yozilish faqat "✍️ Kursga yozilish"
# menyusi orqali amalga oshiriladi (handlers/register.py).

COURSE_DESCRIPTIONS = {
    "onatili": {
        "title": "📖 Ona tili kursi",
        "desc": """
📚 <b>Ona tili bo'yicha dars beriladi.</b>

✍️ Savodxonlik, grammatika va nutq o'stirish
👨‍🏫 Tajribali o'qituvchilar
👥 Kichik guruhlarda samarali ta'lim
        """
    },
    "ingliz": {
        "title": "🇬🇧 Ingliz tili kursi",
        "desc": """
📚 <b>Ingliz tili kursi bo'yicha yo'nalishlar:</b>

🅰️ <b>CEFR</b> — Umumiy ingliz tili (A1—C1 darajalari bo'yicha)
🎓 <b>IELTS</b> — Xalqaro sertifikat uchun tayyorlov

✨ Malakali o'qituvchilar, kichik guruhlar va natijaga yo'naltirilgan dastur.
        """
    },
    "ingliz_kids": {
        "title": "🧒 Ingliz tili (Kids)",
        "desc": """
📚 <b>Bolalar uchun ingliz tili kursi.</b>

🎨 O'yin asosidagi qiziqarli darslar
🧑‍🏫 Bolalar bilan ishlashga ixtisoslashgan o'qituvchilar
👥 Kichik guruhlar, individual e'tibor
        """
    },
    "ingliz_grammar": {
        "title": "✏️ Ingliz tili (Grammatika)",
        "desc": """
📚 <b>Ingliz tili grammatikasi bo'yicha maxsus kurs.</b>

📖 Grammatik qoidalarni chuqur va tizimli o'rganish
✍️ Amaliy mashqlar va testlar orqali mustahkamlash
👨‍🏫 Tajribali o'qituvchilar
        """
    },
}


@router.callback_query(F.data == "courses")
async def show_courses(call: CallbackQuery):
    await safe_edit(
        call,
        "📚 <b>Kurslar ro'yxati</b>\n\n"
        "Quyidagi yo'nalishlardan birini tanlang 👇",
        reply_markup=courses_kb()
    )


@router.callback_query(F.data == "course_onatili")
async def show_onatili(call: CallbackQuery):
    info = COURSE_DESCRIPTIONS["onatili"]
    text = f"<b>{info['title']}</b>\n{info['desc']}"
    await safe_edit(call, text, reply_markup=back_to_courses_kb())


@router.callback_query(F.data == "course_ingliz")
async def show_ingliz(call: CallbackQuery):
    info = COURSE_DESCRIPTIONS["ingliz"]
    text = f"<b>{info['title']}</b>\n{info['desc']}"
    await safe_edit(call, text, reply_markup=back_to_courses_kb())


@router.callback_query(F.data == "course_ingliz_kids")
async def show_ingliz_kids(call: CallbackQuery):
    info = COURSE_DESCRIPTIONS["ingliz_kids"]
    text = f"<b>{info['title']}</b>\n{info['desc']}"
    await safe_edit(call, text, reply_markup=back_to_courses_kb())


@router.callback_query(F.data == "course_ingliz_grammar")
async def show_ingliz_grammar(call: CallbackQuery):
    info = COURSE_DESCRIPTIONS["ingliz_grammar"]
    text = f"<b>{info['title']}</b>\n{info['desc']}"
    await safe_edit(call, text, reply_markup=back_to_courses_kb())


@router.callback_query(F.data == "my_apps")
async def my_applications(call: CallbackQuery, db: Database):
    apps = await db.get_user_applications(call.from_user.id)
    if not apps:
        text = "📋 <b>Sizda hali arizalar yo'q.</b>\n\nKursga yozilish uchun «Kursga yozilish» tugmasini bosing."
    else:
        text = "📋 <b>Sizning arizalaringiz:</b>\n\n"
        status_emoji = {"pending": "⏳", "accepted": "✅", "rejected": "❌"}
        status_text_map = {"pending": "Ko'rib chiqilmoqda", "accepted": "Qabul qilindi", "rejected": "Rad etildi"}
        for i, app in enumerate(apps, 1):
            emoji = status_emoji.get(app["status"], "📌")
            stext = status_text_map.get(app["status"], app["status"])
            text += f"{i}. {emoji} <b>{app['course_name']}</b>"
            if app["subcourse"]:
                text += f"\n   📚 {app['subcourse']}"
            text += f"\n   📅 {app['created_at'][:10]} | {stext}\n\n"

    from keyboards import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Yangi ariza", callback_data="enroll")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
    ])
    await safe_edit(call, text, reply_markup=kb)
