from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import Database
from keyboards import (
    phone_share_kb, main_menu_kb, enroll_courses_kb,
    after_enroll_kb
)
from utils import safe_edit

router = Router()


class RegisterStates(StatesGroup):
    waiting_phone = State()
    waiting_age = State()


COURSE_NAMES = {
    "onatili": "📖 Ona tili",
    "ingliz_cefr": "🇬🇧 Ingliz tili (CEFR)",
    "ingliz_ielts": "🇬🇧 Ingliz tili (IELTS)",
    "ingliz_kids": "🧒 Ingliz tili (Kids)",
    "ingliz_grammar": "✏️ Ingliz tili (Grammatika)",
}


async def check_registration(call: CallbackQuery, db: Database, state: FSMContext, course_key: str):
    user = await db.get_user(call.from_user.id)
    if not user or not user.get("is_registered"):
        # Ro'yxatdan o'tish kerak
        await state.update_data(pending_course=course_key)
        await state.set_state(RegisterStates.waiting_phone)
        await safe_edit(
            call,
            "📱 <b>Ro'yxatdan o'tish</b>\n\n"
            "Kursga yozilish uchun avval ro'yxatdan o'tishingiz kerak.\n\n"
            "Telefon raqamingizni ulashing yoki qo'lda kiriting (+998XXXXXXXXX):",
        )
        await call.message.answer(
            "👇 Pastdagi tugmani bosing:",
            reply_markup=phone_share_kb()
        )
        return False
    return True


@router.callback_query(F.data == "enroll")
async def start_enroll(call: CallbackQuery):
    await safe_edit(
        call,
        "✍️ <b>Kursga yozilish</b>\n\nQaysi kursga yozilmoqchisiz?",
        reply_markup=enroll_courses_kb()
    )


@router.callback_query(F.data.startswith("enroll_"))
async def enroll_course(call: CallbackQuery, state: FSMContext, db: Database):
    course_key = call.data.replace("enroll_", "")
    if not course_key or course_key not in COURSE_NAMES:
        await call.answer("Kurs noto'g'ri!", show_alert=True)
        return

    is_registered = await check_registration(call, db, state, course_key)
    if not is_registered:
        return

    course_name = COURSE_NAMES[course_key]
    await state.update_data(course_key=course_key, course_name=course_name)

    from keyboards import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Ha, {course_name} kursiga yozilaman!", callback_data=f"confirm_enroll_{course_key}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="main_menu")],
    ])
    await safe_edit(
        call,
        f"✍️ <b>Kursga yozilishni tasdiqlang</b>\n\n"
        f"Siz <b>{course_name}</b> kursiga yozilmoqchisiz.\n\n"
        f"Tasdiqlayman?",
        reply_markup=kb
    )


@router.callback_query(F.data.startswith("confirm_enroll_"))
async def confirm_enrollment(call: CallbackQuery, state: FSMContext, db: Database):
    course_key = call.data.replace("confirm_enroll_", "")
    course_name = COURSE_NAMES.get(course_key, course_key)

    await db.add_application(call.from_user.id, course_name)

    user = await db.get_user(call.from_user.id)
    name = user.get("full_name", "Foydalanuvchi") if user else "Foydalanuvchi"

    await safe_edit(
        call,
        f"🎉 <b>Tabriklaymiz, {name}!</b>\n\n"
        f"✅ <b>{course_name}</b> kursiga arizangiz muvaffaqiyatli yuborildi!\n\n"
        f"📞 Tez orada adminlarimiz siz bilan bog'lanadi.\n\n"
        f"📋 Arizalaringizni kuzatib boring!",
        reply_markup=after_enroll_kb()
    )

    # Adminlarga xabar yuborish
    from config import ADMIN_IDS
    phone = user.get("phone", "Kiritilmagan") if user else "Kiritilmagan"
    child_name = user.get("child_name") if user else None
    username = f"@{call.from_user.username}" if call.from_user.username else "yo'q"

    admin_text = (
        f"📬 <b>Yangi ariza!</b>\n\n"
        f"👤 Ism: {name}\n"
        f"🆔 ID: <code>{call.from_user.id}</code>\n"
        f"📱 Telefon: {phone}\n"
        f"💬 Username: {username}\n"
        f"📚 Kurs: <b>{course_name}</b>"
    )
    if child_name:
        admin_text += f"\n🧒 Farzand ismi: {child_name}"

    bot = call.bot
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception:
            pass

    await state.clear()


