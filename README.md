# Evolution Notebook - Survival RPG

Un simulador de supervivencia "Roguelite" escrito en Python puro utilizando el motor `pygame`. Este proyecto se enfoca en entregar una experiencia desafiante mediante permadeath, recolección cruda de materiales, árboles genéticos, y un mundo duro y expansivo en diferentes biomas.

## ⛺ Características Principales
* **Panteón Genético y Metaprogresión:** La muerte no es el final. Los días sobrevividos se convierten en "Puntos Ancestrales" (PA), permitiendo comprar "Mutaciones" permanentes (Brazos de Gorila, Metabolismo Alto, etc.) que tu siguiente reencarnación heredará por default.
* **Sistema de Equipamiento (Paperdoll):** Personaliza tu `Arma`, `Tórax`, `Cabeza` y `Botas`. El avatar dibujado algorítmicamente vestirá y empuñará el botín visualmente con sus respectivos asensos estadísticos calculados en tiempo real.
* **Condiciones Adversas:** Enfrenta clima hostil generado procedimentalmente y lidia con enfermedades complejas como Disentería, Infección, Envenenamiento e Hipotermia según cómo trates tus heridas y lo que consumas.
* **Progresión de Asentamiento:** Funda desde una pequeña fogata (usando simple yesca y fibra) hasta levantar tiendas y, eventualmente, la Forja de la Edad de los Metales (Era 2).
* **Audio y Ambientes Reactivos:** Generador dinámico de pistas de fondo (BGM proc-gen) que reaccionan a los escenarios que exploras en tu aventura.

## 🚀 Requisitos de Instalación
Necesitas **Python 3.10+**. Clona este repositorio y en tu terminal desplázate a la carpeta raíz para instalar el motor libre.

```bash
pip install -r requirements.txt
```
*(Nota: Principalmente descargará `pygame`)*

## 🎮 Cómo Jugar
Simplemente levanta el archivo maestro y sumérgete en el bloc:
```bash
python main.py
```

## 🛠️ Sistemas y Crafting
El modo "Crafting" pide seleccionar **dos** ítems simultáneos del inventario. La lógica experimental de su uso imita lógicas físicas reales. Por ejemplo:
* `Pedernal` + `Fibra` = Cuchillo
* `Filtro de Grava` + `Agua Turbia` = Agua Limpia Purificada
* `Huesos` + `Piel` = Armadura Defensiva

## 🌍 Mundos Seguros (Al inicio)
Nacerás pacíficamente (Biomas: Sabana, Bosque Templado, Pradera). A medida que el explorador avance "Viajando" o persiguiendo "Landmarks", podrá transpirar accidentalmente o mudarse voluntariamente a Tundras infames, Eriales Volcánicos y Pantanos de asedio mortal. ¡Toma tus precauciones armando un campamento antes de viajar!

---
*Escrito como un homenaje rudimentario a las simulaciones darwinianas duras.*
