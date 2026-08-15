# =========================================================
# SOZLAMALAR — bu yerga o'zingizning ma'lumotlaringizni kiriting
# (python-dotenv talab qilinmaydi, hammasi shu faylda)
# =========================================================

import os

# BotFather'dan olgan tokeningiz.
# Railway'da "Variables" bo'limiga BOT_TOKEN qo'shsangiz, o'shani ishlatadi.
# Aks holda pastdagi standart qiymatni ishlatadi.
BOT_TOKEN = os.environ.get(
    "BOT_TOKEN",
    "8875699133:AAGJ6PaH7-qHIJVDgySu5iOQnasld1XAbU4"
)

# Sizning Telegram ID'ingiz (@userinfobot orqali oling)
# Bir nechta admin bo'lsa, vergul bilan ajrating: [111111, 222222]
ADMIN_IDS = [8319291440, 906094470, 935820520]

# BestEnglish ma'lumotlari
ACADEMIA_NAME = "🎓 BestEnglish"
ACADEMIA_PHONE = "+998 97 154 19 77"
ACADEMIA_ADDRESS = "Manzilingizni shu yerga kiriting"
ACADEMIA_TELEGRAM = "@Best_English202444"

# To'lov ma'lumotlari (to'lov eslatmasi uchun)
PAYMENT_CARD_NUMBER = "6262 5700 5545 4153"
PAYMENT_CONTACT = "@Best_English202444"
PAYMENT_DEADLINE_DAY = "15"

DB_PATH = "bestenglish.db"
