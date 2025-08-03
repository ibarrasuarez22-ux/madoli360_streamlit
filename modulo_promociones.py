# modulo_promociones.py
import datetime
import logging

# ⚙️ Configuración de logging institucional
logging.basicConfig(
    filename='logs_promociones.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

# 🧠 Función principal trazable
def bloque_promociones_predictivas(cliente_dict):
    """
    Aplica lógica predictiva sobre un cliente y retorna promociones sugeridas.
    
    Parámetros esperados:
        cliente_dict: dict con al menos los campos 'id_cliente', 'segmento', 'historial'
    
    Retorna:
        dict con 'id_cliente', 'promociones_sugeridas', 'timestamp'
    """

    # 🛡️ Validaciones básicas
    if not isinstance(cliente_dict, dict):
        logging.warning("Entrada no válida: cliente_dict no es tipo dict.")
        return {"error": "Formato de entrada no válido"}

    id_cliente = cliente_dict.get('id_cliente')
    segmento = cliente_dict.get('segmento')
    historial = cliente_dict.get('historial', [])

    if not id_cliente or not segmento:
        logging.warning(f"Cliente inválido | Datos faltantes: {cliente_dict}")
        return {"error": "Faltan campos obligatorios"}

    # 📊 Lógica institucional ficticia para demostración
    promociones = []

    if segmento == "A":
        promociones.append("Descuento 20% en seguro de auto")
    elif segmento == "B":
        promociones.append("Membresía gratuita por 3 meses")
    else:
        promociones.append("Asesoría personalizada sin costo")

    # 🧮 Enriquecimiento adicional por historial
    if "reclamación reciente" in historial:
        promociones.append("Bonificación por fidelidad")

    resultado = {
        "id_cliente": id_cliente,
        "promociones_sugeridas": promociones,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    logging.info(f"Promociones generadas para ID {id_cliente} | {resultado}")
    return resultado

def generar_promociones_consolidadas(fuentes, bitacora):
    resultados = []
    for fuente in fuentes:
        id_cliente = fuente.get("id_cliente", "sin_id")
        segmento = fuente.get("segmento", "N/A")
        historial = fuente.get("historial", [])
        
        entrada = {
            "id_cliente": id_cliente,
            "segmento": segmento,
            "historial": historial
        }
        
        resultado = bloque_promociones_predictivas(entrada)
        
        if "error" not in resultado:
            resultados.append(resultado)
            bitacora.append(f"✔️ Promociones generadas para cliente {id_cliente}")
        else:
            bitacora.append(f"⚠️ Error con cliente {id_cliente}: {resultado['error']}")
    
    return resultados


# ✅ Función de prueba unitario (opcional para ejecución directa)
if __name__ == "__main__":
    cliente_prueba = {
        "id_cliente": "C123456",
        "segmento": "A",
        "historial": ["visita reciente", "reclamación reciente"]
    }

    print(bloque_promociones_predictivas(cliente_prueba))