# =================== REGISTRATION ===================

@router.message(RegisterStates.waiting_phone, F.contact)
async def get_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await state.update_data(phone=phone)
    await state.set_state(RegisterStates.waiting_age)

    from aiogram.types import ReplyKeyboardRemove
    await message.answer(
        f"✅ Telefon: <b>{phone}</b>\n\n"
        f"📅 Ta'lim oluvchining (o'zingiz yoki farzandingizning) yoshini kiriting (masalan: 8):",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(RegisterStates.waiting_phone, F.text)
async def get_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not (phone.startswith("+998") and len(phone) == 13 and phone[1:].isdigit()):
        await message.answer(
            "❌ Noto'g'ri format!\n\nIltimos, raqamni +998XXXXXXXXX formatida kiriting:",
            reply_markup=phone_share_kb()
        )
        return
    await state.update_data(phone=phone)
    await state.set_state(RegisterStates.waiting_age)

    from aiogram.types import ReplyKeyboardRemove
    await message.answer(
        f"✅ Telefon: <b>{phone}</b>\n\n"
        f"📅 Ta'lim oluvchining (o'zingiz yoki farzandingizning) yoshini kiriting (masalan: 8):",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(RegisterStates.waiting_age)
async def get_age(message: Message, state: FSMContext, db: Database):
    try:
        age = int(message.text.strip())
        if not (2 <= age <= 80):
            raise ValueError
    except ValueError:
        await message.answer("❌ Yosh 2 dan 80 gacha bo'lishi kerak. Qaytadan kiriting:")
        return

    data = await state.get_data()
    phone = data.get("phone", "")
    await db.update_user_registration(message.from_user.id, phone, age)

    pending_course = data.get("pending_course")

    await message.answer(
        f"🎉 <b>Ro'yxatdan o'tdingiz!</b>\n\n"
        f"📱 Telefon: <b>{phone}</b>\n"
        f"🎂 Yosh: <b>{age}</b>\n\n"
        f"✅ Ma'lumotlaringiz saqlandi!"
    )

    if pending_course and pending_course in COURSE_NAMES:
        course_name = COURSE_NAMES[pending_course]
        await db.add_application(message.from_user.id, course_name)

        from config import ADMIN_IDS
        user = await db.get_user(message.from_user.id)
        name = user.get("full_name", "Foydalanuvchi") if user else "Foydalanuvchi"
        username = f"@{message.from_user.username}" if message.from_user.username else "yo'q"

        for admin_id in ADMIN_IDS:
            try:
                await message.bot.send_message(
                    admin_id,
                    f"📬 <b>Yangi ariza (yangi foydalanuvchi)!</b>\n\n"
                    f"👤 Ism: {name}\n"
                    f"🆔 ID: <code>{message.from_user.id}</code>\n"
                    f"📱 Telefon: {phone}\n"
                    f"🎂 Yosh: {age}\n"
                    f"💬 Username: {username}\n"
                    f"📚 Kurs: <b>{course_name}</b>"
                )
            except Exception:
                pass

        await message.answer(
            f"✍️ <b>{course_name}</b> kursiga arizangiz yuborildi!\n\n"
            f"📞 Tez orada siz bilan bog'lanishadi.",
            reply_markup=after_enroll_kb()
        )
    else:
        await message.answer(
            "🏠 Bosh menyuga o'tish uchun tugmani bosing:",
            reply_markup=main_menu_kb()
        )

    await state.clear()
