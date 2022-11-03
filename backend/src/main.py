import datetime
import json
import random
from flask import Flask, jsonify,request
from flask_restful import Api
import xml.etree.ElementTree as ET
#modules

app = Flask(__name__)
api = Api(app)

# global variables
consum_list = []


@app.route("/")
def hello_world():
    return "<p>Hello</p>"


@app.route("/consultarDatos", methods=['GET'])
def consultarDatos():
    with open('data.json') as json_file:
        data = json.load(json_file)
        print(data["lista_recursos"][0]["id"])
        return jsonify(data)

# METODOS POST
@app.route("/crearRecurso", methods=['POST'])
def crearRecurso():
    data = request.get_json()
    # obtener base datos
    with open('data.json') as json_file:
        data_base = json.load(json_file)
    # validar recursos
    for recurso in data_base['lista_recursos']:
        if data['id'] == recurso['id']:
            return jsonify({"error": "El recurso ya existe"})
    # agregar recurso
    data_base['lista_recursos'].append(data)
    # guardar base datos
    with open('data.json', 'w') as outfile:
        json.dump(data_base, outfile, indent=4)

    return jsonify({"mensaje": "Recurso creado exitosamente"})


@app.route("/crearCategoria", methods=['POST'])
def crearCategoria():
    data = request.get_json()
    # obtener base datos
    with open('data.json') as json_file:
        data_base = json.load(json_file)
    # validar recursos
    for categoria in data_base['lista_categorias']:
        if data['id'] == categoria['id']:
            return jsonify({"error": "La categoria ya existe ya existe"})
            
    # agregar recurso
    data_base['lista_categorias'].append(data)
    # guardar base datos
    with open('data.json', 'w') as outfile:
        json.dump(data_base, outfile, indent=4)

    return jsonify({"mensaje": "Categoria creado exitosamente"})
            

@app.route('/crearConfiguracion', methods=['POST'])
def crearConfiguracion():
    data = request.get_json()
    # obtener base datos
    with open('data.json') as json_file:
        data_base = json.load(json_file)
    # validar que la categoria exista
    for categoria in data_base['lista_categorias']:
        if categoria['id'] == data['id_categoria']:
            #validar que la configuracion no exista
            for configuracion in categoria['configuraciones']:
                if configuracion['id'] == data['id']:
                    return jsonify({"error": "La configuracion ya existe"})
            # agregar configuracion
            # eliminar id_categoria
            del data['id_categoria']
            categoria['configuraciones'].append(data)
            # guardar base datos
            with open('data.json', 'w') as outfile:
                json.dump(data_base, outfile, indent=4)
            return jsonify({"mensaje": "Configuracion creada exitosamente"})

    return jsonify({"error": "La categoria no existe"})


@app.route("/crearCliente", methods=['POST'])
def crearCliente():
    data = request.get_json()
    # obtener base datos
    with open('data.json') as json_file:
        data_base = json.load(json_file)
    # validar recursos
    for cliente in data_base['lista_clientes']:
        if data['nit'] == cliente['nit']:
            return jsonify({"error": "El cliente ya existe"})
    # agregar recurso
    data_base['lista_clientes'].append(data)
    # guardar base datos
    with open('data.json', 'w') as outfile:
        json.dump(data_base, outfile, indent=4)

    return jsonify({"mensaje": "Cliente creado exitosamente"})


@app.route('/crearInstancia', methods=['POST'])
def crearInstancia():
    data = request.get_json()
    # obtener base datos
    with open('data.json') as json_file:
        data_base = json.load(json_file)
    # validar que el clienta exista
    for cliente in data_base['lista_clientes']:
        if cliente['nit'] == data['nit_cliente']:
            # validar que la instancia que no exista
            for instancia in cliente['lista_instancias']:
                if instancia['id'] == data['id']:
                    return jsonify({"error": "La instancia ya existe"})
            # validar que idConfiguracion exista
            for categoria in data_base['lista_categorias']:
                for configuracion in categoria['configuraciones']:
                    if configuracion['id'] == data['idConfiguracion']:
                        # agregar instancia
                        # eliminar id_categoria
                        del data['nit_cliente']
                        cliente['lista_instancias'].append(data)
                        # guardar base datos
                        with open('data.json', 'w') as outfile:
                            json.dump(data_base, outfile, indent=4)
                        return jsonify({"mensaje": "Instancia creada exitosamente"})
            return jsonify({"error": "La configuracion no existe"})

    return jsonify({"error": "El cliente no existe"})

