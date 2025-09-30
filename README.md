# Attendance System

## معرفی
این پروژه با پایتون و فریم‌ورک Flask توسعه داده شده است و شامل سه میکروسرویس و یک کلاینت ساده می‌باشد:
- میکروسرویس احراز هویت (Auth Service) برای ورود و ثبت‌نام کارمندان
- میکروسرویس ثبت حضور و غیاب (Attendance Service) برای ثبت ورود و خروج و ارائه گزارش‌ها
- میکروسرویس گزارش زنده (Reporter Service) برای نمایش لحظه‌ای ورود و خروج‌ها از طریق WebSocket
- کلاینت ساده HTML برای تست و ارسال درخواست‌ها

این سیستم از **REST**، **gRPC** و **WebSocket** برای پیاده‌سازی APIها استفاده می‌کند. همچنین برای امنیت داده‌ها از **JWT** استفاده شده است.

> توجه: پورت‌های `8001`, `8002`, `8103`, `5500`, `50051`, و `5432` باید خالی باشند.

---

## راه‌اندازی و نصب

1. کلون کردن ریپازیتوری:
```bash
git clone https://github.com/rootmamad/attendance-system.git
cd attendance-system
```

2. اجرا با Docker:
```bash
docker compose up --build
```
سپس به آدرس زیر بروید:  
[http://127.0.0.1:5500/index.html](http://127.0.0.1:5500/index.html)

---

## میکروسرویس‌ها

### 1. Auth Service
- **پورت:** 8001  
- **فایل‌ها:** `app.py`, `routes.py`, `db.py`, `jwt_utils.py`, `Dockerfile`, `requirements.txt`

**توضیحات فایل‌ها:**
- `app.py`: اجرای کلی میکروسرویس  
- `jwt_utils.py`: تولید و اعتبارسنجی JWT + دکوریتور Middleware  
- `db.py`: مدیریت اتصال به دیتابیس  
- `routes.py`: شامل Blueprint و سه اندپوینت برای ثبت‌نام، ورود و لیست کارمندان (REST)  
- `requirements.txt`: لیست وابستگی‌ها  

---

### 2. Attendance Service
- **پورت:** 8002  
- **فایل‌ها:** `grpc_server.py`, `proto/`, `app.py`, `routes_rest.py`, `db.py`, `jwt_utils.py`, `Dockerfile`, `requirements.txt`

**توضیحات فایل‌ها:**
- `grpc_server.py` و `proto`: پیاده‌سازی gRPC و متدهای لیست و استریم  
- `routes_rest.py`: شامل Blueprint برای مدیریت ورود/خروج و نمایش لیست روز اخیر از طریق REST  
- سایر فایل‌ها مشابه Auth Service  

---

### 3. Reporter Service
- **پورت:** 8103  
- **فایل‌ها:** `app.py`

این سرویس با WebSocket کار می‌کند و وظیفه ارسال زنده رویدادهای جدید حضور و غیاب به کلاینت‌ها را دارد. شامل دو اندپوینت در `app.py` است.

---

## کلاینت
یک فایل ساده HTML برای ارسال درخواست‌ها و تست APIها قرار داده شده است.  
برای اجرا:  
```
http://127.0.0.1:5500/index.html
```

---

## فایل‌های پیکربندی

- **docker-compose.yml**: مدیریت سرویس‌ها و اجرای کانتینرها  
- **.env**: تعریف متغیرهای محیطی و جلوگیری از هاردکد شدن مقادیر در کدها  

---

## تست سرویس‌ها

### 1. Register (Auth)
```bash
curl -X POST http://localhost:8001/register   -H "Content-Type: application/json"   -d '{"username":"emp2","password":"1234"}'
```

### 2. Login (Auth)
```bash
curl -X POST http://localhost:8001/login   -H "Content-Type: application/json"   -d '{"username":"emp2","password":"1234"}'
```
خروجی یک **JWT Token** است.

### 3. Attendance.List (gRPC)
```bash
grpcurl -plaintext   -d '{"employee_id":1,"jwt":"<JWT_TOKEN>"}'   localhost:50051 proto.AttendanceService.List
```

### 4. Attendance.StreamNew (gRPC – استریم زنده)
```bash
grpcurl -plaintext   -d '{"employee_id":1,"jwt":"<JWT_TOKEN>"}'   localhost:50051 proto.AttendanceService.StreamNew
```

### 5. Reporter (WebSocket)
```bash
wscat -c "ws://localhost:8103/ws?token=<JWT_TOKEN>"
```
هر بار که Attendance رکورد جدیدی ثبت کند، Reporter آن را به کلاینت‌های WS ارسال می‌کند.

---

## پایان
پروژه کامل شد، آماده بررسی و استفاده! 🚀

