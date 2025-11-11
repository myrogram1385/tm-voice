import logging
import json
import random
import string
import sqlite3
import time
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import re

# تنظیمات
BOT_TOKEN = "7663407390:AAEGjOwfIunYOXdz7PXBvbdegqzMaYaLW6U"
CHANNEL_ID = "5734726593"
DB_FILE = "users.db"
GMAIL_USER = 'myrogram@gmail.com'
GMAIL_PASSWORD = 'hehh mhko bber egkt'

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# دیکشنری‌های چندزبانه
LANGUAGES = {
    'fa': 'فارسی 🇮🇷',
    'en': 'English 🇺🇸', 
    'ar': 'العربية 🇸🇦',
    'ru': 'Русский 🇷🇺',
    'zh': '中文 🇨🇳',
    'ps': 'پښتو 🇦🇫'
}

# متون چندزبانه
TEXTS = {
    'fa': {
        'welcome': "🎯 *ربات کشاورز جیمیل*\n\nلطفاً یک زبان انتخاب کنید:",
        'main_menu': "🎯 *ربات کشاورز جیمیل*\n\nیک گزینه از منو انتخاب کنید:",
        'my_referrals': "👥 معرفی‌های من",
        'total_referrals': "📊 تعداد کل معرف‌ها: *{}*",
        'balance': "💰 موجودی",
        'current_balance': "💵 موجودی فعلی: *{}* سکه",
        'my_accounts': "📋 حساب‌های من",
        'no_accounts': "هنوز حسابی ثبت نشده است.",
        'account_item': "📍 *حساب {}*\n📧 ایمیل: `{}`\n🔐 رمز عبور: `{}`\n📅 تاریخ ثبت: {}",
        'register': "➕ ثبت جیمیل جدید",
        'register_instructions': "📧 *یک حساب جیمیل با اطلاعات مشخص شده ثبت کنید و 0.13$ تا 0.14$ دریافت کنید*\n\n👤 *نام:* `{}`\n👤 *نام خانوادگی:* {}\n📧 *ایمیل:* `{}`\n🔐 *رمز عبور:* `{}`\n\n🔐 *حتماً از اطلاعات مشخص شده استفاده کنید، در غیر این صورت حساب پرداخت نمی‌شود.*\n\n📝 **دستورالعمل‌های مهم:**\n1. حساب جیمیل را با اطلاعات بالا ایجاد کنید\n2. ایمیلی به `{}` با متن 'hi' ارسال کنید\n3. برای تأیید روی ✅ انجام شد کلیک کنید\n\n⚠️ *پس از ارسال ایمیل، روی ✅ انجام شد کلیک کنید*",
        'done': "✅ انجام شد",
        'cancel': "❌ لغو",
        'try_again': "🔄 تلاش مجدد",
        'verifying': "🔍 *در حال تأیید حساب جیمیل...*\n\nدر حال بررسی ارسال ایمیل 'hi'...",
        'verification_success': "✅ *حساب با موفقیت تأیید شد!*\n\n🎉 شما *1 سکه* دریافت کردید!\n📧 حساب: `{}`\n💰 موجودی جدید: *{} سکه*\n📢 اطلاعات به کانال ارسال شد\n\n📩 تأیید: {}",
        'verification_failed': "❌ *تأیید ناموفق!*\n\n📧 حساب: `{}`\n❌ خطا: {}\n\n📝 **لطفاً این مراحل را دنبال کنید:**\n1. مطمئن شوید حساب جیمیل را ایجاد کرده‌اید\n2. ایمیلی به `{}` با متن 'hi' ارسال کنید\n3. چند دقیقه برای تحویل ایمیل صبر کنید\n4. برای بررسی مجدد روی '🔄 تلاش مجدد' کلیک کنید\n\nاگر می‌خواهید لغو کنید، روی '❌ لغو' کلیک کنید",
        'no_pending_account': "❌ هیچ حساب در انتظار تأییدی وجود ندارد.",
        'registration_canceled': "❌ ثبت نام لغو شد.",
        'language_selected': "✅ زبان فارسی انتخاب شد.",
        'change_language': "🌐 تغییر زبان"
    },
    'en': {
        'welcome': "🎯 *Gmail Farmer Bot*\n\nPlease select a language:",
        'main_menu': "🎯 *Gmail Farmer Bot*\n\nSelect an option from the menu:",
        'my_referrals': "👥 My Referrals",
        'total_referrals': "📊 Total Referrals: *{}*",
        'balance': "💰 Balance", 
        'current_balance': "💵 Current Balance: *{}* coins",
        'my_accounts': "📋 My Accounts",
        'no_accounts': "No accounts registered yet.",
        'account_item': "📍 *Account {}*\n📧 Email: `{}`\n🔐 Password: `{}`\n📅 Registered: {}",
        'register': "➕ Register a new Gmail",
        'register_instructions': "📧 *Register a Gmail account using the specified data and get from 0.13$ to 0.14$*\n\n👤 *First name:* `{}`\n👤 *Last name:* {}\n📧 *Email:* `{}`\n🔐 *Password:* `{}`\n\n🔐 *Be sure to use the specified data, otherwise the account will not be paid.*\n\n📝 **Important Instructions:**\n1. Create the Gmail account with above data\n2. Send an email to `{}` with text 'hi'\n3. Click ✅ Done for verification\n\n⚠️ *After sending the email, click ✅ Done*",
        'done': "✅ Done",
        'cancel': "❌ Cancel", 
        'try_again': "🔄 Try Again",
        'verifying': "🔍 *Verifying Gmail account...*\n\nChecking if 'hi' email was sent...",
        'verification_success': "✅ *Account verified successfully!*\n\n🎉 You earned *1 coin*!\n📧 Account: `{}`\n💰 New Balance: *{} coins*\n📢 Information sent to channel\n\n📩 Verification: {}",
        'verification_failed': "❌ *Verification failed!*\n\n📧 Account: `{}`\n❌ Error: {}\n\n📝 **Please follow these steps:**\n1. Make sure you created the Gmail account\n2. Send an email to `{}` with text 'hi'\n3. Wait a few minutes for email delivery\n4. Click '🔄 Try Again' to re-check\n\nIf you want to cancel, click '❌ Cancel'",
        'no_pending_account': "❌ No pending account to verify.",
        'registration_canceled': "❌ Registration canceled.",
        'language_selected': "✅ English language selected.",
        'change_language': "🌐 Change Language"
    },
    'ar': {
        'welcome': "🎯 *بوت زراعة جيميل*\n\nيرجى اختيار لغة:",
        'main_menu': "🎯 *بوت زراعة جيميل*\n\nاختر خيارًا من القائمة:",
        'my_referrals': "👥 الإحالات الخاصة بي",
        'total_referrals': "📊 إجمالي الإحالات: *{}*",
        'balance': "💰 الرصيد",
        'current_balance': "💵 الرصيد الحالي: *{}* عملة",
        'my_accounts': "📋 حساباتي",
        'no_accounts': "لا توجد حسابات مسجلة بعد.",
        'account_item': "📍 *الحساب {}*\n📧 البريد الإلكتروني: `{}`\n🔐 كلمة المرور: `{}`\n📅 مسجل: {}",
        'register': "➕ تسجيل جيميل جديد",
        'register_instructions': "📧 *سجل حساب جيميل باستخدام البيانات المحددة واحصل على 0.13$ إلى 0.14$*\n\n👤 *الاسم الأول:* `{}`\n👤 *اسم العائلة:* {}\n📧 *البريد الإلكتروني:* `{}`\n🔐 *كلمة المرور:* `{}`\n\n🔐 *تأكد من استخدام البيانات المحددة، وإلا لن يتم دفع الحساب.*\n\n📝 **تعليمات مهمة:**\n1. أنشئ حساب جيميل بالبيانات أعلاه\n2. أرسل بريدًا إلكترونيًا إلى `{}` بالنص 'hi'\n3. انقر ✅ تم للتحقق\n\n⚠️ *بعد إرسال البريد الإلكتروني، انقر ✅ تم*",
        'done': "✅ تم",
        'cancel': "❌ إلغاء",
        'try_again': "🔄 حاول مرة أخرى",
        'verifying': "🔍 *جاري التحقق من حساب جيميل...*\n\nجاري التحقق من إرسال بريد 'hi'...",
        'verification_success': "✅ *تم التحقق من الحساب بنجاح!*\n\n🎉 لقد ربحت *1 عملة*!\n📧 الحساب: `{}`\n💰 الرصيد الجديد: *{} عملة*\n📢 تم إرسال المعلومات إلى القناة\n\n📩 التحقق: {}",
        'verification_failed': "❌ *فشل التحقق!*\n\n📧 الحساب: `{}`\n❌ خطأ: {}\n\n📝 **يرجى اتباع هذه الخطوات:**\n1. تأكد من إنشاء حساب جيميل\n2. أرسل بريدًا إلكترونيًا إلى `{}` بالنص 'hi'\n3. انتظر بضع دقائق لتسليم البريد الإلكتروني\n4. انقر '🔄 حاول مرة أخرى' لإعادة الفحص\n\nإذا كنت تريد الإلغاء، انقر '❌ إلغاء'",
        'no_pending_account': "❌ لا يوجد حساب معلق للتحقق.",
        'registration_canceled': "❌ تم إلغاء التسجيل.",
        'language_selected': "✅ تم اختيار اللغة العربية.",
        'change_language': "🌐 تغيير اللغة"
    },
    'ru': {
        'welcome': "🎯 *Gmail Фермер Бот*\n\nПожалуйста, выберите язык:",
        'main_menu': "🎯 *Gmail Фермер Бот*\n\nВыберите опцию из меню:",
        'my_referrals': "👥 Мои рефералы",
        'total_referrals': "📊 Всего рефералов: *{}*",
        'balance': "💰 Баланс",
        'current_balance': "💵 Текущий баланс: *{}* монет",
        'my_accounts': "📋 Мои аккаунты",
        'no_accounts': "Аккаунты еще не зарегистрированы.",
        'account_item': "📍 *Аккаунт {}*\n📧 Email: `{}`\n🔐 Пароль: `{}`\n📅 Зарегистрирован: {}",
        'register': "➕ Зарегистрировать новый Gmail",
        'register_instructions': "📧 *Зарегистрируйте аккаунт Gmail, используя указанные данные, и получите от 0.13$ до 0.14$*\n\n👤 *Имя:* `{}`\n👤 *Фамилия:* {}\n📧 *Email:* `{}`\n🔐 *Пароль:* `{}`\n\n🔐 *Обязательно используйте указанные данные, иначе аккаунт не будет оплачен.*\n\n📝 **Важные инструкции:**\n1. Создайте аккаунт Gmail с указанными данными\n2. Отправьте письмо на `{}` с текстом 'hi'\n3. Нажмите ✅ Готово для проверки\n\n⚠️ *После отправки письма нажмите ✅ Готово*",
        'done': "✅ Готово",
        'cancel': "❌ Отмена",
        'try_again': "🔄 Попробовать снова",
        'verifying': "🔍 *Проверка аккаунта Gmail...*\n\nПроверяем, было ли отправлено письмо 'hi'...",
        'verification_success': "✅ *Аккаунт успешно проверен!*\n\n🎉 Вы заработали *1 монету*!\n📧 Аккаунт: `{}`\n💰 Новый баланс: *{} монет*\n📢 Информация отправлена в канал\n\n📩 Проверка: {}",
        'verification_failed': "❌ *Проверка не удалась!*\n\n📧 Аккаунт: `{}`\n❌ Ошибка: {}\n\n📝 **Пожалуйста, выполните следующие шаги:**\n1. Убедитесь, что вы создали аккаунт Gmail\n2. Отправьте письмо на `{}` с текстом 'hi'\n3. Подождите несколько минут для доставки письма\n4. Нажмите '🔄 Попробовать снова' для повторной проверки\n\nЕсли вы хотите отменить, нажмите '❌ Отмена'",
        'no_pending_account': "❌ Нет аккаунтов, ожидающих проверки.",
        'registration_canceled': "❌ Регистрация отменена.",
        'language_selected': "✅ Выбран русский язык.",
        'change_language': "🌐 Изменить язык"
    },
    'zh': {
        'welcome': "🎯 *Gmail 农场机器人*\n\n请选择一种语言:",
        'main_menu': "🎯 *Gmail 农场机器人*\n\n从菜单中选择一个选项:",
        'my_referrals': "👥 我的推荐",
        'total_referrals': "📊 总推荐数: *{}*",
        'balance': "💰 余额",
        'current_balance': "💵 当前余额: *{}* 硬币",
        'my_accounts': "📋 我的账户",
        'no_accounts': "尚未注册任何账户。",
        'account_item': "📍 *账户 {}*\n📧 邮箱: `{}`\n🔐 密码: `{}`\n📅 注册时间: {}",
        'register': "➕ 注册新 Gmail",
        'register_instructions': "📧 *使用指定数据注册 Gmail 账户并获得 0.13$ 至 0.14$*\n\n👤 *名字:* `{}`\n👤 *姓氏:* {}\n📧 *邮箱:* `{}`\n🔐 *密码:* `{}`\n\n🔐 *请务必使用指定数据，否则账户将不会获得付款。*\n\n📝 **重要说明:**\n1. 使用以上数据创建 Gmail 账户\n2. 发送邮件至 `{}`，内容为 'hi'\n3. 点击 ✅ 完成进行验证\n\n⚠️ *发送邮件后，点击 ✅ 完成*",
        'done': "✅ 完成",
        'cancel': "❌ 取消",
        'try_again': "🔄 重试",
        'verifying': "🔍 *正在验证 Gmail 账户...*\n\n检查是否发送了 'hi' 邮件...",
        'verification_success': "✅ *账户验证成功!*\n\n🎉 您获得了 *1 硬币*!\n📧 账户: `{}`\n💰 新余额: *{} 硬币*\n📢 信息已发送到频道\n\n📩 验证: {}",
        'verification_failed': "❌ *验证失败!*\n\n📧 账户: `{}`\n❌ 错误: {}\n\n📝 **请遵循以下步骤:**\n1. 确保您已创建 Gmail 账户\n2. 发送邮件至 `{}`，内容为 'hi'\n3. 等待几分钟让邮件送达\n4. 点击 '🔄 重试' 重新检查\n\n如果您想取消，请点击 '❌ 取消'",
        'no_pending_account': "❌ 没有待验证的账户。",
        'registration_canceled': "❌ 注册已取消。",
        'language_selected': "✅ 已选择中文。",
        'change_language': "🌐 更改语言"
    },
    'ps': {
        'welcome': "🎯 *د جی میل کرېدونکی بوټ*\n\nځانته یوه ژبه وټاکئ:",
        'main_menu': "🎯 *د جی میل کرېدونکی بوټ*\n\nد مینو څخه یو اختیار غوره کړئ:",
        'my_referrals': "👥 زما راجعونې",
        'total_referrals': "📊 ټولې راجعونې: *{}*",
        'balance': "💰 بیلانس",
        'current_balance': "💵 اوسنی بیلانس: *{}* سکې",
        'my_accounts': "📋 زما حسابونه",
        'no_accounts': "تر اوسه هیڅ حساب ثبت شوی ندی.",
        'account_item': "📍 *حساب {}*\n📧 بریښنالیک: `{}`\n🔐 پاسورډ: `{}`\n📅 ثبت شوی: {}",
        'register': "➕ نوی جی میل ثبت کړئ",
        'register_instructions': "📧 *ټاکل شوي معلومات په کارولو سره د جی میل حساب ثبت کړئ او له 0.13$ څخه تر 0.14$ پورې ترلاسه کړئ*\n\n👤 *لومړی نوم:* `{}`\n👤 *وروستی نوم:* {}\n📧 *بریښنالیک:* `{}`\n🔐 *پاسورډ:* `{}`\n\n🔐 *ډاډ ترلاسه کړئ چې ټاکل شوي معلومات کاروئ، که نه نو حساب به نه ورکول کیږي.*\n\n📝 **مهم لارښوونې:**\n1. پورته معلوماتو سره د جی میل حساب جوړ کړئ\n2. 'hi' متن سره `{}` ته بریښنالیک واستوئ\n3. د تایید لپاره ✅ ترسره شو کلیک وکړئ\n\n⚠️ *بریښنالیک لیږلو وروسته، ✅ ترسره شو کلیک وکړئ*",
        'done': "✅ ترسره شو",
        'cancel': "❌ لغوه کړئ",
        'try_again': "🔄 بیا هڅه وکړئ",
        'verifying': "🔍 *د جی میل حساب تایید کېدی...*\n\nد 'hi' بریښنالیک لیږل تایید کېدی...",
        'verification_success': "✅ *حساب په بریالیتوب سره تایید شو!*\n\n🎉 تاسو *1 سکه* ترلاسه کړه!\n📧 حساب: `{}`\n💰 نوی بیلانس: *{} سکې*\n📢 معلومات چینل ته لیږل شول\n\n📩 تایید: {}",
        'verification_failed': "❌ *تایید ناکام شو!*\n\n📧 حساب: `{}`\n❌ تېروتنه: {}\n\n📝 **مهرباني وکړئ دا ګامونه تعقیب کړئ:**\n1. ډاډ ترلاسه کړئ چې تاسو د جی میل حساب جوړ کړی\n2. 'hi' متن سره `{}` ته بریښنالیک واستوئ\n3. د بریښنالیک د رسولو لپاره څو دقیقې انتظار وکړئ\n4. د بیا چک لپاره '🔄 بیا هڅه وکړئ' کلیک وکړئ\n\nکه تاسو لغوه کول غواړئ، '❌ لغوه کړئ' کلیک وکړئ",
        'no_pending_account': "❌ د تایید لپاره هیڅ حساب نشته.",
        'registration_canceled': "❌ ثبت لغوه شو.",
        'language_selected': "✅ پښتو ژبه وټاکل شوه.",
        'change_language': "🌐 ژبه بدله کړئ"
    }
}

