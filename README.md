# tm-voice
سیستم تماس صوتی با WebRTC و Socket.io - ساخت ایران


# تماس صوتی WebRTC

یک برنامه تماس صوتی کامل با WebRTC شبیه به تلگرام که امکان برقراری تماس مستقیم بین دو کاربر را فراهم می‌کند.

## ویژگی‌ها

- ✅ تماس صوتی Real-time با WebRTC
- ✅ ارتباط مستقیم P2P بین کاربران
- ✅ رابط کاربری فارسی و ریسپانسیو
- ✅ مدیریت اتاق‌های تماس
- ✅ کنترل‌های تماس (موت، بلندگو، پایان تماس)
- ✅ تایمر تماس
- ✅ پشتیبانی از Termux

## نصب و راه‌اندازی

### پیش‌نیازها

- Node.js (ورژن 14 یا بالاتر)
- مرورگر مدرن (پشتیبانی از WebRTC)

### نصب در Termux

```bash
# آپدیت پکیج‌ها
pkg update && pkg upgrade

# نصب Node.js
pkg install nodejs

# نصب git
pkg install git

# کلون پروژه
git clone [آدرس ریپوی شما]
cd webrtc-audio-call

# نصب dependencies
cd server
npm install

# راه‌اندازی سرور
npm start
