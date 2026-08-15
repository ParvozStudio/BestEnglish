import os

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS, PAYMENT_CARD_NUMBER, PAYMENT_CONTACT, PAYMENT_DEADLINE_DAY
from db import Database
from keyboards import (
    admin_panel_kb, admin_app_actions_kb, admin_users_nav_kb, back_to_menu_kb,
    payment_reminder_confirm_kb, InlineKeyboardMarkup, InlineKeyboardButton,
    payments_menu_kb, payments_list_kb, unpaid_student_detail_kb, paid_student_detail_kb,
)
from utils import safe_edit

router = Router()

ADMIN_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "logo.jpg")

LIMIT = 5  # Users per page


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def send_admin_panel(bot: Bot, chat_id: int, text: str):
    """Admin panelni rasm bilan birga yuboradi."""
    if os.path.exists(ADMIN_IMAGE_PATH):
        try:
            await bot.send_photo(
                chat_id,
                photo=FSInputFile(ADMIN_IMAGE_PATH),
                caption=text,
                reply_markup=admin_panel_kb()
            )
            return
        except Exception:
            pass
    await bot.send_message(chat_id, text, reply_markup=admin_panel_kb())


# Admin panel rasm bilan (caption) ko'rsatilgani uchun undan matnli bo'limlarga
# o'tishda oddiy edit_text ishlamaydi — shared safe_edit shu holatni avtomatik
# hal qiladi (o'chirib, yangi matnli xabar yuboradi).
safe_render = safe_edit


class BroadcastState(StatesGroup):
    waiting_message = State()


class PaymentReminderState(StatesGroup):
    waiting_month = State()


def build_payment_reminder_text(month: str) -> str:
    return (
        "Assalomu aleykum !\n"
        f"Shu hafta ohirigacha <b>{month}</b> oyi to'lovlarini (bermaganlar) "
        "to'lovni yopishi shart ❗️\n\n"
        "Qo'shimcha ma'lumotlar uchun:🌐\n"
        f"{PAYMENT_CONTACT}\n"
        "shu telegram akkauntiga murojat qilishingiz mumkin 📱\n\n"
        "Karta raqam kerak bolsa 💳\n"
        f"<code>{PAYMENT_CARD_NUMBER}</code>"
    )


# =================== ADMIN CHECK ===================

@router.message(Command("admin"))
async def admin_command(message: Message, db: Database):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q!")
        return
    stats = await db.get_stats()
    text = (
        f"🛡 <b>Admin Panel</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total']}</b>\n"
        f"✅ Ro'yxatdan o'tganlar: <b>{stats['registered']}</b>\n"
        f"📋 Jami arizalar: <b>{stats['apps']}</b>\n"
        f"⏳ Kutayotgan arizalar: <b>{stats['pending_apps']}</b>\n"
        f"🟢 Bugun faol: <b>{stats['active_today']}</b>"
    )
    await send_admin_panel(message.bot, message.chat.id, text)


@router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    stats = await db.get_stats()
    text = (
        f"🛡 <b>Admin Panel</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total']}</b>\n"
        f"✅ Ro'yxatdan o'tganlar: <b>{stats['registered']}</b>\n"
        f"📋 Jami arizalar: <b>{stats['apps']}</b>\n"
        f"⏳ Kutayotgan arizalar: <b>{stats['pending_apps']}</b>\n"
        f"🟢 Bugun faol: <b>{stats['active_today']}</b>"
    )
    try:
        await call.message.delete()
    except Exception:
        pass
    await send_admin_panel(call.bot, call.message.chat.id, text)


# =================== STATISTICS ===================

