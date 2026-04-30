import psycopg2
import psycopg2.extras
from config import DB_CONFIG

SCHEMA = 

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def get_or_create_player(username: str) -> int:
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) "
                "ON CONFLICT (username) DO NOTHING",
                (username,)
            )
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            pid = cur.fetchone()[0]
        conn.commit()
        return pid
    finally:
        conn.close()

def save_result(username: str, score: int, level_reached: int):
    
    conn = get_connection()
    try:
        pid = get_or_create_player(username)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached) "
                "VALUES (%s, %s, %s)",
                (pid, score, level_reached)
            )
        conn.commit()
    finally:
        conn.close()

def get_top10() -> list[dict]:
    
    sql = 
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def get_personal_best(username: str) -> int:
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                ,
                (username,)
            )
            return cur.fetchone()[0]
    finally:
        conn.close()