@app.route('/generarFactura', methods=['POST'])
def generarFactura():
    data = request.get_json()
    # obtener base datos
    with open('data.json') as json_file:
        data_base = json.load(json_file)
    
    # buscar los consumos de un cliente
    lista_consumo = []
    for consumo in consum_list:
        if consumo['nitCliente'] == data['nit']:
            lista_consumo.append(consumo)

    
    # json factura
    factura = {
        # id aleatorio
        "id": random.randint(1, 100000),
        "Fecha de emision": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nit_cliente": data['nit'],
        "Total":0,
        "Detalle": []
    }
   # buscar el cliente
    for consumo in lista_consumo:
        for cliente in data_base['lista_clientes']:
            if cliente['nit'] == consumo['nitCliente']:
                # verificar instancia
                for instancia in cliente['lista_instancias']:
                    if instancia['id'] == consumo['idInstancia']:
                        # verificar configuracion
                        for categoria in data_base['lista_categorias']:
                            for configuracion in categoria['configuraciones']:
                                if configuracion['id'] == instancia['idConfiguracion']:
                                    # calcular el total
                                    valor_por_recurso = 0
                                    print(configuracion['recursos_configuracion'])
                                    for recurso_config in configuracion['recursos_configuracion']:
                                        lista_recursos = []
                                        for recurso in data_base['lista_recursos']:
                                            if recurso['id'] == recurso_config['id']:
                                                print(recurso['valorXhora'])
                                                valor_por_recurso += float(recurso['valorXhora']) * float(recurso_config['value']) * float(consumo['tiempo'])

                                            # agregar detalle recurso
                                            recurso_dic = {
                                                "id": recurso['id'],
                                                "nombre": recurso['nombre'],
                                                "valorXhora": recurso['valorXhora'],
                                            }
                                            lista_recursos.append(recurso_dic)
                                    # agregar detalle configuracion
                                    configuracion_dic = {
                                        "id": configuracion['id'],
                                        "nombre": configuracion['nombre'],
                                        "recursos": lista_recursos
                                    }
                                    # agregar detalle instanciaaunque
                                    instancia_dic = {
                                        "id": instancia['id'],
                                        "nombre": instancia['nombre'],
                                        "fecha de inicio": instancia['fechaInicio'],
                                        "fecha de fin": consumo['fechaHora'],
                                        "configuraciones": [configuracion_dic]
                                    }
                                    # agregar detalle cliente
                                    cliente_dic = {
                                        "nit": cliente['nit'],
                                        "nombre": cliente['nombre'],
                                        "valor de consumo": valor_por_recurso,
                                        "instancias": [instancia_dic],
                                    }
                                    # agregar detalle factura
                                    factura['Detalle'].append(cliente_dic)
                                    factura['Total'] += valor_por_recurso    

    # guardar factura en cliente
    for cliente in data_base['lista_clientes']:
        if cliente['nit'] == data['nit']:
            cliente['lista_facturas'] = []
            cliente['lista_facturas'].append(factura)
            # guardar base datos
            with open('data.json', 'w') as outfile:
                json.dump(data_base, outfile, indent=4)
                # eliminar detalles 
                del factura['Detalle']
            return jsonify({
                "mensaje": "Factura creada exitosamente", 
                "factura": factura
            }), 200
    return jsonify({"error": "El cliente no existe"})

@app.route('/detalleFactura', methods=['POST'])
def detalleFactura():
    data = request.get_json()
    # obtener base datos
    with open('data.json') as json_file:
        data_base = json.load(json_file)
    # buscar el cliente
    for cliente in data_base['lista_clientes']:
        if cliente['nit'] == data['nit']:
            # buscar la factura
            for factura in cliente['lista_facturas']:
                if factura['id'] == data['idFactura']:
                    return jsonify(factura), 200
            return jsonify({"error": "La factura no existe"})
            
