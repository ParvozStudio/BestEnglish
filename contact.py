from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import contact_kb, back_to_menu_kb
from utils import safe_edit


router = Router()


def contact_text() -> str:
    import config
    phone = getattr(config, "ACADEMIA_PHONE", "Kiritilmagan")
    telegram = getattr(config, "ACADEMIA_TELEGRAM", "Kiritilmagan")
    address = getattr(config, "ACADEMIA_ADDRESS", "Kiritilmagan")
    return f"""
📞 <b>Bog'lanish</b>

━━━━━━━━━━━━━━━━━━━━
📱 <b>Telefon:</b> <code>{phone}</code>
💬 <b>Telegram:</b> {telegram}

━━━━━━━━━━━━━━━━━━━━
📍 <b>Manzil:</b>
{address}

━━━━━━━━━━━━━━━━━━━━
💡 <i>Qo'ng'iroq qiling yoki Telegramda yozing —
biz sizni kutamiz!</i>
    """


@router.callback_query(F.data == "contact")
async def show_contact(call: CallbackQuery):
    await safe_edit(call, contact_text(), reply_markup=contact_kb())