@router.callback_query(F.data == "admin_stats")
async def admin_stats(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    stats = await db.get_stats()
    apps = await db.get_all_applications()

    course_count = {}
    for app in apps:
        c = app.get("course_name", "Noma'lum")
        course_count[c] = course_count.get(c, 0) + 1

    course_text = ""
    for c, n in sorted(course_count.items(), key=lambda x: -x[1])[:5]:
        course_text += f"  • {c}: <b>{n}</b>\n"

    pending = sum(1 for a in apps if a["status"] == "pending")
    accepted = sum(1 for a in apps if a["status"] == "accepted")
    rejected = sum(1 for a in apps if a["status"] == "rejected")

    text = (
        f"📊 <b>Batafsil Statistika</b>\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"  • Jami: <b>{stats['total']}</b>\n"
        f"  • Ro'yxatdan o'tgan: <b>{stats['registered']}</b>\n"
        f"  • Bugun faol: <b>{stats['active_today']}</b>\n\n"
        f"📋 <b>Arizalar:</b>\n"
        f"  • Jami: <b>{stats['apps']}</b>\n"
        f"  • ⏳ Kutayotgan: <b>{pending}</b>\n"
        f"  • ✅ Qabul: <b>{accepted}</b>\n"
        f"  • ❌ Rad: <b>{rejected}</b>\n\n"
        f"🏆 <b>Kurslar bo'yicha:</b>\n{course_text if course_text else '  Hali ariza yo&#39;q'}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
    ])
    await safe_render(call, text, reply_markup=kb)


# =================== USERS ===================

@router.callback_query(F.data == "admin_users")
async def admin_users(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await show_users_page(call, db, 0)


@router.callback_query(F.data.startswith("admin_users_page_"))
async def admin_users_page(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    offset = int(call.data.split("_")[-1])
    await show_users_page(call, db, offset)


async def show_users_page(call: CallbackQuery, db: Database, offset: int):
    users = await db.get_all_users()
    total = len(users)
    page_users = users[offset:offset + LIMIT]

    text = f"👥 <b>Foydalanuvchilar</b> ({offset + 1}–{min(offset + LIMIT, total)} / {total})\n\n"
    for u in page_users:
        reg = "✅" if u["is_registered"] else "🔴"
        uname = f"@{u['username']}" if u["username"] else "—"
        phone = u.get("phone") or "—"
        age = u.get("age") or "—"
        child = u.get("child_name")
        text += (
            f"{reg} <b>{u['full_name'] or 'Nomsiz'}</b>\n"
            f"   🆔 <code>{u['telegram_id']}</code> | 💬 {uname}\n"
            f"   📱 {phone} | 🎂 {age} yosh\n"
        )
        if child:
            text += f"   🧒 Farzand: {child}\n"
        text += f"   📅 {u['joined_at'][:10]}\n\n"

    await safe_render(call, text, reply_markup=admin_users_nav_kb(offset, total, LIMIT))


# =================== APPLICATIONS ===================

@router.callback_query(F.data == "admin_apps")
async def admin_applications(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    apps = await db.get_all_applications()
    pending = [a for a in apps if a["status"] == "pending"]

    if not pending:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")],
        ])
        await safe_render(call, "⏳ <b>Kutayotgan arizalar yo'q.</b>", reply_markup=kb)
        return

    app = pending[0]
    text = (
        f"📋 <b>Ariza #{app['id']}</b> ({pending.index(app) + 1}/{len(pending)})\n\n"
        f"👤 Ism: <b>{app.get('full_name', 'Nomsiz')}</b>\n"
        f"🆔 ID: <code>{app['user_id']}</code>\n"
        f"💬 Username: {('@' + app['username']) if app.get('username') else '—'}\n"
        f"📱 Telefon: {app.get('phone') or '—'}\n"
        f"📚 Kurs: <b>{app['course_name']}</b>\n"
        f"📅 Sana: {app['created_at'][:10]}"
    )

    await safe_render(call, text, reply_markup=admin_app_actions_kb(app['id'], app['user_id']))


@router.callback_query(F.data.startswith("app_accept_"))
async def accept_app(call: CallbackQuery, db: Database, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    parts = call.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    await db.update_application_status(app_id, "accepted")
    # Ariza qabul qilinganda o'quvchi avtomatik "to'lov qilmaganlar" ro'yxatiga tushadi
    await db.mark_paying_student(user_id)
    await call.answer("✅ Ariza qabul qilindi!", show_alert=True)

    try:
        await bot.send_message(
            user_id,
            "🎉 <b>Tabriklaymiz!</b>\n\n"
            "✅ Arizangiz <b>qabul qilindi!</b>\n\n"
            "📞 Tez orada o'qituvchimiz siz bilan bog'lanadi.\n\n"
            "🏫 BestEnglish o'quv markaziga xush kelibsiz!",
            reply_markup=back_to_menu_kb()
        )
    except Exception:
        pass

    await admin_applications(call, db)


@router.callback_query(F.data.startswith("app_reject_"))
async def reject_app(call: CallbackQuery, db: Database, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    parts = call.data.split("_")
    app_id = int(parts[2])
    user_id = int(parts[3])

    await db.update_application_status(app_id, "rejected")
    await call.answer("❌ Ariza rad etildi!", show_alert=True)

    try:
        await bot.send_message(
            user_id,
            "😔 <b>Arizangiz ko'rib chiqildi.</b>\n\n"
            "❌ Afsuski, hozircha arizangiz qabul qilinmadi.\n\n"
            f"📞 Batafsil ma'lumot uchun: {PAYMENT_CONTACT}\n\n"
            "🔄 Boshqa kursga yozilishingiz mumkin!",
            reply_markup=back_to_menu_kb()
        )
    except Exception:
        pass

    await admin_applications(call, db)


# =================== BROADCAST (umumiy xabar) ===================

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_message)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
    ])
    await safe_render(
        call,
        "📨 <b>Xabar yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:",
        reply_markup=kb
    )


