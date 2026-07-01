# 👤 Face Recognition Check-in System

Một hệ thống điểm danh thông minh sử dụng nhận diện khuôn mặt thời gian thực từ camera và ảnh upload.

## ✨ Tính năng chính

- 📷 **Nhận diện realtime**: Stream camera trực tiếp, nhận diện khuôn mặt real-time
- 📤 **Upload ảnh**: Tải ảnh lên, nhận diện tới 10 người trong một ảnh
- 👥 **Quản lý nhân viên**: CRUD thông tin nhân viên và ảnh khuôn mặt
- 📊 **Lịch sử điểm danh**: Xem chi tiết thời gian check-in/check-out
- 🔍 **Nhận diện chính xác**: Sử dụng InsightFace buffalo_l model (98%+ accuracy)
- 🎨 **Giao diện thân thiện**: React web UI với real-time updates

## 🏗️ Kiến trúc hệ thống

```
backend/                 # FastAPI + InsightFace
frontend/               # React + Vite
db/                     # Database schemas
docker-compose.yml      # Orchestration
```

### Stack công nghệ

**Backend:**
- FastAPI (Python)
- InsightFace (buffalo_l model)
- PostgreSQL
- Redis (caching, real-time)
- WebSocket/SSE

**Frontend:**
- React 18
- Vite
- TailwindCSS
- Socket.io
- OpenCV.js (camera processing)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### Installation

```bash
# Clone repo
git clone https://github.com/ThienDT69/face-recognition-checkin.git
cd face-recognition-checkin

# Sử dụng Docker Compose (khuyến nghị)
docker-compose up -d

# Hoặc cài đặt manual
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### Environment Variables

Xem file `.env.example` trong mỗi thư mục.

```bash
# backend/.env
DATABASE_URL=postgresql://user:password@localhost/checkin_db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
```

## 📖 API Documentation

### FastAPI Docs
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

### Main Endpoints

**Employees**
- `GET /api/v1/employees` - Danh sách nhân viên
- `POST /api/v1/employees` - Thêm nhân viên
- `PUT /api/v1/employees/{id}` - Cập nhật nhân viên
- `DELETE /api/v1/employees/{id}` - Xóa nhân viên

**Face Recognition**
- `POST /api/v1/recognize/image` - Nhận diện từ ảnh upload
- `WebSocket /ws/camera` - Nhận diện realtime từ camera
- `POST /api/v1/face/register/{employee_id}` - Đăng ký khuôn mặt

**Check-in/Check-out**
- `GET /api/v1/checkins` - Lịch sử điểm danh
- `POST /api/v1/checkin/{employee_id}` - Manual check-in
- `GET /api/v1/checkins/stats` - Thống kê

## 🔧 Configuration

### Face Recognition Model

Model mặc định: `buffalo_l` (Large model - 98%+ accuracy)

Tùy chỉnh tại `backend/app/config.py`:
```python
FACE_MODEL = "buffalo_l"  # hoặc "buffalo_m", "buffalo_s"
CONFIDENCE_THRESHOLD = 0.6
MAX_FACES_PER_IMAGE = 10
```

### Database

Database migrations tự động chạy khi khởi động. Manual:
```bash
cd backend
alembic upgrade head
```

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── employees.py
│   │   │   │   ├── recognition.py
│   │   │   │   ├── checkin.py
│   │   │   │   └── auth.py
│   │   │   └── deps.py
│   │   ├── models/
│   │   │   ├── employee.py
│   │   │   ├── checkin.py
│   │   │   ├── face_embedding.py
│   │   │   └── base.py
│   │   ├── schemas/
│   │   │   ├── employee.py
│   │   │   ├── recognition.py
│   │   │   └── checkin.py
│   │   ├── services/
│   │   │   ├── face_recognition.py
│   │   │   ├── checkin_service.py
│   │   │   ├── employee_service.py
│   │   │   └── cache.py
│   │   ├── ws/
│   │   │   └── camera.py
│   │   └── utils/
│   │       ├── image_processing.py
│   │       └── validators.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── alembic/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Camera.jsx
│   │   │   ├── ImageUpload.jsx
│   │   │   ├── EmployeeForm.jsx
│   │   │   ├── CheckinHistory.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── pages/
│   │   │   ├── CheckinPage.jsx
│   │   │   ├── AdminPage.jsx
│   │   │   ├── EmployeesPage.jsx
│   │   │   ├── HistoryPage.jsx
│   │   │   └── LoginPage.jsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   ├── useCamera.js
│   │   │   └── useFaceRecognition.js
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── websocket.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🔐 Security

- JWT authentication cho API
- CORS configuration
- Rate limiting
- Input validation
- Secure password hashing

## 📊 Database Schema

```sql
-- Employees
CREATE TABLE employees (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE,
  department VARCHAR(100),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Face Embeddings
CREATE TABLE face_embeddings (
  id UUID PRIMARY KEY,
  employee_id UUID REFERENCES employees(id),
  embedding FLOAT8[],
  image_path VARCHAR(255),
  created_at TIMESTAMP
);

-- Check-ins
CREATE TABLE checkins (
  id UUID PRIMARY KEY,
  employee_id UUID REFERENCES employees(id),
  check_in_time TIMESTAMP,
  check_out_time TIMESTAMP,
  method VARCHAR(50), -- camera, upload, manual
  confidence FLOAT,
  created_at TIMESTAMP
);
```

## 🧪 Testing

```bash
cd backend
pytest tests/
```

## 📝 Logging

Logs được lưu tại `logs/app.log`. Tùy chỉnh tại `backend/app/config.py`.

## 🤝 Contributing

1. Fork repo
2. Tạo branch feature (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - xem file LICENSE

## 👨‍💻 Author

ThienDT69 - [GitHub](https://github.com/ThienDT69)

## 📧 Support

Có câu hỏi? Mở issue trên GitHub hoặc liên hệ trực tiếp.

---

**Made with ❤️ using FastAPI + React + InsightFace**
