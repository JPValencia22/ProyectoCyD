# Proyecto de Portal de Búsqueda de Genes en Vino

Este proyecto tiene como objetivo la creación de un portal web que permita la consulta eficiente de datos genéticos de uvas, provenientes de dos tipos de vino: Chardonnay y Cabernet. 
La empresa chilena que ha realizado una inversión en el análisis de genes de sus uvas necesita un sistema que facilite la visualización y búsqueda de los resultados encontrados por su equipo de investigadores en bioinformática.

## Requisitos

El proyecto cumple con los siguientes puntos:

1. **Registro de usuarios**: Proteger la información de los tipos de vino mediante un sistema de registro de usuarios.
2. **Autenticación**: Al registrarse, el usuario recibe una llave de seguridad enviada por correo electrónico. El envío se gestiona mediante el patrón `publisher/subscriber` usando RabbitMQ.
3. **Estrategia de almacenamiento**: Se debe crear una estrategia para almacenar los archivos de los investigadores y permitir la carga de nuevos archivos.
4. **Paginación**: El buscador debe estar paginado para gestionar grandes volúmenes de datos de manera eficiente.
5. **Paralelización**: La consulta y envío de resultados debe realizarse de forma paralela para optimizar el rendimiento.
6. **Ordenación de resultados**: Los resultados deben poder ordenarse por las columnas de la tabla.
7. **Carga de archivos**: Crear un endpoint para cargar archivos al backend mediante `curl`.
8. **Columnas del buscador**: El sistema debe mostrar las siguientes columnas:
   - `Chrom`
   - `Pos`
   - `Id`
   - `Ref`
   - `Alt`
   - `Qual`
   - `Filter`
   - `Info`
   - `Format`
   - `Outputs` (Variables específicas para cada archivo)
9. **Campos de búsqueda**: Los usuarios pueden buscar por las siguientes columnas:
   - `Chrom`
   - `Filter`
   - `Info`
   - `Format`

## Tecnologías Utilizadas

- **Lenguaje**: Python
- **RabbitMQ**: Utilizado para gestionar la mensajería entre componentes.
- **Gmail API**: Para el envío de correos electrónicos de validación y autenticación.
- **MongoDB**: Se usa de manera local, sirve para guardar los archivos, además, también se guardan los usuarios registrados.
- **Paginación y paralelización**: Implementación de técnicas para manejar grandes volúmenes de datos de manera eficiente.

## Instalación

Para instalar y ejecutar el proyecto en tu entorno local, sigue estos pasos:

**Prerrequisitos:**
- Tener Python instalado y pip funcional.
- Tener MongoDBCompass instalado y con su respectivo servicio funcionando.
- Tener instalado RabbitMQ instalado y con su respectivo servicio funcionando.

1. Clona el repositorio:
   ```bash
   git clone https://github.com/JPValencia22/ProyectoCyDBack.git
   cd ProyectoCyDBack
   
2. Crea un entorno virtual y actívalo:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # En Windows usa venv\Scripts\activate

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt

4. Agrega un archivo llamado .env en la carpeta raíz del proyecto. Allí guardarás tus variables de entorno. La estructura que se requiere es:
   ```.env
   AMAZON_USER=tu_correo_electronico
   AMAZON_PASSWORD=tu_contraseña
   ```
   La contraseña debe ser una contraseña de aplicación, puedes crearla ingresando con tu correo en el siguiente enlace:
   https://accounts.google.com/v3/signin/challenge/pwd?TL=AE--Llz1OREx8QVkb1h-Jam_-WSDyWO7mSZIOFrtP78C3UJE8Hg-Pq8fQju3Z6kR&cid=2&continue=https%3A%2F%2Fmyaccount.google.com%2Fapppasswords&flowName=GlifWebSignIn&followup=https%3A%2F%2Fmyaccount.google.com%2Fapppasswords&ifkv=AeZLP98BIh8eOxZz7luJSoOj5zkDeZWXe-RalbwoD_uf5RBomdKwQ-qK4WWbtTxgAHk5iRo--kuF&osid=1&rart=ANgoxccq8Mf4EhlRe-KlGmutV9Zq2QsYLKI7TfnJIapmEpXJu80rpvLPGEGzvIsrvjrecSa9EsBiuQcejWphKh2ptM2jniQjSszpPe1oK_dSk7i2-UsGtr4&rpbg=1&service=accountsettings