@router.message(BroadcastState.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext, db: Database, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    users = await db.get_all_users()
    success = 0
    fail = 0

    status_msg = await message.answer(f"📨 Yuborilmoqda... 0/{len(users)}")

    for i, user in enumerate(users):
        try:
            await bot.send_message(user["telegram_id"], message.text)
            success += 1
        except Exception:
            fail += 1

        if (i + 1) % 10 == 0:
            try:
                await status_msg.edit_text(f"📨 Yuborilmoqda... {i + 1}/{len(users)}")
            except Exception:
                pass

    await state.clear()
    await status_msg.edit_text(
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"✅ Muvaffaqiyatli: {success}\n"
        f"❌ Yuborilmadi: {fail}"
    )
    await message.answer("🛡 Admin panel:", reply_markup=admin_panel_kb())


# =================== TO'LOV ESLATMASI (ota-onalarga) ===================

@router.callback_query(F.data == "admin_payment_reminder")
async def payment_reminder_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(PaymentReminderState.waiting_month)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
    ])
    await safe_render(
        call,
        "💳 <b>To'lov eslatmasi</b>\n\n"
        "Qaysi oy uchun eslatma yuborilsin? Oy nomini kiriting.\n"
        "Masalan: <code>Avgust</code>",
        reply_markup=kb
    )


