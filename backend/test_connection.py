import psycopg2
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def test_postgresql_connection():
    database_url = os.getenv("DATABASE_URL")
    print(f"Testing connection to: {database_url}")
    
    try:
        # Test with SQLAlchemy
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"PostgreSQL version: {version}")
        
        # Test creating a simple table
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50)
                );
            """))
            conn.commit()
            print("✅ Can create tables!")
            
            # Clean up
            conn.execute(text("DROP TABLE IF EXISTS test_table;"))
            conn.commit()
            print("✅ Database is ready!")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_postgresql_connection()