class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                referrals INTEGER DEFAULT 0,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                email TEXT,
                password TEXT,
                first_name TEXT,
                last_name TEXT,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES users (chat_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_accounts (
                chat_id INTEGER PRIMARY KEY,
                email TEXT,
                password TEXT,
                first_name TEXT,
                last_name TEXT,
                verification_attempts INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user(self, chat_id):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute('INSERT INTO users (chat_id, balance, language) VALUES (?, ?, ?)', (chat_id, 0, 'en'))
            conn.commit()
            cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
            user = cursor.fetchone()
        
        conn.close()
        return user
    
    def get_user_language(self, chat_id):
        """دریافت زبان کاربر"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM users WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return result[0]
        return 'en'
    
    def update_user_language(self, chat_id, language):
        """به روزرسانی زبان کاربر"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET language = ? WHERE chat_id = ?', (language, chat_id))
        conn.commit()
        conn.close()
    
    def update_balance(self, chat_id, amount):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET balance = balance + ? WHERE chat_id = ?', (amount, chat_id))
        conn.commit()
        conn.close()
    
    def save_pending_account(self, chat_id, account_data):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO pending_accounts 
            (chat_id, email, password, first_name, last_name, verification_attempts) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            chat_id, 
            account_data['email'], 
            account_data['password'], 
            account_data['first_name'], 
            account_data['last_name'],
            0
        ))
        
        conn.commit()
        conn.close()
    
    def get_pending_account(self, chat_id):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pending_accounts WHERE chat_id = ?', (chat_id,))
        account = cursor.fetchone()
        
        conn.close()
        
        if account:
            return {
                'chat_id': account[0],
                'email': account[1],
                'password': account[2],
                'first_name': account[3],
                'last_name': account[4],
                'verification_attempts': account[5],
                'created_at': account[6]
            }
        return None
    
    def delete_pending_account(self, chat_id):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pending_accounts WHERE chat_id = ?', (chat_id,))
        conn.commit()
        conn.close()
    
    def increment_verification_attempts(self, chat_id):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE pending_accounts 
            SET verification_attempts = verification_attempts + 1 
            WHERE chat_id = ?
        ''', (chat_id,))
        conn.commit()
        conn.close()
    
    def save_verified_account(self, chat_id, account_data):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO accounts (chat_id, email, password, first_name, last_name, verified)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            chat_id, 
            account_data['email'], 
            account_data['password'],
            account_data['first_name'], 
            account_data['last_name'], 
            True
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_accounts(self, chat_id):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, password, first_name, last_name, created_at 
            FROM accounts 
            WHERE chat_id = ? 
            ORDER BY created_at DESC
        ''', (chat_id,))
        
        accounts = cursor.fetchall()
        conn.close()
        return accounts