# obtener facturas de un cliente
@app.route("/archivoEntrada", methods=['POST'])
def leer_xml():
    xml_data = request.get_data()
    # read xml
    tree =  ET.fromstring(xml_data)

    list_initial_config = {
        "lista_recursos": None,
        "lista_categorias": None,
        "lista_clientes": None,
    }
    for i in tree:
        list_resource = []
        for resource_list in i.iter('listaRecursos'):
            for resource in resource_list.iter('recurso'):
                dic_resource = {
                    "id": resource.attrib['id'],
                    "nombre": resource.find('nombre').text,
                    "abreviatura": resource.find('abreviatura').text,
                    "metrica": resource.find('metrica').text,
                    "tipo": resource.find('tipo').text,
                    "valorXhora": resource.find('valorXhora').text
                }
                list_resource.append(dic_resource)
            list_initial_config["lista_recursos"] = list_resource
            

        list_category = []
        for category_list in i.iter('listaCategorias'):
            for category in category_list.iter('categoria'):
                list_config = []
                for config_list in category.iter('listaConfiguraciones'):
                    for config in config_list.iter('configuracion'):

                        list_resources_config = []
                        for resource_config in config.iter('recursosConfiguracion'):
                            for resource in resource_config.iter('recurso'):
                                print(resource.attrib)
                                for value in resource.iter('recurso'):
                                    print(value.text)

                                dic_resource_config = {
                                    "id": resource.attrib['id'],
                                    "value": value.text
                                }
                                list_resources_config.append(dic_resource_config)
                        dic_config = {
                            "id": config.attrib['id'],
                            "nombre": config.find('nombre').text,
                            "description": config.find('descripcion').text,
                            "recursos_configuracion": list_resources_config
                        }
                        list_config.append(dic_config)   
                dic_category = {
                    "id": category.attrib['id'],
                    "nombre": category.find('nombre').text,
                    "descripcion": category.find('descripcion').text,
                    "carga_trabajo": category.find('cargaTrabajo').text,
                    "configuraciones": list_config
                }
                list_category.append(dic_category)
            list_initial_config["lista_categorias"] = list_category

        list_clients = []
        for client_list in i.iter('listaClientes'):
            for client in client_list.iter('cliente'):
                list_instance = []
                for instance_list in client.iter('listaInstancias'):
                    for instance in instance_list.iter('instancia'):
                        dic_instance = {
                            "id": instance.attrib['id'],
                            "idConfiguracion": instance.find('idConfiguracion').text,
                            "nombre": instance.find('nombre').text,
                            "fechaInicio": instance.find('fechaInicio').text,
                            "estado": instance.find('estado').text,
                            "fechaFinal": instance.find('fechaFinal').text
                        }
                        list_instance.append(dic_instance)
                dic_client = {
                    "nit": client.attrib['nit'],
                    "nombre": client.find('nombre').text,
                    "usuario": client.find('usuario').text,
                    "clave": client.find('clave').text,
                    "direccion": client.find('direccion').text,
                    "correoElectronico": client.find('correoElectronico').text,
                    "lista_instancias": list_instance
                }
                list_clients.append(dic_client)
            list_initial_config["lista_clientes"] = list_clients
    with open('data.json', 'w') as outfile:
        json.dump(list_initial_config, outfile, indent=4)
    
    return jsonify({"datos": 'se ha leido el xml'})

@app.route("/archivoConsumo", methods=['POST'])
def leer_xml_consumo():
    xml_data = request.get_data()
    # read xml
    tree =  ET.fromstring(xml_data)
    for i in tree:
        for consum in i.iter('consumo'):
            consum_dic = {
                "nitCliente": consum.attrib['nitCliente'],
                "idInstancia": consum.attrib['idInstancia'],
                "tiempo": consum.find('tiempo').text,
                "fechaHora": consum.find('fechaHora').text
            }
            consum_list.append(consum_dic)
    print(consum_list)
    return jsonify({"datos": 'se ha leido el xml de consumos'})





if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run(host="0.0.0.0", port="5000")