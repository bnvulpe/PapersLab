# PapersLab: Extracción, Procesamiento y Análisis de Papers Públicos

## Tabla de Contenidos

1. [Acerca de](#acerca-de)
2. [Infraestructura](#infraestructura)
   - [Microservicios de Extracción de Datos](#microservicios-de-extracción-de-datos)
     - [Estructura de Carpetas](#estructura-de-carpetas)
   - [Explicación de Componentes](#explicación-de-componentes)
     - [Servicio de Extracción de Datos (Worker)](#servicio-de-extracción-de-datos-worker)
     - [Almacenamiento de Datos en Volúmenes Docker](#almacenamiento-de-datos-en-volúmenes-docker)
     - [Servicios de Bases de Datos (MongoDB y Neo4j)](#servicios-de-bases-de-datos-mongodb-y-neo4j)
3. [Almacenamiento de Datos](#almacenamiento-de-datos)
   - [Volumen Docker para Almacenamiento](#volumen-docker-para-almacenamiento)
   - [Formato de Almacenamiento](#formato-de-almacenamiento)
     - [Justificación del Uso de JSON y CSV](#justificación-del-uso-de-json-y-csv)
4. [Garantía de Disponibilidad y Escalabilidad de los Datos](#garantía-de-disponibilidad-y-escalabilidad-de-los-datos)
5. [Decisiones de Diseño y Calidad](#decisiones-de-diseño-y-calidad)
   - [Eficiencia](#eficiencia)
   - [Escalabilidad](#escalabilidad)
   - [Fiabilidad](#fiabilidad)
   - [Gestión de la Carga](#gestión-de-la-carga)
6. [Alcance](#alcance)
7. [Instalación](#instalación)
8. [Uso](#uso)
9. [Licencia](#licencia)


## Acerca de

El proyecto tiene como objetivo automatizar la clasificación de contenido y la recuperación de conocimiento, así como realizar análisis sobre el impacto geográfico y temático en la investigación a lo largo del tiempo. Además, se contempla la posibilidad de realizar análisis de redes para analizar la comunicación superficial de referencia en la comunidad científica.

## Infraestructura

En esta sección, se identifican y describen los componentes clave de la infraestructura, incluyendo los servicios de contenedores a utilizar.

### Microservicios de Extracción de Datos

La infraestructura se basa en microservicios diseñados para la extracción eficiente de datos de papers científicos utilizando múltiples API keys. Consiste en cuatro workers, uno para cada API key asociada a los miembros del grupo. Además de estos workers, se han implementado dos servicios adicionales: uno para acceder a la API de wiki y obtener información de los publishers, y otro para acceder a la API de Crossref y obtener la ubicación de los publishers.

El objetivo de estos servicios adicionales es enriquecer los datos extraídos de las API de papers científicos con información adicional sobre los publishers, lo que puede ser útil para análisis posteriores. La integración de estos servicios amplía la funcionalidad de la infraestructura, permitiendo una recopilación más completa y enriquecida de los datos.

Además, se implementa un volumen de Docker llamado "data" para almacenar los datos descargados, lo que facilita su posterior almacenamiento, tratamiento y manipulación en las siguientes etapas del proyecto (en diferentes servicios de almacenamiento y tratamiento de datos como Neo4j y Elasticsearch). La razón detrás la elección de estos servicios se fundamenta en los siguientes puntos:

- **Neo4j:** se trata de una base de datos de grafos que es ideal para modelar y representar relaciones complejas entre entidades, como los autores de los papers, las citas entre papers y las conexiones entre conceptos científicos. Al aprovechar la capacidad de Neo4j para almacenar datos en forma de grafos, pueden modelar fácilmente las relaciones entre los distintos atributos. Esto permite consultas eficientes para descubrir patrones y relaciones entre los datos.

- **Elasticsearch:** motor de búsqueda que puede ser utilizado para indexar y buscar los contenidos de los papers científicos, así como también para almacenar y consultar la información obtenida de la API de Wiki. Elasticsearch ofrece capacidades avanzadas de búsqueda de texto completo, agregaciones, análisis de datos y visualización, lo que facilita la extracción de información significativa de grandes conjuntos de datos no estructurados. Además, Elasticsearch es altamente escalable y tolerante a fallos, lo que lo hace adecuado para manejar grandes volúmenes de datos y cargas de trabajo distribuidas.

#### Estructura de Carpetas:

- **Carpeta docker-configuration:**
  - *docker-compose.yml.template:* Template del Docker Compose utilizado para generar el archivo de configuración.
  - *docker_compose_configuration.py:* Script en Python que genera el Docker Compose deseado a partir del template, creando y asignando workers con las API keys correspondientes.
  - *Dockerfile:* Archivo para construir la imagen de Docker necesaria para ejecutar *docker_compose_configuration.py*.
  - *docker-compose.yml:* Docker Compose utilizado para montar la imagen anterior y crear el volumen donde se guardarán los datos.
  - *.env:* Archivo para almacenar las variables de entorno como BEGIN_YEAR, END_YEAR y CALL_LIMIT.
  - *env_vars.txt:* Archivo de texto donde se encuentran las 4 API keys (una en cada línea).

- **Carpeta worker:**
  - *worker.py:* Script encargado de la extracción de datos desde la API.
  - *requirements.txt:* Archivo que especifica las librerías necesarias para ejecutar el script.
  - *Dockerfile:* Dockerfile que construye la imagen responsable de ejecutar *worker.py* e instala las librerías especificadas en requirements.txt.

- **Carpeta wiki:**
  - *wiki.py:* Script encargado de hacerla limpieza de los autores a partir de los ficheros JSON extraídos por los workers, acceder a la API de Wiki y guardar en un fichero CSV la información obtenida. 
  - *wait-for-it.sh:* Script Bash que pimplementa la espera a que el host y el puerto 1234 (abierto mediante el coordinador) estén disponibles para continuar con la ejecución de este microservicio.
  - *requirements.txt:* Archivo que especifica las librerías necesarias para ejecutar el script.
  - *Dockerfile:* Dockerfile que construye la imagen que ejecuta *wait-for-it.sh*, instala las librerías necesarias especificadas en el fichero requirements.txt y ejecuta el script *wiki.py*.

- **Carpeta crossref:**
  - *crossref.py:* Script que toma la información de un paper en formato JSON, extrae el nombre del publisher y realiza una búsqueda en la API Crossref para obtener su localización. Luego, añade estos datos, incluyendo el título original del paper y la localización del publisher, a un archivo CSV. Este proceso se realiza de forma asíncrona para manejar múltiples papers de manera eficiente. Además, aprovecha el módulo concurrent.futures.ThreadPoolExecutor para procesar los papers de forma concurrente.
  - *wait-for-it.sh:* Similar al de la carpeta wiki
  - *requirements.txt:* Archivo que especifica las librerías necesarias para ejecutar el script.
  -  *Dockerfile:* Dockerfile que construye la imagen que ejecuta *wait-for-it.sh*, instala las librerías necesarias especificadas en el fichero requirements.txt y ejecuta el script *crossref.py*.

- **Carpeta coordinator:**
  - *coordinator.py:* Script que implementa un servidor TCP que espera a recibir mensajes de los contenedores de los workers y una vez que ha recibido tantos mensajes como workers activa el puerto 1234 en el que se ejecutarán los servicios wiki y crossref.
  - *Dockerfile:* Dockerfile que construye la imagen encargada de ejecutar el script *coordinator.py*.

### Explicación de Componentes

- **Servicio de Extracción de Datos (Worker):** Este microservicio se encarga de la extracción de datos desde una API dada utilizando un conjunto de API keys. Su función principal es recolectar los datos necesarios de manera eficiente y confiable. 
  - *Contribución al manejo eficiente de datos:* El uso de varios workers distribuye la carga de trabajo y acelera el proceso de extracción de datos al paralelizar las solicitudes a la API. Esto optimiza el rendimiento y garantiza una extracción rápida y efectiva de grandes volúmenes de datos.
  - *Integración con otros componentes:* Los datos extraídos por cada worker se almacenan en un volumen Docker compartido, lo que permite un acceso uniforme a los datos desde otros componentes del sistema, como las bases de datos Elasticsearch y Neo4j.

- **Almacenamiento de Datos en Volúmenes Docker:** Los datos extraídos por los workers se almacenan en volúmenes Docker para facilitar su acceso desde otros servicios y garantizar su persistencia a lo largo del tiempo.
  - *Contribución al manejo eficiente de datos:* Almacenar los datos en volúmenes Docker permite un acceso rápido y eficiente a los mismos desde cualquier componente del sistema. Esto reduce la latencia y mejora el rendimiento en comparación con el almacenamiento en sistemas de archivos externos o bases de datos.
  - *Integración con otros componentes:* Los volúmenes Docker proporcionan una capa de abstracción para los datos, lo que simplifica su integración con otros servicios, como las bases de datos Elasticsearch y Neo4j.

- **Servicios de Bases de Datos (Elasticsearch y Neo4j):** Estos servicios almacenan y gestionan los datos de manera estructurada, lo que permite realizar consultas y análisis complejos sobre ellos.
  - *Contribución al manejo eficiente de datos:* Las bases de datos Elasticsearch y Neo4j están diseñadas para manejar grandes volúmenes de datos de manera eficiente. Proporcionan capacidades de indexación, consultas optimizadas y almacenamiento escalable que facilitan el acceso y la manipulación de los datos de forma eficiente.
  - *Integración con otros componentes:* Los datos almacenados en los volúmenes Docker pueden ser fácilmente cargados en las bases de datos Elasticsearch y Neo4j para su análisis posterior. Estos servicios proporcionan interfaces de programación y consultas que permiten acceder a los datos de manera programática desde otros servicios, como Jupyter y Spark.

- **Servicio de Coordinador:**  Este microservicio actúa como un orquestador, asegurando que los servicios se ejecuten en el orden adecuado y proporcionando una señal para habilitar la ejecución de servicios subsiguientes (wiki y crossref) una vez que los workers han completado su tarea.
  - *Contribución al manejo eficiente de datos:* El servicio de coordinador garantiza un flujo eficiente de trabajo al asegurar que los diferentes servicios se ejecuten en el orden correcto, minimizando el tiempo de inactividad y maximizando la utilización de los recursos disponibles. Asimismo, permite una gestión eficiente de los datos al controlar la secuencia de ejecución de los servicios, lo que asegura que los datos se procesen y enriquezcan de manera oportuna y coherente.
  - *Integración con otros componentes:* Se integra estrechamente con los workers encargados de la extracción de datos de las API de papers científicos, coordinando su ejecución y proporcionando una señal para habilitar la ejecución de servicios subsiguientes. Coordina la ejecución de los servicios adicionales que acceden a la wiki y a la API de Crossref, asegurando que se realicen después de que los workers hayan completado su tarea. Por último, interactúa con el volumen de Docker llamado "data" para acceder a los datos descargados y facilitar su posterior procesamiento y manipulación en los servicios subsiguientes de almacenamiento y tratamiento de datos.

## Almacenamiento de Datos

En esta sección, se propone una solución para el almacenamiento en crudo de los datos, optimizando el acceso y la recuperación de información.

#### Volumen Docker para Almacenamiento

Los datos extraídos se almacenarán en un volumen Docker denominado "data". Este enfoque garantiza un acceso centralizado y sencillo desde todos los servicios de bases de datos que se utilizarán, como Neo4j y Elasticsearch, así como desde herramientas de análisis como Jupyter, ElasticSearch y Spark.

- **Centralización y Simplificación:** Al almacenar los datos en un volumen Docker, garantizamos un acceso centralizado desde todos los servicios de bases de datos que utilizaremos, así como desde herramientas de análisis. Esto simplifica la gestión y evita la duplicación de datos en diferentes ubicaciones.

- **Agilidad en la Manipulación:** Se elimina la necesidad de transferir los datos entre diferentes sistemas de archivos o dispositivos de almacenamiento, agilizando el proceso de manipulación y análisis.

- **Escalabilidad:** Los volúmenes Docker son altamente escalables y pueden crecer según las necesidades del proyecto. Esta flexibilidad nos permite adaptarnos a cambios en el volumen de datos sin comprometer el rendimiento del sistema.

#### Formato de Almacenamiento

Dado que se requerirá acceso programático a los datos a través de diferentes herramientas y servicios, proponemos almacenar los datos tanto en formato JSON como en formato CSV, dependiendo de su naturaleza y necesidades específicas.

##### Justificación del Uso de JSON y CSV:

- **JSON (JavaScript Object Notation):**
    - **Estructura Flexible:** Adecuado para representar datos estructurados y semiestructurados, facilitando su manipulación y análisis posterior en herramientas como Jupyter y Spark.
    - **Compatibilidad con Diversas Plataformas:** Ampliamente compatible y puede ser procesado por una variedad de herramientas y lenguajes de programación, garantizando una interoperabilidad sin problemas en diferentes entornos de desarrollo.
    - **Legibilidad y Mantenibilidad:** Legible tanto para humanos como para máquinas, lo que simplifica la comprensión de la estructura y los atributos de los datos, facilitando el desarrollo y mantenimiento del sistema.

- **CSV (Comma-Separated Values):**
    - **Ideal para Datos Tabulares:** Simplifica la importación de datos en bases de datos relacionales y no relacionales, como Elasticsearch y Neo4j, permitiendo una integración más fácil con las diferentes bases de datos que se utilizarán en la segunda parte de la práctica.

Esta solución proporciona una solución robusta y eficiente que optimiza el acceso, la manipulación y la recuperación de información, preparándonos para la siguiente fase de la práctica donde se realizará el tratamiento, manipulación y almacenamiento de los datos extraídos. El uso de un volumen Docker y la selección de formatos de almacenamiento adecuados aseguran un acceso programático sencillo y optimizado a los datos desde diversas herramientas y servicios.

## Garantía de Disponibilidad y Escalabilidad de los Datos

En el sistema propuesto, la disponibilidad y escalabilidad de los datos se garantizan mediante una arquitectura basada en microservicios respaldada por el uso de volúmenes Docker. Esta combinación de tecnologías proporciona una infraestructura robusta y flexible para asegurar el acceso continuo a los datos y su escalabilidad según las necesidades del sistema.

La implementación de microservicios permite descomponer la aplicación en componentes independientes, cada uno encapsulando su propia lógica de negocio y datos. Al utilizar volúmenes Docker para almacenar los datos de estos microservicios, se asegura que los datos estén disponibles para cada instancia del servicio, incluso en casos de fallos o reinicios de los contenedores. Esto garantiza una alta disponibilidad de datos, ya que cada instancia tiene acceso al mismo estado persistente a través del volumen compartido.

Además, la arquitectura basada en microservicios facilita la escalabilidad del sistema. Al escalar horizontalmente los microservicios para manejar una carga de trabajo creciente, los volúmenes Docker aseguran que cada instancia del servicio tenga acceso a los mismos datos almacenados en el volumen compartido. Esto permite una escalabilidad fluida y sin interrupciones, ya que todas las instancias comparten el mismo estado de datos.

Por lo tanto, mediante la combinación de microservicios y volúmenes Docker, se garantiza una alta disponibilidad y escalabilidad de los datos en el sistema propuesto. Esta arquitectura proporciona una base sólida para satisfacer las demandas cambiantes de capacidad y carga de trabajo, asegurando el acceso continuo y eficiente a los datos en todo momento.

## Decisiones de Diseño y Calidad

En este apartado, se abordan las decisiones de diseño que se fundamentan en los principios de calidad para infraestructuras virtuales, como la eficiencia, la escalabilidad, la fiabilidad y la gestión de la carga.

#### Eficiencia

- **Uso de Múltiples Workers:** La implementación de múltiples workers distribuye la carga de trabajo de extracción de datos, permitiendo un procesamiento más eficiente y rápido. Esto garantiza un uso más efectivo de los recursos disponibles y reduce el tiempo total de extracción de datos.

- **Utilización de Contenedores Docker:** La elección de usar contenedores Docker proporciona un entorno ligero y eficiente para ejecutar aplicaciones. Al compartir el mismo kernel del sistema operativo del host, los contenedores minimizan el sobrecosto y permiten una mayor portabilidad de las aplicaciones entre diferentes entornos.

- **Almacenamiento de Datos en Volúmenes Docker:** Al optar por almacenar los datos en volúmenes Docker, se optimiza el acceso a los datos y se reduce la latencia. Esto mejora la eficiencia de las operaciones de lectura y escritura en comparación con el acceso a través de una red.

#### Escalabilidad

- **Orquestación Mediante Docker Compose:** La utilización de Docker Compose facilita la gestión y escalabilidad de los servicios. La infraestructura puede escalar verticalmente agregando más recursos a cada worker o horizontalmente agregando más workers según sea necesario para manejar mayores volúmenes de datos.

- **Uso de Volúmenes Docker:** Al utilizar volúmenes Docker para almacenar datos, se facilita la escalabilidad horizontal. Esto permite la adición o eliminación dinámica de contenedores sin afectar la disponibilidad de los datos, lo que permite adaptarse rápidamente a cambios en la demanda del sistema.

#### Fiabilidad

- **Tolerancia a Fallos:** La distribución de la carga de trabajo entre varios workers aumenta la redundancia y la tolerancia a fallos. Si un worker falla, los otros pueden continuar ejecutándose, lo que garantiza la disponibilidad y la fiabilidad del sistema en general.

- **Gestión de Fallos:** A través del monitoreo constante de los workers y la implementación de estrategias de recuperación, se garantiza una gestión efectiva de fallos para mantener la estabilidad del sistema.

#### Gestión de la Carga

- **Distribución Equitativa de la Carga:** La asignación equitativa de trabajos a los workers evita la sobrecarga de un worker específico. Esto garantiza una distribución uniforme de la carga de trabajo y optimiza el rendimiento del sistema en su conjunto.

## Alcance

En este apartado se aborda qué dimensiones del Big Data se han sacrificado, si es el caso, y cómo esta decisión simplifica la implementación de la infraestructura sin comprometer significativamente su funcionalidad.

Si bien en nuestro servicio se ha sacrificado la variedad de datos en favor del volumen y la variedad en el proceso final de almacenamiento, esta decisión simplifica la implementación de la infraestructura sin comprometer significativamente su funcionalidad.

- **Enfoque en Volumen y Variedad en el Almacenamiento Final:** Esta decisión prioriza la cantidad y diversidad de los datos procesados y almacenados. Se simplifica la implementación al reducir la complejidad en la fase inicial de procesamiento, permitiendo un mayor énfasis en la cantidad de datos recopilados y la variedad de fuentes finales de almacenamiento, como Neo4j y Elasticsearch.

- **Formato JSON para los Datos Recopilados:** La elección de conservar los datos en formato JSON simplifica el proceso de extracción y almacenamiento inicial. Este formato es fácilmente manipulable y compatible con la mayoría de las herramientas y plataformas de análisis de datos, reduciendo la complejidad en la fase inicial de procesamiento.

- **Almacenamiento de Información de Wikidata en Formato CSV:** Optar por guardar la información obtenida de Wikidata en formato CSV muestra un enfoque pragmático para el análisis posterior. Facilita la manipulación y el análisis de estos datos específicos para el estudio geográfico previsto.

En resumen, el enfoque en el volumen y la variedad en el proceso final de almacenamiento simplifica la implementación de la infraestructura al reducir la complejidad en las etapas iniciales de extracción y almacenamiento, al tiempo que facilita la integración y el análisis posterior de los datos recopilados.

## Instalación

Para comenzar con este proyecto, puedes descargarlo desde el repositorio de GitHub. Puedes hacerlo haciendo clic en el botón "Code" y luego seleccionando "Download ZIP". Una vez descargado, extrae el contenido del archivo ZIP en la ubicación deseada.

Alternativamente, puedes clonar el repositorio usando Git. Abre tu terminal o símbolo del sistema y ejecuta el siguiente comando:

```bash
git clone https://https://github.com/bnvulpe/PapersLab.git
```
## Uso

Después de descargar o clonar el repositorio, navega hasta el directorio del proyecto en tu terminal o símbolo del sistema.

Una vez ubicado en la carpeta docker-configuration:

Para POWERSHELL de Windows:

1. $env:PWD_PARENT = (Get-Item -Path ".\").Parent.FullName; docker-compose up --build --detach 

2. docker ps -a --filter "name=docker_configuration" --format "{{.ID}}"

3. Utilice el output ID delpaso anterior : docker cp ID:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName

	example: docker cp 37f7a096ea63:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName

4. cd ..

6. docker-compose up --build --detach

7. Una vez el servicio crossref haya finalizado su ejecución: docker-compose stop 

Para Linux/MacOS:

1. export PWD_PARENT=$(dirname "$(pwd)")

2. docker-compose up --build --detach 

3. docker ps -a --filter "name=docker_configuration" --format "{{.ID}}"

4. Utilice el output ID delpaso anterior : docker cp ID:/app/docker-compose.yml $(dirname "$(pwd)")

	example: docker cp 37f7a096ea63:/app/docker-compose.yml $(dirname "$(pwd)")

5. cd ..

7. docker-compose up --build --detach

8. Una vez el servicio crossref haya finalizado su ejecución: docker-compose stop 

## License

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.