class EmailChecker:
    def __init__(self, gmail_user, gmail_password):
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password
    
    def connect_to_gmail(self):
        """اتصال به جیمیل"""
        try:
            import imaplib
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
            self.mail.login(self.gmail_user, self.gmail_password)
            return True
        except Exception as e:
            logging.error(f"❌ خطا در اتصال به جیمیل: {e}")
            return False
    
    def check_hi_email_received(self, target_email):
        """بررسی آیا ایمیل 'hi' از ایمیل مشخص شده دریافت شده است"""
        try:
            if not self.connect_to_gmail():
                return {'success': False, 'message': 'Cannot connect to Gmail'}
            
            self.mail.select('inbox')
            
            # جستجو برای ایمیل‌های از فرستنده مشخص
            status, messages = self.mail.search(None, f'FROM "{target_email}"')
            email_ids = messages[0].split()
            
            if not email_ids:
                return {'success': False, 'message': f'No emails found from {target_email}'}
            
            # بررسی همه ایمیل‌های از این فرستنده
            for email_id in email_ids[-5:]:  # فقط 5 ایمیل آخر را چک کن
                import email
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                # استخراج متن ایمیل
                body = self._get_email_body(msg)
                
                # بررسی اگر متن ایمیل شامل 'hi' باشد
                if 'hi' in body.lower():
                    return {
                        'success': True, 
                        'message': 'Verification successful - hi email found',
                        'email_body': body[:200]
                    }
            
            return {'success': False, 'message': 'No hi email found from this sender'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error checking email: {str(e)}'}
        finally:
            self.close_connection()
    
    def _get_email_body(self, msg):
        """استخراج متن ایمیل"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                        break
                    except:
                        pass
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', 'ignore')
                except:
                    pass
        return body.strip()
    
    def close_connection(self):
        """بستن اتصال"""
        try:
            self.mail.close()
            self.mail.logout()
        except:
            pass

class GmailVerifier:
    def __init__(self):
        self.email_checker = EmailChecker(GMAIL_USER, GMAIL_PASSWORD)
    
    @staticmethod
    def generate_random_string(length=15):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_random_email():
        return GmailVerifier.generate_random_string(15) + '@gmail.com'
    
    @staticmethod
    def generate_random_password(length=12):
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        
        password = [
            random.choice(uppercase),
            random.choice(digits),
            random.choice(lowercase)
        ]
        
        all_chars = uppercase + lowercase + digits
        password.extend(random.choice(all_chars) for _ in range(length - 3))
        
        random.shuffle(password)
        return ''.join(password)
    
    def verify_gmail_with_hi_email(self, user_email):
        """
        بررسی آیا ایمیل 'hi' از کاربر به ایمیل مشخص شده ارسال شده است
        """
        try:
            verification_result = self.email_checker.check_hi_email_received(user_email)
            return verification_result
            
        except Exception as e:
            return {'success': False, 'message': f'Verification error: {str(e)}'}

class TelegramBot:
    def __init__(self):
        self.db = Database()
        self.verifier = GmailVerifier()
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_handler))
        self.application.add_handler(CommandHandler("language", self.language_handler))
        self.application.add_handler(CallbackQueryHandler(self.language_callback_handler, pattern="^lang_"))
        
        # هندلرهای پیام‌های متنی
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_message_handler))
    
    def get_user_text(self, chat_id, text_key, *format_args):
        """دریافت متن مناسب بر اساس زبان کاربر"""
        language = self.db.get_user_language(chat_id)
        text = TEXTS.get(language, TEXTS['en']).get(text_key, TEXTS['en'].get(text_key, text_key))
        if format_args:
            return text.format(*format_args)
        return text
    
    async def send_message(self, chat_id, text, reply_markup=None, parse_mode='Markdown'):
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Error sending message: {e}")
    
    async def send_to_channel(self, account_data, user_chat_id):
        message = f"✅ *New Gmail Account Created*\n\n"
        message += f"👤 User ID: `{user_chat_id}`\n"
        message += f"📧 Email: `{account_data['email']}`\n"
        message += f"🔐 Password: `{account_data['password']}`\n"
        message += f"👤 First Name: `{account_data['first_name']}`\n"
        message += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await self.send_message(CHANNEL_ID, message)
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = self.db.get_user(chat_id)
        
        # اگر کاربر زبان انتخاب نکرده باشد، صفحه انتخاب زبان نشان داده شود
        language = self.db.get_user_language(chat_id)
        if language == 'en':  # زبان پیش‌فرض
            await self.show_language_selection(chat_id)
        else:
            await self.show_main_menu(chat_id)
    
    async def language_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await self.show_language_selection(chat_id)
    
    async def language_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        language = query.data.replace('lang_', '')
        
        if language in LANGUAGES:
            self.db.update_user_language(chat_id, language)
            await query.edit_message_text(
                self.get_user_text(chat_id, 'language_selected')
            )
            await self.show_main_menu(chat_id)
    
    async def show_language_selection(self, chat_id):
        keyboard = []
        for lang_code, lang_name in LANGUAGES.items():
            keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self.send_message(chat_id, self.get_user_text(chat_id, 'welcome'), reply_markup)
    
    async def show_main_menu(self, chat_id):
        keyboard = [
            [
                KeyboardButton(self.get_user_text(chat_id, 'my_referrals')), 
                KeyboardButton(self.get_user_text(chat_id, 'balance'))
            ],
            [
                KeyboardButton(self.get_user_text(chat_id, 'my_accounts')), 
                KeyboardButton(self.get_user_text(chat_id, 'register'))
            ],
            [
                KeyboardButton(self.get_user_text(chat_id, 'change_language'))
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await self.send_message(
            chat_id,
            self.get_user_text(chat_id, 'main_menu'),
            reply_markup
        )
    
    async def text_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = update.message.text
        
        # تشخیص نوع پیام بر اساس متن
        if text == self.get_user_text(chat_id, 'my_referrals'):
            await self.referrals_handler(update, context)
        elif text == self.get_user_text(chat_id, 'balance'):
            await self.balance_handler(update, context)
        elif text == self.get_user_text(chat_id, 'my_accounts'):
            await self.accounts_handler(update, context)
        elif text == self.get_user_text(chat_id, 'register'):
            await self.register_handler(update, context)
        elif text == self.get_user_text(chat_id, 'done'):
            await self.verify_handler(update, context)
        elif text == self.get_user_text(chat_id, 'cancel'):
            await self.cancel_handler(update, context)
        elif text == self.get_user_text(chat_id, 'try_again'):
            await self.try_again_handler(update, context)
        elif text == self.get_user_text(chat_id, 'change_language'):
            await self.language_handler(update, context)
        else:
            await self.show_main_menu(chat_id)
    
    async def referrals_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = self.db.get_user(chat_id)
        await self.send_message(
            chat_id, 
            f"{self.get_user_text(chat_id, 'my_referrals')}\n\n{self.get_user_text(chat_id, 'total_referrals', user[2])}"
        )
    
    async def balance_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = self.db.get_user(chat_id)
        await self.send_message(
            chat_id, 
            f"{self.get_user_text(chat_id, 'balance')}\n\n{self.get_user_text(chat_id, 'current_balance', user[1])}"
        )
    
    async def accounts_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        accounts = self.db.get_user_accounts(chat_id)
        
        if not accounts:
            text = f"{self.get_user_text(chat_id, 'my_accounts')}\n\n{self.get_user_text(chat_id, 'no_accounts')}"
        else:
            text = f"{self.get_user_text(chat_id, 'my_accounts')}\n\n"
            for i, account in enumerate(accounts, 1):
                text += self.get_user_text(chat_id, 'account_item', i, account[0], account[1], account[4]) + "\n\n"
        
        await self.send_message(chat_id, text)
    
    async def register_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        
        account_data = {
            'first_name': self.verifier.generate_random_string(15),
            'last_name': "✖️",
            'email': self.verifier.generate_random_email(),
            'password': self.verifier.generate_random_password()
        }
        
        self.db.save_pending_account(chat_id, account_data)
        
        message = self.get_user_text(
            chat_id, 
            'register_instructions', 
            account_data['first_name'],
            account_data['last_name'],
            account_data['email'],
            account_data['password'],
            GMAIL_USER
        )
        
        keyboard = [
            [
                KeyboardButton(self.get_user_text(chat_id, 'done')), 
                KeyboardButton(self.get_user_text(chat_id, 'cancel'))
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await self.send_message(chat_id, message, reply_markup)
    
    async def verify_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        pending_account = self.db.get_pending_account(chat_id)
        
        if not pending_account:
            await self.send_message(chat_id, self.get_user_text(chat_id, 'no_pending_account'))
            return
        
        await self.send_message(chat_id, self.get_user_text(chat_id, 'verifying'))
        
        # بررسی آیا ایمیل 'hi' ارسال شده است
        verification_result = self.verifier.verify_gmail_with_hi_email(pending_account['email'])
        
        if verification_result['success']:
            # موفقیت آمیز - ایمیل hi پیدا شد
            self.db.save_verified_account(chat_id, pending_account)
            self.db.update_balance(chat_id, 1)
            self.db.delete_pending_account(chat_id)
            
            await self.send_to_channel(pending_account, chat_id)
            
            user = self.db.get_user(chat_id)
            success_message = self.get_user_text(
                chat_id,
                'verification_success',
                pending_account['email'],
                user[1],
                verification_result['message']
            )
            
            await self.send_message(chat_id, success_message)
            await self.show_main_menu(chat_id)
            
        else:
            # ایمیل hi پیدا نشد
            self.db.increment_verification_attempts(chat_id)
            
            error_message = self.get_user_text(
                chat_id,
                'verification_failed',
                pending_account['email'],
                verification_result['message'],
                GMAIL_USER
            )
            
            keyboard = [
                [
                    KeyboardButton(self.get_user_text(chat_id, 'try_again')), 
                    KeyboardButton(self.get_user_text(chat_id, 'cancel'))
                ]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            
            await self.send_message(chat_id, error_message, reply_markup)
    
    async def try_again_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """هندلر برای دکمه Try Again"""
        await self.verify_handler(update, context)
    
    async def cancel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.db.delete_pending_account(chat_id)
        await self.send_message(chat_id, self.get_user_text(chat_id, 'registration_canceled'))
        await self.show_main_menu(chat_id)
    
    def run(self):
        print("🤖 Bot is starting...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()