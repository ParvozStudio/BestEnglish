from aiogram.types import CallbackQuery


async def safe_edit(call: CallbackQuery, text: str, reply_markup=None):
    """
    call.message har doim ham matnli bo'lavermaydi (masalan, bosh menyu yoki
    "Biz haqimizda" rasm/video bilan yuboriladi). Bunday xabarlarni edit_text
    bilan o'zgartirib bo'lmaydi — Telegram xatolik qaytaradi va tugma
    "ishlamayotgandek" ko'rinadi. Shu sabab avval oddiy tahrirlashga
    urinamiz, ishlamasa xabarni o'chirib, o'rniga yangi matnli xabar yuboramiz.
    """
    try:
        await call.message.edit_text(text, reply_markup=reply_markup)
    except Exception:
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer(text, reply_markup=reply_markup)
