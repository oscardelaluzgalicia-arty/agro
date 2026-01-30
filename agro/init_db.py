#!/usr/bin/env python3
"""
Script para inicializar el schema de la base de datos
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Crea todas las tablas necesarias"""
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✓ Conectado a la base de datos")
        
        # Leer y ejecutar schema
        with open("schema.sql", "r") as f:
            schema = f.read()
        
        with conn.cursor() as cur:
            for statement in schema.split(";"):
                if statement.strip():
                    print(f"Ejecutando: {statement[:60]}...")
                    cur.execute(statement)
        
        conn.commit()
        print("✓ Schema inicializado correctamente")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    init_database()
