import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime, json
import requests
from flask import Flask, url_for, flash
from flask import render_template, request, redirect
import requests


cred = credentials.Certificate("firebase-key.json")
fire = firebase_admin.initialize_app(cred)
db = firestore.client()
client_ref = db.collection('Clientes')
order_ref = db.collection('Ordenes')
history_ref = db.collection('Historial')


#regresa todos lo que hay en un documento en forma de lista 
def read_docs(ref):
    docs = ref.get()
    all_entries = []
    # return [task.to_dict() for task in docs]
    for doc in docs:
        entries = doc.to_dict()
        entries['id'] = doc.id
        all_entries.append(entries)

    return all_entries

#obtiene la informacion de un solo documento y la regresa en forma de diccionario 
def read_doc(ref, id):
    task = ref.document(id).get() #leer una solo un documento de firebase 
    return task.to_dict()

def create_history(ref, name, action):
    if action == 'terminada':
        info = {
        'cliente': name,
        'action': action,
        'date':datetime.datetime.now()
        }
        ref.document().set(info)
    elif action == 'cancelo':
        info = {
        'cliente': name,
        'action': action,
        'date':datetime.datetime.now()
        }
        ref.document().set(info)
    elif action == 'entregada':
        info = {
        'cliente': name,
        'action': action,
        'date':datetime.datetime.now()
        }
        ref.document().set(info)
    elif action == 'compro':
        info = {
        'cliente': name,
        'action': action,
        'date':datetime.datetime.now()
        }
        ref.document().set(info)

def create_order(ref, name, qty):
    client_search = search_client(name)
    if client_search != "No existe":
        info = {
        'name': name,
        'cantidad': qty,
        'check': False,
        'date':datetime.datetime.now()
        }
        ref.document().set(info)
        create_history(history_ref, name, 'compro')
    else:
        print("El cliente no existe")

def create_client(ref, name):
        info = {
        'name': name,
        }
        ref.document().set(info)

def update_doc(ref,id):
    ref.document(id).update({'check': True})

def update_order(ref,id):
    ref.document(id).update({'check': True})
    doc = read_doc(ref,id)
    client = doc['name']
    create_history(history_ref, client, 'terminada')


def delete_doc(ref,id):
    ref.document(id).delete()

def delete_order(ref,id):
    doc = read_doc(ref,id)
    client = doc['name']
    create_history(history_ref, client, 'cancelo')
    ref.document(id).delete()

def deliver_order(ref,id):
    doc = read_doc(ref,id)
    client = doc['name']
    create_history(history_ref, client, 'entregada')
    ref.document(id).delete()
    
def search_client(name):
    clients = read_docs(client_ref)
    clientID = "No existe"
    for client in clients:
        if client['name'] == name:
            clientID = client['id']
    return clientID


# order = create_order(order_ref, 'Alejandro Linares', 12)
# cancel_order = delete_doc(order_ref, 'Vp817kHiCr9RxUjEasiX')
#update_order(order_ref, 'ReFj2pOnaUueU3OyrQta')
# cancel_order = delete_order(order_ref, 'WcJXfojf8Bw9oEbe4OXC')


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        try:
            orders = read_docs(order_ref)
            clients = read_docs(client_ref)
            completed = []
            incompleted = []

            for order in orders:
                if order['check']==True:
                    completed.append(order)
                else:
                    incompleted.append(order)

        except:
            orders = []
            print("error")
        print(len(incompleted))
        response = {
            'completed':completed,
            'incompleted':incompleted,
            'completadas':len(completed),
            'pendientes':len(incompleted),
            'clientes':len(clients),
            'allclients':clients
        }
        return render_template('index.html', response=response)

    
@app.route('/ordenes', methods=['GET', 'POST'])
def ordenes():
    if request.method == 'GET':
            try:
                orders = read_docs(order_ref)
                completed = []
                incompleted = []

                for order in orders:
                    if order['check']==True:
                        completed.append(order)
                    else:
                        incompleted.append(order)
            except:
                order = []
                print("error")
            response = {
                'completed':completed,
                'incompleted':incompleted,
                'contador1':len(completed),
                'contador2':len(incompleted)
            }
            return render_template('ordenes.html', response=response)
    else:
        name = request.form["name"]
        qty = request.form["qty"]
        try:
            create_order(order_ref, name, qty)
            return redirect('/ordenes')
        except:
            pass
    
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if request.method == 'GET':
            try:
                clients = read_docs(client_ref)
            except:
                print("error")
            response = {

            'allclients':clients
            }
            return render_template('clientes.html', response=response)
    else:
        name = request.form["name"]
        try:
            create_client(client_ref, name)
            return redirect('/clientes')
        except:
            pass
    
@app.route('/historial', methods=['GET'])
def historial():
    if request.method == 'GET':
            try:
                clients = read_docs(history_ref)
                hist = sorted(clients, key=lambda i: i['date'], reverse=True)
            except:
                print("error")
            response = {
            'history':hist
            }
            return render_template('historial.html', response=response)

    


@app.route('/update/<string:id>', methods=['GET'])
def update(id):
    try:
            update_order(order_ref, id)
            return redirect(request.referrer)

    except:
        return redirect('/')


@app.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    print(f"\nVas a borrar {id}\n")
    try:
        delete_order(order_ref, id)
        return redirect(request.referrer)

    except:
        return redirect(request.referrer)

@app.route('/deletec/<string:id>', methods=['GET'])
def deletec(id):
    print(f"\nVas a borrar {id}\n")
    try:
        delete_doc(client_ref, id)
        return redirect(request.referrer)

    except:
        return redirect(request.referrer)

@app.route('/deleteh/<string:id>', methods=['GET'])
def deleteh(id):
    print(f"\nVas a borrar {id}\n")
    try:
        delete_doc(history_ref, id)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)
        

@app.route('/deleteh2/<string:id>', methods=['GET'])
def deleteh2(id):
    print(f"\nVas a borrar {id}\n")
    try:
        deliver_order(order_ref, id)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)



if __name__ == '__main__':
    app.run(debug=True)









