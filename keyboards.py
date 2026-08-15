from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# =================== MAIN MENU ===================

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📚 Kurslar", callback_data="courses"),
            InlineKeyboardButton(text="📋 Arizalarim", callback_data="my_apps"),
        ],
        [
            InlineKeyboardButton(text="✍️ Kursga yozilish", callback_data="enroll"),
        ],
        [
            InlineKeyboardButton(text="🏫 Biz haqimizda", callback_data="about"),
            InlineKeyboardButton(text="📞 Bog'lanish", callback_data="contact"),
        ],
    ])


# =================== COURSES (BROWSE — faqat ko'rish, ariza yo'q) ===================
# 4 ta yo'nalish: Ona tili, Ingliz tili, Ingliz tili (Kids), Ingliz tili (Grammatika)
# Bu bo'limda fanlar faqat ko'rsatiladi — yozilish tugmasi yo'q.

def courses_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Ona tili", callback_data="course_onatili")],
        [InlineKeyboardButton(text="🇬🇧 Ingliz tili", callback_data="course_ingliz")],
        [InlineKeyboardButton(text="🧒 Ingliz tili (Kids)", callback_data="course_ingliz_kids")],
        [InlineKeyboardButton(text="✏️ Ingliz tili (Grammatika)", callback_data="course_ingliz_grammar")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")],
    ])


# Fan tavsifidan keyin faqat "Orqaga" tugmasi — yozilish tugmasi yo'q
def back_to_courses_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="courses")],
    ])


# =================== COURSES (ENROLL — «Kursga yozilish» oqimi uchun) ===================

def enroll_courses_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Ona tili", callback_data="enroll_onatili")],
        [InlineKeyboardButton(text="🅰️ Ingliz tili (CEFR)", callback_data="enroll_ingliz_cefr")],
        [InlineKeyboardButton(text="🎓 Ingliz tili (IELTS)", callback_data="enroll_ingliz_ielts")],
        [InlineKeyboardButton(text="🧒 Ingliz tili (Kids)", callback_data="enroll_ingliz_kids")],
        [InlineKeyboardButton(text="✏️ Ingliz tili (Grammatika)", callback_data="enroll_ingliz_grammar")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")],
    ])


# =================== ENROLL ===================

def enroll_confirm_kb(course: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, yozilaman!", callback_data=f"confirm_enroll_{course}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="main_menu")],
    ])


def after_enroll_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Arizalarim", callback_data="my_apps")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
    ])


# =================== CONTACT ===================

def contact_kb() -> InlineKeyboardMarkup:
    from config import ACADEMIA_TELEGRAM
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Telegram", url=f"https://t.me/{ACADEMIA_TELEGRAM.lstrip('@')}"),
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")],
    ])


def phone_share_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# =================== BACK ===================

def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
    ])


# =================== ADMIN ===================

def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton(text="📋 Arizalar", callback_data="admin_apps"),
            InlineKeyboardButton(text="📨 Xabar yuborish", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton(text="💳 To'lov eslatmasi", callback_data="admin_payment_reminder"),
            InlineKeyboardButton(text="💰 To'lovlar", callback_data="admin_payments"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu"),
        ],
    ])


def admin_app_actions_kb(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Qabul", callback_data=f"app_accept_{app_id}_{user_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"app_reject_{app_id}_{user_id}"),
        ],
        # Orqaga tugmasi admin panelga qaytaradi (arizalar ro'yxatiga emas —
        # avval shu yerga qaytishda "xabar o'zgarmagan" xatoligi tugma ishlamayotgandek ko'rsatardi)
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")],
    ])


def admin_users_nav_kb(offset: int, total: int, limit: int = 5) -> InlineKeyboardMarkup:
    buttons = []
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"admin_users_page_{offset - limit}"))
    if offset + limit < total:
        nav.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"admin_users_page_{offset + limit}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_reminder_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Barchaga yuborish", callback_data="payment_reminder_send")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")],
    ])


# =================== TO'LOVLAR (yangi bo'lim) ===================

def payments_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ To'lov qilganlar", callback_data="payments_paid")],
        [InlineKeyboardButton(text="❌ To'lov qilmaganlar", callback_data="payments_unpaid")],
        [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")],
    ])


def payments_list_kb(students, list_type: str) -> InlineKeyboardMarkup:
    """list_type: 'unpaid' yoki 'paid' — o'quvchilar ro'yxati, faqat username bilan"""
    buttons = []
    for s in students:
        label = f"@{s['username']}" if s.get("username") else (s.get("full_name") or f"ID {s['telegram_id']}")
        buttons.append([InlineKeyboardButton(
            text=label,
            callback_data=f"{list_type}_student_{s['telegram_id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_payments")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def unpaid_student_detail_kb(telegram_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ To'lov qilindi", callback_data=f"mark_paid_{telegram_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="payments_unpaid")],
    ])


def paid_student_detail_kb(telegram_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Oylik to'lovni bekor qilish", callback_data=f"mark_unpaid_{telegram_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="payments_paid")],
    ])
