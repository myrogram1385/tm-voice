class WebRTCAudioCall {
    constructor() {
        this.socket = null;
        this.localStream = null;
        this.peerConnections = {};
        this.roomId = null;
        this.isMuted = false;
        this.isSpeakerOn = true;
        this.callStartTime = null;
        this.timerInterval = null;
        
        this.initializeElements();
        this.setupEventListeners();
    }

    initializeElements() {
        this.connectionPanel = document.getElementById('connectionPanel');
        this.callPanel = document.getElementById('callPanel');
        this.roomInput = document.getElementById('roomInput');
        this.joinBtn = document.getElementById('joinBtn');
        this.usersList = document.getElementById('usersList');
        this.status = document.getElementById('status');
        this.timer = document.getElementById('timer');
        this.muteBtn = document.getElementById('muteBtn');
        this.endCallBtn = document.getElementById('endCallBtn');
        this.speakerBtn = document.getElementById('speakerBtn');
        this.remoteAudio = document.getElementById('remoteAudio');
        this.localAudio = document.getElementById('localAudio');
    }

    setupEventListeners() {
        this.joinBtn.addEventListener('click', () => this.joinRoom());
        this.muteBtn.addEventListener('click', () => this.toggleMute());
        this.endCallBtn.addEventListener('click', () => this.endCall());
        this.speakerBtn.addEventListener('click', () => this.toggleSpeaker());
        
        // Enter key برای اتاق
        this.roomInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.joinRoom();
        });
    }

    async joinRoom() {
        const roomId = this.roomInput.value.trim();
        if (!roomId) {
            alert('لطفاً شناسه اتاق را وارد کنید');
            return;
        }

        this.roomId = roomId;
        this.joinBtn.disabled = true;
        this.joinBtn.textContent = 'در حال اتصال...';

        try {
            await this.initializeSocket();
            await this.initializeMedia();
            this.socket.emit('join-room', roomId);
        } catch (error) {
            console.error('خطا در اتصال:', error);
            alert('خطا در برقراری ارتباط');
            this.joinBtn.disabled = false;
            this.joinBtn.textContent = 'ورود به اتاق';
        }
    }

    initializeSocket() {
        return new Promise((resolve) => {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('متصل به سرور شد');
                resolve();
            });

            this.socket.on('room-users', (users) => {
                this.updateUsersList(users);
                users.forEach(userId => {
                    if (userId !== this.socket.id) {
                        this.createPeerConnection(userId);
                    }
                });
            });

            this.socket.on('user-connected', (userId) => {
                this.addUserToList(userId);
                this.createPeerConnection(userId);
            });

            this.socket.on('user-disconnected', (userId) => {
                this.removeUserFromList(userId);
                if (this.peerConnections[userId]) {
                    this.peerConnections[userId].close();
                    delete this.peerConnections[userId];
                }
            });

            this.socket.on('signal', async (data) => {
                await this.handleSignal(data.sender, data.signal);
            });
        });
    }

    async initializeMedia() {
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                },
                video: false
            });
            
            // نمایش استریم محلی (برای دیباگ)
            this.localAudio.srcObject = this.localStream;
        } catch (error) {
            console.error('خطا در دسترسی به میکروفون:', error);
            throw new Error('دسترسی به میکروفون ممکن نیست');
        }
    }

    createPeerConnection(userId) {
        if (this.peerConnections[userId]) return;

        const peerConnection = new RTCPeerConnection({
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        });

        // اضافه کردن استریم محلی
        this.localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, this.localStream);
        });

        // دریافت استریم ریموت
        peerConnection.ontrack = (event) => {
            console.log('دریافت استریم ریموت از:', userId);
            this.remoteAudio.srcObject = event.streams[0];
            this.startCall();
        };

        // مدیریت ICE candidates
        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.socket.emit('signal', {
                    target: userId,
                    signal: {
                        type: 'ice-candidate',
                        candidate: event.candidate
                    }
                });
            }
        };

        this.peerConnections[userId] = peerConnection;

        // ایجاد offer
        this.createOffer(userId);
    }

    async createOffer(userId) {
        try {
            const offer = await this.peerConnections[userId].createOffer();
            await this.peerConnections[userId].setLocalDescription(offer);
            
            this.socket.emit('signal', {
                target: userId,
                signal: offer
            });
        } catch (error) {
            console.error('خطا در ایجاد offer:', error);
        }
    }

    async handleSignal(senderId, signal) {
        const peerConnection = this.peerConnections[senderId];
        if (!peerConnection) return;

        try {
            if (signal.type === 'offer') {
                await peerConnection.setRemoteDescription(signal);
                const answer = await peerConnection.createAnswer();
                await peerConnection.setLocalDescription(answer);
                
                this.socket.emit('signal', {
                    target: senderId,
                    signal: answer
                });
            } else if (signal.type === 'answer') {
                await peerConnection.setRemoteDescription(signal);
            } else if (signal.type === 'ice-candidate') {
                await peerConnection.addIceCandidate(signal.candidate);
            }
        } catch (error) {
            console.error('خطا در مدیریت سیگنال:', error);
        }
    }

    updateUsersList(users) {
        this.usersList.innerHTML = '';
        users.forEach(userId => this.addUserToList(userId));
    }

    addUserToList(userId) {
        const li = document.createElement('li');
        li.innerHTML = `👤 کاربر ${userId.substring(0, 8)}...`;
        li.dataset.userId = userId;
        this.usersList.appendChild(li);
    }

    removeUserFromList(userId) {
        const userItem = this.usersList.querySelector(`[data-user-id="${userId}"]`);
        if (userItem) {
            userItem.remove();
        }
    }

    startCall() {
        this.connectionPanel.classList.add('hidden');
        this.callPanel.classList.remove('hidden');
        this.status.textContent = '🔊 در حال تماس';
        this.status.className = 'status connected';
        
        this.callStartTime = Date.now();
        this.startTimer();
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.callStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
            const seconds = (elapsed % 60).toString().padStart(2, '0');
            this.timer.textContent = `${minutes}:${seconds}`;
        }, 1000);
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        this.localStream.getAudioTracks().forEach(track => {
            track.enabled = !this.isMuted;
        });
        
        this.muteBtn.textContent = this.isMuted ? '🔈 صدا دار' : '🔇 بی‌صدا';
        this.muteBtn.style.background = this.isMuted ? '#ffeb3b' : '#f1f3f4';
    }

    toggleSpeaker() {
        this.isSpeakerOn = !this.isSpeakerOn;
        this.remoteAudio.volume = this.isSpeakerOn ? 1 : 0;
        this.speakerBtn.textContent = this.isSpeakerOn ? '🔇 بی‌صدا' : '🔊 بلندگو';
        this.speakerBtn.style.background = this.isSpeakerOn ? '#f1f3f4' : '#ffeb3b';
    }

    endCall() {
        // قطع تمام اتصالات
        Object.values(this.peerConnections).forEach(pc => pc.close());
        this.peerConnections = {};
        
        // توقف استریم محلی
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }
        
        // پاک کردن تایمر
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        // اطلاع به سرور
        if (this.socket && this.roomId) {
            this.socket.emit('disconnect-call', this.roomId);
        }
        
        // بازگشت به صفحه اول
        this.callPanel.classList.add('hidden');
        this.connectionPanel.classList.remove('hidden');
        this.joinBtn.disabled = false;
        this.joinBtn.textContent = 'ورود به اتاق';
        this.usersList.innerHTML = '';
        
        this.status.textContent = 'در حال اتصال...';
        this.status.className = 'status';
        this.timer.textContent = '00:00';
    }
}

// راه‌اندازی برنامه وقتی صفحه لود شد
document.addEventListener('DOMContentLoaded', () => {
    new WebRTCAudioCall();
});
