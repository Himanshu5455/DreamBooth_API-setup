import psycopg2

def dbConnect():
    conn = psycopg2.connect(user='postgres',
                            password='dreambooth123',
                            host='dreambooth.cldngnmue5iq.ap-south-1.rds.amazonaws.com',
                            port='5432',
                            database='dreambooth_db')
    return conn

