# Evolution Notebook - Survival RPG

Un simulador de supervivencia "Roguelite" escrito en Python puro utilizando el motor `pygame-ce`. Este proyecto se enfoca en entregar una experiencia desafiante mediante permadeath, recolección cruda de materiales, árboles genéticos, y un mundo duro y expansivo en diferentes biomas.

## ⛺ Características Principales
* **Panteón Genético y Metaprogresión:** La muerte no es el final. Los días sobrevividos se convierten en "Puntos Ancestrales" (PA), permitiendo comprar "Mutaciones" permanentes que tu siguiente reencarnación heredará.
* **Sistema de Equipamiento Evolutivo:** El avatar del jugador es un boceto que evoluciona físicamente (postura y detalle) según la Era y el equipo que vistas.
* **Atmósfera de Diario Realista:** La interfaz emula un diario antiguo de cuero. La lluvia humedece el papel, el polvo se asienta en las páginas y la tinta roja (sangre) mancha la libreta tras los combates.
* **Crónica del Clan:** Notas manuscritas aparecen en los márgenes narrando tus hitos, derrotas y la sabiduría de tus ancestros.
* **Sistema de Descubrimiento (I+D):** No basta con tener materiales. Debes desbloquear conceptos (Espiritualidad, Trampeo, Curación) mediante hitos de juego para acceder a recetas avanzadas.
* **Eventos de Migración:** Manadas de Mamuts y Bisontes aparecen dinámicamente en el mapa, ofreciendo grandes recompensas y peligros.

## 🚀 Requisitos de Instalación
Necesitas **Python 3.10+**. Este proyecto es compatible con las versiones más recientes de Python (incluyendo 3.14) gracias al uso de `pygame-ce`.

```bash
pip install -r requirements.txt
```
*(Nota: Instalará `pygame-ce` para máxima compatibilidad y rendimiento)*

## 🎮 Cómo Jugar
Simplemente levanta el archivo maestro y sumérgete en el bloc:
```bash
python main.py
```

## 🛠️ Sistemas y Crafting
El modo "Crafting" pide seleccionar **dos** ítems simultáneos del inventario. Pero cuidado: las recetas de Era 2 y rituales requieren que primero **descubras** el concepto adecuado.
* `Pedernal` + `Huesos` = Cuchillo (Requiere Manejo del Fuego para la Forja)
* `Milenrama` + `Agua` = Curación (Desbloquea el concepto de Medicina)
* `Piedra` + `Carbón` = Tótem (Requiere haber descubierto la Espiritualidad)

## 🌍 Mundos y Peligros
Nacerás en biomas pacíficos, pero la exploración te llevará a Tundras infames y Pantanos mortales. El clima afectará no solo tu estado, sino la legibilidad y el estado físico de tu cuaderno de bitácora.

---
*Escrito como un homenaje rudimentario a las simulaciones darwinianas duras.*
