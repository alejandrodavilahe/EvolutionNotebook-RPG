import random

TEMPLATES = {
    "MOVE": [
        "Avanzamos hacia {biome}, con pies cansados pero paso firme.",
        "El horizonte de {biome} nos desvela sus secretos.",
        "Nos adentramos en {biome}; la tierra parece hablarnos.",
        "Buscando un mejor futuro en {biome}... las leyendas dicen que es fértil.",
        "Cambio de aires: {biome}. El clan debe sobrevivir a este viaje."
    ],
    "SEARCH_SUCCESS": [
        "La tierra ha sido generosa. Mis manos están llenas de {item}.",
        "Entre la maleza y las rocas, la fortuna: {item}.",
        "He recolectado {item} para el grupo. Sabiduría de recolector.",
        "Hoy no pasaremos privaciones; {item} es un buen botín.",
        "Mis ojos no fallan: {item} estaba oculto en el paisaje."
    ],
    "SEARCH_EMPTY": [
        "Horas buscando bajo el sol y mis manos siguen vacías.",
        "El bioma de {biome} hoy no nos ha dado nada... frustrante.",
        "Nada más que tierra y viento. Debemos movernos pronto.",
        "La escasez nos aprieta el pecho. Mañana será otro día.",
        "He buscado en cada rincón, pero la abundancia nos huye."
    ],
    "FIGHT_WIN": [
        "La sangre de {enemy} mancha el suelo. Hemos triunfado.",
        "La fiera ha caído bajo mi voluntad. Mis manos tiemblan.",
        "Hoy no seremos presa; {enemy} ya no respira.",
        "Una lucha feroz contra {enemy}, pero el espíritu del clan es fuerte.",
        "El rugido de {enemy} se ha silenciado para siempre."
    ],
    "FIGHT_FLEE": [
        "El miedo fue más sabio. Huimos de las garras de {enemy}.",
        "No era nuestro momento. {enemy} vigila sus dominios... y corrimos.",
        "Escapamos por poco. El corazón me late en los oídos.",
        "A veces la sabiduría es saber cuándo retirarse ante {enemy}.",
        "La astucia nos salvó de {enemy}. Volveremos más fuertes."
    ],
    "REST": [
        "Cierro los ojos un momento... el descanso es sagrado.",
        "El cuerpo duele, pero la mente se despeja bajo el refugio.",
        "Reponiendo fuerzas tras un día de supervivencia agotador.",
        "Un respiro necesario. El mañana exigirá toda mi voluntad.",
        "Dormir bajo las estrellas recupera los músculos y el alma."
    ],
    "CRAFT": [
        "Hierba, piedra y hueso... así nace {item}.",
        "Mis manos han dado forma a {item}. Útil para lo que viene.",
        "Fabricando {item}. El ingenio es nuestra mejor arma.",
        "Un nuevo recurso terminado: {item}. La evolución no se detiene.",
        "Poco a poco, con paciencia, he terminado de forjar {item}."
    ],
    "HUNGER_LOW": [
        "El estómago gita vacío. Un hueco que me quita el aliento.",
        "El hambre... ese lobo hambriento que me muerde por dentro.",
        "Debo comer pronto o mis fuerzas me abandonarán.",
        "El delirio de la inanición empieza a nublar mi vista.",
        "Inanición. Mis manos fallan, los dioses exigen sustento."
    ],
    "THIRST_LOW": [
        "La garganta parece una herida abierta. Sed mortal.",
        "Buscando agua... o la arena será mi tumba.",
        "Mis labios se agrietan. Cada palabra arde como el fuego.",
        "Deshidratado. El espejismo del agua me atormenta.",
        "Sin agua, el mundo es solo ceniza y fuego."
    ],
    "ERA_TRANSITION": [
        "Un nuevo conocimiento nos inunda. La Era {era} amanece.",
        "Dejamos atrás lo viejo. El clan ha evolucionado.",
        "Ya no somos los mismos. {era} es nuestro nuevo hogar mental.",
        "El mundo parece distinto ahora... comprendemos más.",
        "A través de los milenios, hemos dado el paso definitivo."
    ]
}

def get_narrative(event_type, context={}, generation=1):
    if event_type not in TEMPLATES:
        return "Sucedió algo indefinido en el cuaderno."
    
    templates = TEMPLATES[event_type]
    raw_text = random.choice(templates)
    
    # Prefix de ancestros para Generations altas
    if generation > 1 and random.random() < 0.2:
        prefixes = ["Los antiguos decían: ", "Sabiduría del clan: ", "Mis abuelos sabían que ", "En el linaje se cuenta: "]
        raw_text = random.choice(prefixes) + raw_text[0].lower() + raw_text[1:]

    # Formatting
    try:
        return raw_text.format(**context)
    except KeyError as e:
        return raw_text # Fallback if context missing a key
