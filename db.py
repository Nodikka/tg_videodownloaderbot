from databases import Database
class BotDB:

    def __init__(self, DATABASE_URL):
        self.database = Database(DATABASE_URL)

    async def connect(self):
        await self.database.connect()

    async def create_table(self):
        if await self.database.execute("select exists(select * from information_schema.tables where table_name=(:users))", values={'users': 'users'}) == False:
            await self.database.execute('''CREATE TABLE users ( 
                        id           SERIAL PRIMARY KEY,
                        user_id      BIGINT UNIQUE NOT NULL,
                        join_time    TIMESTAMPTZ DEFAULT Now(),
                        lang_code    INTEGER NOT NULL)''')
    
    async def user_exists(self, user_id):
        if await self.database.execute("select exists(select id from users where user_id = (:user_id))", values={'user_id': user_id}) == False:
            return False
    
    async def new_user(self, user_id, lang_code):
        await self.database.execute(f"INSERT INTO users(user_id, lang_code) "
                           f"VALUES (:user_id, :lang_code) returning id", values={'user_id': user_id, 'lang_code': lang_code})

    async def save_lang_code(self, user_id, lang_code):
        await self.database.execute(f"UPDATE users SET lang_code = (:lang_code)"
                            f"WHERE user_id = (:user_id)", values={'lang_code': lang_code, 'user_id': user_id})

    async def get_lang_code(self, user_id):
        results = await self.database.fetch_all("SELECT lang_code FROM users WHERE user_id = (:user_id)", values={'user_id': user_id})
        result = [next(result.values()) for result in results]
        return int(''.join(map(str, result)))

    async def get_all_users_id(self):
        results = await self.database.fetch_all("SELECT user_id FROM users")
        result = [next(result.values()) for result in results]
        return  result