@router.message(PaymentReminderState.waiting_month)
async def payment_reminder_preview(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    month = message.text.strip()
    await state.update_data(month=month)

    preview_text = build_payment_reminder_text(month)
    await message.answer(
        "👀 <b>Xabar shunday ko'rinishda yuboriladi:</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{preview_text}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Barcha ro'yxatdan o'tgan ota-onalarga yuborilsinmi?",
        reply_markup=payment_reminder_confirm_kb()
    )


@router.callback_query(F.data == "payment_reminder_send")
async def payment_reminder_send(call: CallbackQuery, state: FSMContext, db: Database, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    data = await state.get_data()
    month = data.get("month")
    if not month:
        await call.answer("Xatolik: oy tanlanmagan. Qaytadan urinib ko'ring.", show_alert=True)
        await state.clear()
        return

    text = build_payment_reminder_text(month)

    users = await db.get_registered_users()
    success = 0
    fail = 0

    status_msg = await call.message.edit_text(f"💳 Yuborilmoqda... 0/{len(users)}")

    for i, user in enumerate(users):
        try:
            await bot.send_message(user["telegram_id"], text)
            success += 1
        except Exception:
            fail += 1

        if (i + 1) % 10 == 0:
            try:
                await status_msg.edit_text(f"💳 Yuborilmoqda... {i + 1}/{len(users)}")
            except Exception:
                pass

    await state.clear()
    await status_msg.edit_text(
        f"✅ <b>To'lov eslatmasi yuborildi!</b>\n\n"
        f"✅ Muvaffaqiyatli: {success}\n"
        f"❌ Yuborilmadi: {fail}"
    )
    await call.message.answer("🛡 Admin panel:", reply_markup=admin_panel_kb())


# =================== TO'LOVLAR (yangi bo'lim) ===================

def _student_label(user: dict) -> str:
    return f"@{user['username']}" if user.get("username") else (user.get("full_name") or f"ID {user['telegram_id']}")


@router.callback_query(F.data == "admin_payments")
async def admin_payments(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await safe_render(
        call,
        "💰 <b>To'lovlar</b>\n\nBo'limni tanlang:",
        reply_markup=payments_menu_kb()
    )


@router.callback_query(F.data == "payments_unpaid")
async def payments_unpaid(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    students = await db.get_unpaid_students()
    if not students:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_payments")],
        ])
        await safe_render(call, "❌ <b>To'lov qilmaganlar yo'q.</b>", reply_markup=kb)
        return
    text = f"❌ <b>To'lov qilmaganlar</b> ({len(students)})\n\nO'quvchini tanlang:"
    await safe_render(call, text, reply_markup=payments_list_kb(students, "unpaid"))


@router.callback_query(F.data == "payments_paid")
async def payments_paid(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    students = await db.get_paid_students()
    if not students:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_payments")],
        ])
        await safe_render(call, "✅ <b>To'lov qilganlar yo'q.</b>", reply_markup=kb)
        return
    text = f"✅ <b>To'lov qilganlar</b> ({len(students)})\n\nO'quvchini tanlang:"
    await safe_render(call, text, reply_markup=payments_list_kb(students, "paid"))


@router.callback_query(F.data.startswith("unpaid_student_"))
async def unpaid_student_detail(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    telegram_id = int(call.data.replace("unpaid_student_", ""))
    user = await db.get_user(telegram_id)
    if not user:
        await call.answer("O'quvchi topilmadi.", show_alert=True)
        return
    label = _student_label(user)
    text = (
        f"👤 <b>{label}</b>\n\n"
        f"❌ <b>To'lov qilinmadi</b>\n\n"
        f"💳 Oylik to'lovni eslatib qo'ying: shu oy uchun to'lov hali amalga oshirilmagan.\n"
        f"Karta raqam: <code>{PAYMENT_CARD_NUMBER}</code>\n\n"
        f"To'lov qilingandan so'ng pastdagi tugmani bosing 👇"
    )
    await safe_render(call, text, reply_markup=unpaid_student_detail_kb(telegram_id))


@router.callback_query(F.data.startswith("paid_student_"))
async def paid_student_detail(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    telegram_id = int(call.data.replace("paid_student_", ""))
    user = await db.get_user(telegram_id)
    if not user:
        await call.answer("O'quvchi topilmadi.", show_alert=True)
        return
    label = _student_label(user)
    text = f"👤 <b>{label}</b>\n\n✅ <b>To'lov qilindi</b>"
    await safe_render(call, text, reply_markup=paid_student_detail_kb(telegram_id))


@router.callback_query(F.data.startswith("mark_paid_"))
async def mark_paid(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    telegram_id = int(call.data.replace("mark_paid_", ""))
    await db.set_payment_status(telegram_id, "paid")
    await call.answer("✅ To'lov qilindi deb belgilandi!", show_alert=True)
    await payments_unpaid(call, db)


@router.callback_query(F.data.startswith("mark_unpaid_"))
async def mark_unpaid(call: CallbackQuery, db: Database):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    telegram_id = int(call.data.replace("mark_unpaid_", ""))
    await db.set_payment_status(telegram_id, "unpaid")
    await call.answer("❌ Oylik to'lov bekor qilindi!", show_alert=True)
    await payments_paid(call, db)
