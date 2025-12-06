# Analizador de contratos IA
Aplicación en Gradio para analizar textos contractuales en español e inglés. Extrae cláusulas clave, detecta posibles riesgos con niveles de severidad y genera un resumen ejecutivo utilizando modelos de Hugging Face Transformers.
# 🚀 Características
- Detección automática del idioma (español/inglés).

- Extracción de cláusulas:

  - Pagos
  
  - Penalizaciones
  
  - Obligaciones
  
  - Confidencialidad
  
  - Terminación

- Detección de fechas dentro del contrato.

- Identificación de posibles riesgos clasificados por nivel: Bajo, Moderado, Alto, Crítico.

- Cada cláusula y riesgo incluye referencia a la posición en el texto [Ref X].

- Resumen automático del documento mediante sshleifer/distilbart-cnn-12-6.
# 🛠 Tecnologías utilizadas
- Python

- Gradio

- Hugging Face Transformers

- langdetect

- Expresiones regulares (regex)
# ✔ Nota
Este proyecto es una herramienta de apoyo para la revisión preliminar de contratos.

No constituye asesoramiento legal.
