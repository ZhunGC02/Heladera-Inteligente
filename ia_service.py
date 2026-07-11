import os
from google import genai

def generar_receta_con_inventario(productos: list, api_key: str = None) -> str:
    """Toma la lista de productos del inventario y genera una receta usando la API Key provista."""
    if not productos:
        return "⚠️ No hay ingredientes en el inventario para generar una receta."

    # Resolver cuál API Key usar (Prioridad: la ingresada en la App > Variable de entorno)
    clave_final = api_key or os.getenv("GEMINI_API_KEY")

    if not clave_final:
        raise ValueError("No se encontró ninguna API Key válida para conectar con Gemini.")

    # Formatear la lista de ingredientes
    lista_formateada = []
    for p in productos:
        cat = p.get('categoria', 'General')
        venc = p.get('fecha_vencimiento') or 'N/A'
        info = f"- {p['nombre'].capitalize()} (Categoría: {cat}): {p['cantidad']} {p['unidad']} | Vence: {venc}"
        lista_formateada.append(info)
    
    texto_ingredientes = "\n".join(lista_formateada)

    prompt = f"""
    Eres un chef y nutricionista experto. Analiza el siguiente inventario de mi heladera y despensa:

    {texto_ingredientes}

    Por favor, sugiere una receta deliciosa combinando adecuadamente las proteínas, carbohidratos y verduras disponibles.
    Si faltan ingredientes secundarios básicos (como sal, pimienta, aceite o agua), asume que los tengo.

    Formatea la respuesta en Markdown con:
    1. 🍽️ Nombre de la receta.
    2. 📝 Ingredientes utilizados y sus cantidades aproximadas.
    3. 🍳 Modo de preparación paso a paso.
    4. 💡 Valor nutricional o sugerencias breves.
    """

    client = genai.Client(api_key=clave_final)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    return response.text