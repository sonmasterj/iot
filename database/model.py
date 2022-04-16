from peewee import *
db = PostgresqlDatabase('sensors', user='pi', password='12345678s',host='localhost', port=5432)
db.connect()
class BaseModel(Model):
    class Meta:
        database =db
class CO2(BaseModel):
    co2= FloatField(null=False)
    time = IntegerField(null=False)
class Temp(BaseModel):
    temp= FloatField(null=False)
    time = IntegerField(null=False)
class Digital(BaseModel):
    air_oxy= FloatField(null=False)
    humid= FloatField(null=False)
    press= FloatField(null=False)
    time = IntegerField(null=False)
class Analog(BaseModel):
    water_oxy= FloatField(null=False)
    ec= FloatField(null=False)
    pH= FloatField(null=False)
    time = IntegerField(null=False)
class Sound(BaseModel):
    sound= FloatField(null=False)
    time = IntegerField(null=False)

def creat_table():
    if db.table_exists(table_name='co2')!=True:
        db.create_tables([CO2,Sound,Analog,Digital,Temp])
def db_close():
    db.close()