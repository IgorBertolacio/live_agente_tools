"""
Script para testar conexão com PostgreSQL
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Testa conexão com o banco de dados"""
    try:
        print("🔌 Conectando ao PostgreSQL...")
        print(f"Host: {os.getenv('DB_HOST')}")
        print(f"Database: {os.getenv('DB_NAME')}")
        print(f"User: {os.getenv('DB_USER')}")

        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

        print("✅ Conexão estabelecida com sucesso!")

        # Testar uma query simples
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"\n📊 Versão do PostgreSQL: {version[0]}")

        # Listar tabelas
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            LIMIT 10;
        """)
        tables = cursor.fetchall()

        print(f"\n📋 Primeiras 10 tabelas encontradas:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

        print("\n✅ Teste concluído com sucesso!")
        return True

    except psycopg2.OperationalError as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("\n💡 Verifique:")
        print("  - Host e porta corretos")
        print("  - Credenciais válidas")
        print("  - Firewall/VPN se necessário")
        return False
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_connection()
