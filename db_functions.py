import mysql.connector
def connected_to_db():
    return mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'root',
    database = 'dummy_project'
)

def get_basic_information(cursor):
    queries = {
        "Total suppliers": "select count(distinct supplier_id) as total_suppliers from suppliers",
        "Total products": " select count(*) as total_products from products" ,
        "Total categories": " select count(distinct category) from products" ,

        "Total sales value made in last 3 months":
            """select round(sum(abs(se.change_quantity) * p.price), 2) as total_sales_in_last_3_months
               from stock_entries se
                        join products p
                             on se.product_id = p.product_id
               where se.change_type = 'Sale'
                 and se.entry_date >=
                     (select date_sub(max(entry_date), interval 3 month) from stock_entries)""",

        "Total restock value made in last 3 months":
            """select round(sum(abs(se.change_quantity) * p.price), 2) as total_restock_in_last_3_months 
               from stock_entries se
                        join products p
                             on se.product_id = p.product_id
               where se.change_type = 'Restock'
                 and se.entry_date >=
                     (select date_sub(max(entry_date), interval 3 month) from stock_entries)
            """,

        "Below Reorder and No pending Reorders":
            """select count(p.product_id) as below_order
               from products p
               where p.stock_quantity < p.reorder_level
                 and product_id not in
                     (select distinct product_id
                      from reorders
                      where status = 'Pending')"""}
    result = {}
    for label, query in queries.items():
        cursor.execute(query)
        row = cursor.fetchone()
        result[label] = list(row.values())[0]
    return result


def get_additional_tables(cursor):
    queries = {
        "Suppliers and their contact details": "select supplier_name, contact_name , email, phone from suppliers ",
        "Product with their supplier and current stock ": """
    
                                                          select p.product_name,
                                                                 s.supplier_name,
                                                                 p.stock_quantity,
                                                                 p.reorder_level
                                                          from products p
                                                                   join suppliers s
                                                                        on s.supplier_id = p.supplier_id
                                                          order by p.product_name """,

        "Product needing reorder":  """select product_id, product_name, category, stock_quantity, reorder_level from products where stock_quantity < reorder_level """

    }
    tables = {}

    for label, query in queries.items():
        cursor.execute(query)
        tables[label] = cursor.fetchall()
    return tables

def get_categories(cursor):
    cursor.execute("select distinct category from products order by category asc")
    rows = cursor.fetchall()
    return [row['category'] for row in rows ]

def get_suppliers(cursor):
    cursor.execute("select supplier_id, supplier_name from suppliers order by supplier_name ")
    return cursor.fetchall()

def add_new_manual_id(cursor, db,  p_name, p_category, p_price, p_stock, p_reorder, p_supplier):
    proc_call = "call AddNewProductManualID(%s , %s , %s ,%s ,%s ,%s)"
    params = ( p_name, p_category, p_price, p_stock, p_reorder, p_supplier)
    cursor.execute(proc_call , params)
    db.commit()

def get_all_products(cursor):
    cursor.execute('select product_id, product_name from products order by product_name desc')
    return cursor.fetchall()

def get_product_history(cursor,product_id):
    query = "select * from product_inventory_history where product_id = %s order by record_date desc"
    params = (product_id,)
    cursor.execute(query, params)
    return cursor.fetchall()

def place_order(cursor,db,product_id,reorder_quantity):

    query =  """
        insert into reorders(reorder_id , product_id , reorder_quantity, reorder_date, status)
        select max(reorder_id)+1,%s ,%s ,curdate(), 'Ordered'
        from reorders
        """
    cursor.execute(query, (product_id, reorder_quantity))
    db.commit()




