import psycopg2

def connect_base(namebase, users, password):
    conn = psycopg2.connect(database=namebase, user=users, password=password)
    return conn

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute('create table if not exists clients (id SERIAL PRIMARY KEY, \n'
                    'name varchar(60), \n'
                    'last_name varchar(100), \n'
                    'e_mail varchar(60) \n'
                    ');')

        cur.execute('create table if not exists phone_of_clients (id SERIAL PRIMARY KEY, \n'
                    'phone varchar(20), \n'
                    'id_client integer not null references clients(id) \n'
                    ');')

        conn.commit()
def search_id_client(conn, email): #поскольку в задании не было точно сказано, то я предполагаю, что у клиент уникальный e-mail
    with conn.cursor() as cur:
        cur.execute("SELECT id from clients WHERE e_mail=%s;",(f'{email}',))
        fet = cur.fetchone()
    return fet
#в задании точно не сказано,
#поэтому сначала ищем по email, потом по имени и по фамилии
def search_client(conn, email, name, last_name):
    text_request = "SELECT name, last_name, e_mail from clients "
    with conn.cursor() as cur:
        cur.execute(f"{text_request}WHERE e_mail=%s;",(f'{email}',))
        fet = cur.fetchone()
        if fet == None: #значит по email не нашли
            cur.execute(f"{text_request}WHERE name=%s and last_name=%s ;", (f'{name}',f'{last_name}'))
            fet = cur.fetchone()
            if fet == None: #значит по имени и фамили не нашли
                return f"Нет клиента с таким email: {email}, именем: {name}, фамилией {last_name}"
            else:
                return f"Клиент {fet[0]} {fet[1]}, e-mail: {fet[2]}"
        else:
            return f"Клиент {fet[0]} {fet[1]}, e-mail: {fet[2]}"

#поиск по телефону отдельно сделаем
def search_client_for_phone(conn, phone):
    with conn.cursor() as cur:
        cur.execute('select c."name", c.last_name, c.e_mail  from phone_of_clients poc \n'
                    'join clients c on poc.id_client = c.id \n'
                    ' WHERE poc.phone =%s;', (f'{phone}',))
        fet = cur.fetchone()
        if fet == None:  # значит по имени и фамили не нашли
            return f"Нет клиента с таким телефоном: {phone}"
        else:
            return f"С номером {phone} клиент {fet[0]} {fet[1]}, e-mail: {fet[2]}"
def add_phone(conn, email, phone): #добавялем по email'у, ищем есть ли для такого имайла id, и если есть, то добавляем
    cleint_ids = search_id_client(conn, email)
    if len(cleint_ids) > 0:
        id = cleint_ids[0]
        with conn.cursor() as cur:
            cur.execute('insert into phone_of_clients(phone, id_client) \n'
                        'values(%s,%s)',(phone,id,))
        conn.commit()
    else:
        print(f"Нет клиента с таким email: {email}")
def add_clients(conn, list_clients):
    if len(list_clients) > 0:
        s_list_clients = ""
        for cl in list_clients:
            s_list_clients = s_list_clients + f' (\'{cl["name"]}\',\'{cl["last_name"]}\',\'{cl["email"]}\'),\n'
        with conn.cursor() as cur:
            cur.execute('insert into clients(name, last_name, e_mail) \n'
                        'values \n'
                        f'{s_list_clients[:-2]};')
        conn.commit()
def update_clients(conn,email, name, last_name): #ищем клиента по email, и меняем имя и фамилию, email менять не можем, по сути он "id" клиента
    cleint_ids = search_id_client(conn, email)
    if len(cleint_ids) > 0:
        id = cleint_ids[0]
        with conn.cursor() as cur:
            cur.execute('UPDATE clients SET name = %s, last_name = %s WHERE id = %s;', (name,last_name, id,))
            cur.execute('SELECT * FROM clients ')
        conn.commit()
    else:
        print(f"Нет клиента с таким email: {email}")
def delete_all_clinets(conn): #удаляем все телефоны и всех клиентов
    with conn.cursor() as cur:
        cur.execute('DELETE FROM phone_of_clients; \n'
                    'DELETE FROM clients;')
        cur.execute('SELECT * FROM clients')
        cur.execute('SELECT * FROM phone_of_clients')
    conn.commit()

def delete_all_phones(conn,email): #удаляем все телефоны
    cleint_ids = search_id_client(conn, email)
    if len(cleint_ids) > 0:
        id = cleint_ids[0]
        with conn.cursor() as cur:
            cur.execute('DELETE FROM phone_of_clients WHERE id_client = %s;', (id,))
            cur.execute('SELECT * FROM phone_of_clients ')
        conn.commit()
    else:
        print(f"Нет клиента с таким email: {email}")

def delete_phone(conn, email, phone): #удаляем конкретный номер
    cleint_ids = search_id_client(conn, email)
    if len(cleint_ids) > 0:
        id = cleint_ids[0]
        with conn.cursor() as cur:
            cur.execute('DELETE FROM phone_of_clients WHERE id_client = %s AND phone = %s;', (id,phone))
            cur.execute('SELECT * FROM phone_of_clients ')
        conn.commit()
    else:
        print(f"Нет клиента с таким email: {email}")
def delete_clients(conn,email):
    cleint_ids = search_id_client(conn, email)
    if len(cleint_ids) > 0:
        # сначала удаляем все телефоны
        delete_all_phones(conn, email)
        id = cleint_ids[0]
        with conn.cursor() as cur:
            cur.execute('DELETE FROM clients WHERE id = %s;', (id,))
            cur.execute('SELECT * FROM clients ')
        conn.commit()
    else:
        print(f"Нет клиента с таким email: {email}")

def main():
    client1 = {"name":'Иван',"last_name":'Сидоров',"email":'isid@mail.ru'}
    client2 = {"name":'Петр', "last_name": 'Коровьев', "email": 'p_kor@mail.ru'}
    client3 = {"name":'Сергей', "last_name": 'Петров', "email": 's_petr@mail.ru'}
    list_clients = [client1,client2,client3]
    conn = connect_base('lesson_3','postgres','postgres')
    create_table(conn)
    delete_all_clinets(conn)
    add_clients(conn,list_clients)
    add_phone(conn,'isid@mail.ru','8(121)221-22-22')
    add_phone(conn,'isid@mail.ru','8(4545)545-45-434')
    add_phone(conn,'isid@mail.ru','8(3412)22-22-44')
    add_phone(conn,'p_kor@mail.ru','8(434)112-22-21')
    update_clients(conn,'isid@mail.ru',"Сергей","Григорьев")
    # delete_all_phones(conn,'isid@mail.ru')
    # delete_phone(conn,'isid@mail.ru','8(3412)22-22-44')
    #delete_clients(conn,'isid@mail.ru')
    print(search_client(conn,'isid@mail.ru','',''))
    print(search_client(conn, '', 'Сергей', 'Петров'))
    print(search_client(conn, 's_petr@mail.ru', '', ''))
    print(search_client_for_phone(conn, '8(434)112-22-21'))

    conn.close()
if __name__ == '__main__':
    main()

