import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

print("📱 기존 사용자 전화번호 업데이트 중...")

with engine.connect() as conn:
    # admin 계정 전화번호 업데이트
    conn.execute(text("UPDATE users SET phone_number = '010-1234-5678' WHERE email = 'admin@jupyter-platform.com'"))
    
    # test 계정 전화번호 업데이트  
    conn.execute(text("UPDATE users SET phone_number = '010-9876-5432' WHERE email = 'test@example.com'"))
    
    conn.commit()
    print('✅ 기존 사용자 전화번호 업데이트 완료')
    
    # 확인
    result = conn.execute(text("SELECT username, email, phone_number FROM users WHERE email IN ('admin@jupyter-platform.com', 'test@example.com')"))
    
    print("\n📋 업데이트된 사용자:")
    for row in result:
        print(f"  👤 {row[0]} ({row[1]}) - 📱 {row[2]}") 