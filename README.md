# 🎓 BestEnglish — Telegram Bot

> Ota-onalar uchun BestEnglish o'quv markazi Telegram boti

## 🚀 Tezkor ishga tushirish

```bash
# 1. Kutubxonalar o'rnatish
pip install -r requirements.txt

# 2. config.py faylini oching va BOT_TOKEN, ADMIN_IDS ni kiriting

# 3. Botni ishga tushirish
python bot.py
```

## ⚙️ Sozlash

`.env` fayl kerak emas — barcha sozlamalar to'g'ridan-to'g'ri **`config.py`** faylida:

```python
BOT_TOKEN = "sizning_bot_tokeningiz"
ADMIN_IDS = [sizning_telegram_id_ingiz]
```

> **Bot token olish:** @BotFather → /newbot
> **Telegram ID olish:** @userinfobot

Bir nechta admin bo'lsa, ro'yxatga qo'shing: `ADMIN_IDS = [111111, 222222]`

## 📋 Asosiy buyruqlar

| Buyruq | Tavsif |
|--------|--------|
| /start | Botni ishga tushirish |
| /menu  | Bosh menyu |
| /courses | Kurslar ro'yxati |
| /myapps | Mening arizalarim |
| /admin | Admin panel (faqat adminlar) |
| /help  | Yordam |

## 📚 Kurslar

- 📖 **Ona tili**
- 🇬🇧 **Ingliz tili** — bosilganda faqat **CEFR** yoki **IELTS** yo'nalishini tanlash chiqadi
- 🧒 **Ingliz tili (Kids)** — bolalar uchun, yo'nalish tanlash yo'q

## 🛡 Admin Panel

`/admin` buyrug'i orqali:
- 📊 Statistika
- 👥 Foydalanuvchilar ro'yxati (farzand ismi bilan)
- 📋 Arizalarni boshqarish (qabul/rad)
- 📨 Barcha foydalanuvchilarga umumiy xabar (broadcast)
- 💳 **To'lov eslatmasi** — ota-onalarga oylik to'lov haqida eslatma yuborish:
  1. "💳 To'lov eslatmasi" tugmasini bosing
  2. Oy nomini kiriting (masalan: `Avgust`)
  3. Xabar ko'rinishini tasdiqlang — barcha ro'yxatdan o'tgan foydalanuvchilarga avtomatik yuboriladi

Karta raqami va murojaat kontakti `config.py` faylida (`PAYMENT_CARD_NUMBER`, `PAYMENT_CONTACT`, `PAYMENT_DEADLINE_DAY`) sozlanadi.

## 🏗 Tuzilma

```
bestenglish_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Sozlamalar (token, admin, to'lov ma'lumotlari)
├── database/db.py      # Ma'lumotlar bazasi
├── handlers/           # Barcha handlerlar (start, courses, register, admin...)
├── keyboards/          # Tugmalar
└── middlewares/        # Middleware (foydalanuvchi kuzatish)
```

## 📞 Bog'lanish

- Telegram: @Best_English202444
