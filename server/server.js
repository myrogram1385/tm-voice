const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// سرو فایل‌های استاتیک
app.use(express.static(path.join(__dirname, '../client')));

// مدیریت اتصال Socket.io
io.on('connection', (socket) => {
  console.log('کاربر متصل شد:', socket.id);

  // پیوستن به اتاق
  socket.on('join-room', (roomId) => {
    socket.join(roomId);
    console.log(`کاربر ${socket.id} به اتاق ${roomId} پیوست`);
    
    // اطلاع به سایر کاربران اتاق
    socket.to(roomId).emit('user-connected', socket.id);
    
    // ارسال لیست کاربران موجود در اتاق
    const roomUsers = Array.from(io.sockets.adapter.rooms.get(roomId) || []);
    socket.emit('room-users', roomUsers);
  });

  // ارسال سیگنال WebRTC
  socket.on('signal', (data) => {
    socket.to(data.target).emit('signal', {
      sender: socket.id,
      signal: data.signal
    });
  });

  // قطع تماس
  socket.on('disconnect-call', (roomId) => {
    socket.to(roomId).emit('user-disconnected', socket.id);
  });

  // قطع اتصال
  socket.on('disconnect', () => {
    console.log('کاربر قطع شد:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`سرور در حال اجرا روی پورت ${PORT}`);
  console.log(`برای دسترسی: http://localhost:${PORT}`);
  console.log(`برای دسترسی از دستگاه دیگر: http://YOUR_IP:${PORT}`);
});
