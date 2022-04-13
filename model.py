from peewee import *
dbName = "data.db"
db = SqliteDatabase(dbName,pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0
})
db.connect()
class BaseModel(Model):
    class Meta:
        database =db
class Sensor(BaseModel):
    so2= CharField(null=False,max_length=5)
    no2= CharField(null=False,max_length=5)
    co= CharField(null=False,max_length=5)
    time = TimestampField()

def creat_table():
    if db.table_exists(table_name='sensor')!=True:
        db.create_tables([Sensor])
def db_close():
    db.close()
