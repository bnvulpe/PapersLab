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

El proyecto tiene como objetivo ofrecer una conveniente estructura de datos sobre papers científicos y sus características específicas, proporcionando una estructura eficiente tanto para el procesamiento de datos como para su almacenamiento y análisis posterior, según las necesidades del cliente.

## Infraestructura

###Esquema general de la Infraestructura
![infrastructure_schema](https://github.com/bnvulpe/PapersLab/assets/77082096/c8ca5219-ba71-428f-9958-e1bc3b08df18)

En esta sección, se identifican y describen los componentes clave de la infraestructura, incluyendo los servicios de contenedores a utilizar.

### Microservicios de Extracción de Datos

La infraestructura se basa en microservicios diseñados para la extracción eficiente de datos de papers científicos utilizando múltiples claves API. Consiste en cuatro workers, cada uno asociado a una clave API específica de los miembros del grupo. Además de estos workers, se implementó un servicio adicional para la fusión de los datos extraídos por cada worker, de manera que finalicemos la etapa de extracción con un único archivo en formato JSON que contenga toda la información recabada.

Además, se implementa un volumen de Docker llamado "data" para almacenar los datos descargados, lo que facilita su posterior almacenamiento, tratamiento y manipulación en las siguientes etapas del proyecto (en diferentes servicios de almacenamiento y tratamiento de datos como Neo4j y Elasticsearch). La razón detrás la elección de estos servicios se fundamenta en los siguientes puntos:

- **Neo4j:** se trata de una base de datos de grafos que es ideal para modelar y representar relaciones complejas entre entidades, como los autores de los papers, las citas entre papers y las conexiones entre conceptos científicos. Al aprovechar la capacidad de Neo4j para almacenar datos en forma de grafos, pueden modelar fácilmente las relaciones entre los distintos atributos. Esto permite consultas eficientes para descubrir patrones y relaciones entre los datos.

- **Elasticsearch:** motor de búsqueda que puede ser utilizado para indexar y buscar los contenidos de los papers científicos, así como también para almacenar y consultar la información obtenida. Elasticsearch ofrece capacidades avanzadas de búsqueda de texto completo, agregaciones, análisis de datos y visualización, lo que facilita la extracción de información significativa de grandes conjuntos de datos no estructurados. Además, Elasticsearch es altamente escalable y tolerante a fallos, lo que lo hace adecuado para manejar grandes volúmenes de datos y cargas de trabajo distribuidas.

#### Estructura de Carpetas:

- **Carpeta coordinator:**
  - *coordinator.py:* Script que implementa un servidor TCP que espera a recibir mensajes de los contenedores de los workers y una vez que ha recibido tantos mensajes como workers activa el puerto 1234 en el que se ejecutarán los servicios wiki y crossref.
  - *Dockerfile:* Dockerfile que construye la imagen encargada de ejecutar el script *coordinator.py*.

- **Carpeta data:**
  - *coordinator.py:* Script que implementa  

- **Carpeta databases:**
  - *docker-compose.yml* levanta tres servicios: Neo4j, MySQL y Elasticsearch. Neo4j se configura en modo único, con autenticación, plugins, y puertos expuestos para interacción. MySQL se configura con credenciales de usuario, una base de datos específica, y expone el puerto estándar de MySQL.Conectando todos los servicios a una red externa llamada connection_network.
  - *initbd/init.sql* carga datos desde archivos CSV en tres tablas temporales separadas. Luego, mediante consultas de inserción, transfiere esos datos a una tabla principal llamada papers, actualizando registros existentes si es necesario. Finalmente, elimina las tablas temporales y verifica que los datos se hayan insertado correctamente en la tabla papers.

- **Carpeta dfs:**
  - *graph.ipynb:* script para procesar los datos utilizando PySpark. Realiza operaciones para unir, transformar y generar relaciones entre los datos de los documentos y los autores, y luego guarda esta información en archivos CSV para su posterior análisis. El script carga datos de archivos CSV y JSON, los une según identificadores únicos, crea relaciones entre documentos y autores, y extrae nodos individuales para documentos y autores. 
  - *crossref_service.ipynb:* Script que toma la información de un paper en formato JSON, extrae el nombre del publisher y realiza una búsqueda en la API Crossref para obtener su localización. Luego, añade estos datos, incluyendo el título original del paper y la localización del publisher, a un archivo CSV. Este proceso se realiza de forma asíncrona para manejar múltiples papers de manera eficiente. Además, aprovecha el módulo concurrent.futures.ThreadPoolExecutor para procesar los papers de forma concurrente.
  - *wiki-publishers.ipynb:* Script encargado de hacerla limpieza de los autores a partir de los ficheros JSON extraídos por los workers, acceder a la API de Wiki y guardar en un fichero CSV la información obtenida.
  - *init_elasticdb.ipynb:* Script que se encarga de conectar con Elasticsearch, crear un índice si no existe y luego cargar datos desde un archivo JSON en Elasticsearch. Una vez cargados los datos, realiza una consulta de búsqueda simple para verificar la carga exitosa.
  - *renaming.ipynb:* Este script renombra archivos CSV en función de sus ubicaciones actuales y los nuevos nombres proporcionados.
  - *run_notebooks.sh:* Este script ejecuta varios cuadernos Jupyter en paralelo. Luego, ejecuta en segundo plano los cuadernos "text_classification.ipynb", "time_data.ipynb" y "wiki-publishers.ipynb" utilizando jupyter nbconvert. Después, espera a que todos los procesos en segundo plano finalicen y ejecuta los cuadernos adicionales, "graph.ipynb" y "renaming.ipynb".
  - *text_classification.ipynb:* El script utiliza PySpark para leer datos de archivos JSON, luego llama a una API de Hugging Face para clasificar el contenido de cada documento. La clasificación se basa en el título del documento y utiliza un modelo específico de Hugging Face. El resultado de la clasificación se imprime y luego se guarda en un nuevo archivo CSV que contiene el ID del documento y el tema asignado por el modelo.
  - *time_data.ipynb:* El script utiliza PySpark para leer datos JSON y extraer el mes y el día de la semana de las fechas de publicación de documentos. Luego, guarda esta información en un archivo CSV.
    
- **Carpeta docker-configuration:**
  - *docker-compose.yml.template:* Template del Docker Compose utilizado para generar el archivo de configuración.
  - *docker_compose_configuration.py:* Script en Python que genera el Docker Compose deseado a partir del template, creando y asignando workers con las API keys correspondientes, junto a otras asignaciones automatizadas.
  - *Dockerfile:* Archivo para construir la imagen de Docker necesaria para ejecutar *docker_compose_configuration.py*.
  - *docker-compose.yml:* Docker Compose utilizado para montar la imagen anterior y crear el volumen donde se guardarán los datos.
  - *.env:* Archivo para almacenar las variables de entorno como BEGIN_YEAR, END_YEAR y CALL_LIMIT, personalizables por usuario.
  - *env_vars.txt:* Archivo de texto donde se encuentran las API keys (una en cada línea), asegurando un worker por cada key.

- **Carpeta merger:**
  - *Dockerfile:* Script que prepara un entorno para ejecutar una aplicación Python, asegurándose de que las dependencias y utilidades necesarias estén disponibles.
  - *merge.py:* Este script en Python combina múltiples archivos JSON en un único archivo JSON de salida.

- **Carpeta spark:**
  - *.env* Contiene la variable del entorno que determinará el numero de nodos de spark que tendrá el cluster montado
  - *build.sh* El script prepara un entorno Dockerizado para ejecutar un clúster de Spark con soporte de JupyterLab.
  - *cluster-base.Dockerfile* Este archivo Dockerfile crea una imagen de Docker basada en una versión ligera de Debian con Java Runtime Environment (JRE).
  - *docker-compose.yml* Configura un entorno de clúster con servicios de JupyterLab, Spark Master y Spark Worker. Define un volumen compartido llamado shared-workspace para almacenar datos persistentes y compartir archivos entre los servicios.
  - *jupyterlab.Dockerfile* El archivo prepara una imagen Docker para ejecutar JupyterLab en un entorno de clúster con soporte para Spark y otras bibliotecas necesarias.
  - *spark-base.Dockerfile* El archivo prepara una imagen Docker para ejecutar Apache Spark en un entorno de clúster.
  - *spark-defaults.conf* Estas configuraciones optimizan la gestión de eventos y registros en un entorno de Spark, mientras también establecen un límite en el número máximo de núcleos que pueden utilizarse.
  - *spark-master.Dockerfile* Extiende una imagen base de Spark para configurar un entorno que incluye herramientas adicionales y personalizaciones.
  - *spark-worker.Dockerfile* Extiende una imagen base de Spark para configurar un entorno de trabajador de Spark.

- **Carpeta worker:**
  - *worker.py:* Script encargado de la extracción de datos desde la API.
  - *requirements.txt:* Archivo que especifica las librerías necesarias para ejecutar el script.
  - *Dockerfile:* Dockerfile que construye la imagen responsable de ejecutar *worker.py* e instala las librerías especificadas en requirements.txt.

### Explicación de Componentes

- **Servicio de Extracción de Datos (Worker):** Este microservicio se encarga de la extracción de datos desde una API dada utilizando un conjunto de API keys. Su función principal es recolectar los datos necesarios de manera eficiente y confiable. 
  - *Contribución al manejo eficiente de datos:* El uso de varios workers distribuye la carga de trabajo y acelera el proceso de extracción de datos al paralelizar las solicitudes a la API. Esto optimiza el rendimiento y garantiza una extracción rápida y efectiva de grandes volúmenes de datos.
  - *Integración con otros componentes:* Los datos extraídos por cada worker se almacenan en un volumen Docker compartido, lo que permite un acceso uniforme a los datos desde otros componentes del sistema, como las bases de datos Elasticsearch y Neo4j.

- **Almacenamiento de Datos en Volúmenes Docker:** Los datos extraídos por los workers se almacenan en volúmenes Docker para facilitar su acceso desde otros servicios y garantizar su persistencia a lo largo del tiempo.
  - *Contribución al manejo eficiente de datos:* Almacenar los datos en volúmenes Docker permite un acceso rápido y eficiente a los mismos desde cualquier componente del sistema. Esto reduce la latencia y mejora el rendimiento en comparación con el almacenamiento en sistemas de archivos externos o bases de datos.
  - *Integración con otros componentes:* Los volúmenes Docker proporcionan una capa de abstracción para los datos, lo que simplifica su integración con otros servicios, como las bases de datos Elasticsearch y Neo4j.

- **Sistema de procesamiento distribuido(Spark):**
  Para enriquecer la información recopilada de los papers científicos, se implementa un proceso utilizando Apache Spark. Los datos almacenados en los volúmenes Docker son accedidos por los nodos del clúster Spark, permitiendo un procesamiento distribuido y eficiente.

  - *Escalabilidad:* Spark puede escalar fácilmente desde una sola máquina hasta miles de nodos, lo que le permite procesar grandes cantidades de datos de forma eficiente. Esta escalabilidad es esencial para manejar el elevado volumen de datos de artículos científicos y la información complementaria procedente de múltiples API.
  - *Tolerancia a fallos:* Los conjuntos de datos distribuidos resistentes (RDD) y las API DataFrame de Spark proporcionan tolerancia a fallos integrada. Si un nodo falla durante el procesamiento, Spark puede volver a calcular los datos perdidos utilizando la información de linaje, lo que garantiza la fiabilidad de las tareas de procesamiento.
  - *Rendimiento:* Al distribuir las tareas entre varios nodos, Spark puede realizar el procesamiento en paralelo, lo que reduce significativamente el tiempo necesario para la transformación y el análisis de los datos. Esto es crucial para cumplir los requisitos de rendimiento de las aplicaciones de big data. 

  - *Mejora en la Eficiencia del Sistema:* Al procesar los datos directamente desde los volúmenes Docker, se evita la necesidad de transferir grandes cantidades de datos a través de la red, lo que reduce la latencia y mejora el rendimiento general del sistema.
  - *Integración con Otros Componentes:* Los datos enriquecidos pueden ser fácilmente integrados con otros componentes del sistema, como bases de datos Elasticsearch, Neo4j y SQL aprovechando la capa de abstracción proporcionada por los volúmenes Docker.

- **Servicios de Bases de Datos (Elasticsearch, Neo4j y SQL):** Estos servicios almacenan y gestionan los datos de manera estructurada, lo que permite realizar consultas y análisis complejos sobre ellos.
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

En este apartado se aborda cómo las dimensiones del Big Data han sido abordadas y cómo estas decisiones simplifican la implementación de la infraestructura sin comprometer su funcionalidad.

Este proyecto se basa en las dimensiones clave del Big Data, como la velocidad, la veracidad y el valor, para ofrecer resultados óptimos. En términos de velocidad, hemos optado por tecnologías más económicas que permiten una flexibilidad mayor en el procesamiento de datos. Esto se traduce en la capacidad de extraer datos de manera eficiente y en tiempo real, tanto en procesos batch como en múltiples flujos de datos históricos. En cuanto a la veracidad, nos hemos centrado en garantizar la fiabilidad y autenticidad de los datos. Esto implica verificar la consistencia estadística y la fiabilidad de las API utilizadas, como Crossref, Wikidata y CoreAPI. Aseguramos la fiabilidad de los datos validando su origen, métodos de recopilación y procesamiento, así como la infraestructura de confianza utilizada. En cuanto al valor, nuestro enfoque se basa en ofrecer insights significativos y prácticos a partir de los datos recopilados, proporcionando un retorno de inversión tangible y beneficios tangibles para las partes interesadas.

Si bien hemos sacrificado la variedad de datos en favor del volumen y la variedad en el almacenamiento final, esta decisión simplifica la implementación de la infraestructura sin comprometer significativamente su funcionalidad.

- **Enfoque en Volumen y Variedad en el Almacenamiento Final:** Priorizamos la cantidad y diversidad de los datos procesados y almacenados. Esto simplifica la implementación al reducir la complejidad en la fase inicial de procesamiento, permitiendo un mayor énfasis en la cantidad de datos recopilados y la variedad de fuentes finales de almacenamiento, como Neo4j y Elasticsearch.

- **Formato JSON para los Datos Recopilados:** Optamos por conservar los datos en formato JSON, lo que simplifica el proceso de extracción y almacenamiento inicial. Este formato es fácilmente manipulable y compatible con la mayoría de las herramientas y plataformas de análisis de datos, reduciendo la complejidad en la fase inicial de procesamiento.

- **Almacenamiento de Información de Wikidata en Formato CSV:** Decidimos guardar la información obtenida de Wikidata en formato CSV, lo que muestra un enfoque pragmático para el análisis posterior. Facilita la manipulación y el análisis de estos datos específicos para el estudio geográfico previsto.

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
```bash
cd docker-configuration
```

Para POWERSHELL de Windows:
```bash

1. docker build -t docker_configuration .

2. $env:PWD_PARENT = (get-item -Path ".\").Parent.FullName;docker run -d --name docker_configuration -v PWD_PARENT:/app/project docker_configuration

3. docker ps -a --filter "name=docker_configuration" --format "{{.ID}}"

4. Utilice el output ID delpaso anterior : docker cp ID:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName

	example: docker cp eff65bf855b9:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName

5. cd ..

6. docker-compose up --build --detach

7. Una vez el servicio crossref haya finalizado su ejecución: docker-compose stop 
```

Para Linux/MacOS:
```bash

1. export PWD_PARENT=$(dirname "$(pwd)")

2. docker build -t docker_configuration .

3. docker run -d --name docker_configuration -v PWD_PARENT:/app/project docker_configuration

4. docker ps -a --filter "name=docker_configuration" --format "{{.ID}}"

5. Utilice el output ID delpaso anterior : docker cp ID:/app/docker-compose.yml $(dirname "$(pwd)")

	example: docker cp 5699c33389aa:/app/docker-compose.yml $(dirname "$(pwd)")

6. cd ..

7. docker-compose up --build --detach

8. Una vez el servicio crossref haya finalizado su ejecución: docker-compose stop 
```

## License

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.
