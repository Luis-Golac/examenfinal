from flask import (
    Flask,
    jsonify,
    request,
    abort
)

from datetime import datetime


class Cuenta:
    def __init__(self, numero, nombre, saldo, contactos):
        self.numero = numero
        self.nombre = nombre
        self.saldo = saldo
        self.contactos = contactos

    def __repr__(self):
        return f'Cuenta: numero = {self.numero}, nombre = {self.nombre}, saldo = {self.saldo}, contactos = {self.contactos}'

    def format(self):

        return {
            'nombre': self.nombre,
            'saldo': self.saldo,
            'contactos': self.contactos
        }

    def format_contactos(self):
        c = {}
        for i in self.contactos:
            act = Cuenta.get_cuenta_byNombre(i)
            c[act.numero] = i
        return c

    def historial(self):
        pagos = []
        recibidos = []
        for operacion in operaciones:
            if operacion.numero_cuenta == self.numero:
                pagos.append(operacion)

            if operacion.numeroDestino == self.numero:
                recibidos.append(operacion)

        return pagos, recibidos

    def actualizar_saldo(self, valor):
        self.saldo = self.saldo + valor

    def pagar(self, destino, valor, i1, i2):
        if self.saldo - valor < 0:
            return -1

        fecha_act = datetime.now().strftime('%Y-%m-%d')
        operaciones.append(Operacion(destino.numero, fecha_act, valor, self.numero))
        self.saldo = self.saldo - valor
        cuentas[i1] = Cuenta(self.numero, self.nombre, self.saldo, self.contactos)
        destino.actualizar_saldo(valor)
        cuentas[i2] = destino

        return fecha_act

    @staticmethod
    def get_cuenta_byNumero(numero):
        for i in range(len(cuentas)):
            if cuentas[i].numero == numero:
                return cuentas[i], i
        return -1, -1

    @staticmethod
    def get_cuenta_byNombre(nombre):
        for i in cuentas:
            if i.nombre == nombre:
                return i
        return -1

class Operacion:
    def __init__(self, numeroDestino, fecha, valor, numero_cuenta):
        self.numeroDestino = numeroDestino
        self.fecha = fecha
        self.valor = valor
        # Para identificar el numero de cuenta origen
        self.numero_cuenta = numero_cuenta

    def __repr__(self):
        return f'Operacion: numeroDestino = {self.numeroDestino}, numero_cuenta = {self.numero_cuenta}, valor = {self.valor}, fecha = {self.fecha}'

    def format_p(self):
        return f'Pago realizado de {self.valor} a {self.numeroDestino}'

    def format_r(self):
        return f'Pago recibido de {self.valor} a {self.numero_cuenta}'

# Data con data de inicial
cuentas = [
    Cuenta("123456789", "Luis", 500.5, ["Ximena", "Sebastian"]),
    Cuenta("123456787", "Ximena", 30.5, ["Sebastian"]),
    Cuenta("123456786", "Sebastian", 120.78, ["Ximena"])
]

# Data
operaciones = []

app = Flask(__name__)


@app.route('/', methods=['GET'])
def obtener_contactos():
    return jsonify({
        'success': True,
    })

@app.route('/billetera/contactos')
def contactos():
    error_404 = False
    error_422 = False
    try:
        numero = request.args.get('minumero')
        if numero == "" or numero is None:
            error_422 = True
            abort(422)

        c, i = Cuenta.get_cuenta_byNumero(numero)

        if c == -1:
            error_404 = True
            abort(404)

        return jsonify({
            'success': True,
            'contactos': c.format_contactos()
        })
    except Exception as e:
        print(e)
        if error_404:
            abort(404)
        elif error_422:
            abort(422)
        else:
            abort(500)

@app.route('/billetera/pagar')
def pagar():
    error_404 = False
    error_406 = False
    error_422 = False
    try:
        numero = request.args.get('minumero')
        numero_destino = request.args.get('numerodestino')
        valor = request.args.get('valor')

        if (numero == "" or numero is None) or (numero_destino == "" or numero_destino is None):
            error_422 = True
            abort(422)

        if numero == numero_destino:
            error_406 = True
            abort(406)

        if valor == "" or valor is None:
            error_422 = True
            abort(422)
        try:
            valor = float(valor)
        except Exception as e_:
            print(e_)
            error_406 = True
            abort(406)

        if valor <= 0:
            error_406 = True
            abort(406)

        c1, i1 = Cuenta.get_cuenta_byNumero(numero)

        c2, i2 = Cuenta.get_cuenta_byNumero(numero_destino)

        if c1 == -1 or c2 == -1:
            error_404 = True
            abort(404)

        op = c1.pagar(c2, valor, i1, i2)
        if op == -1:
            error_406 = True
            abort(406)

        return jsonify({
            'success': True,
            'message': f'Realizado el {op}'
        })

    except Exception as e:
        print(e)
        if error_404:
            abort(404)
        elif error_406:
            abort(406)
        elif error_422:
            abort(422)
        else:
            abort(500)

@app.route('/billetera/historial')
def historial():
    error_404 = False
    error_422 = False
    try:
        numero = request.args.get('minumero')
        if numero == "":
            error_422 = True
            abort(422)

        c, i = Cuenta.get_cuenta_byNumero(numero)

        if c == -1:
            error_404 = True
            abort(404)

        p, r = c.historial()

        p = [x.format_p() for x in p]
        r = [x.format_r() for x in r]

        print(p, r)

        return jsonify({
            'success': True,
            'datos': c.format(),
            'pagos_hechos': p,
            'pagos_recibidos': r
        })
    except Exception as e:
        print(e)
        if error_404:
            abort(404)
        elif error_422:
            abort(422)
        else:
            abort(500)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'code': 404,
        'message': 'resource not found'
    }), 404

@app.errorhandler(406)
def not_accepted(error):
    return jsonify({
        'success': False,
        'code': 406,
        'message': 'Not accepted'
    }), 406

@app.errorhandler(422)
def unprocesable(error):
    return jsonify({
        'success': False,
        'code': 422,
        'message': 'Unprocesable'
    }), 422

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'code': 500,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run()
