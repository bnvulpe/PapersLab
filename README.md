# PapersLab: Extracción, Procesamiento y Análisis de Papers Públicos
# Índice

1. [Introducción](#introducción)
2. [Almacenamiento de Datos](#almacenamiento-de-datos)
   - [Volumen Docker para Almacenamiento](#volumen-docker-para-almacenamiento)
   - [Formato de Almacenamiento](#formato-de-almacenamiento)
     - [Justificación del Uso de JSON y CSV](#justificación-del-uso-de-json-y-csv)
3. [Instalación](#instalación)
4. [Uso](#uso)
5. [Licencia](#licencia)

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

La infraestructura se basa en microservicios diseñados para la extracción eficiente de datos de papers científicos utilizando múltiples claves API. Consiste en cuatro workers, cada uno asociado a una clave API específica de los miembros del grupo. Además de estos workers, se implementó un servicio adicional para la fusión de los datos extraídos por cada worker, de manera que finalicemos la etapa de extracción con un único archivo en formato JSON que contenga toda la información.

Además, se implementa un volumen de Docker para almacenar los datos descargados, lo que facilita su posterior almacenamiento, tratamiento y manipulación en las siguientes etapas del proyecto (en diferentes servicios de almacenamiento y tratamiento de datos como Neo4j y Elasticsearch). La razón detrás la elección de estos servicios se fundamenta en los siguientes puntos:

- **Neo4j:** se trata de una base de datos de grafos que es ideal para modelar y representar relaciones complejas entre entidades, como los autores de los papers, las citas entre papers y las conexiones entre conceptos científicos. Al aprovechar la capacidad de Neo4j para almacenar datos en forma de grafos, pueden modelar fácilmente las relaciones entre los distintos atributos. Esto permite consultas eficientes para descubrir patrones y relaciones entre los datos.

- **Elasticsearch:** motor de búsqueda que puede ser utilizado para indexar y buscar los contenidos de los papers científicos, así como también para almacenar y consultar la información obtenida. Elasticsearch ofrece capacidades avanzadas de búsqueda de texto completo, agregaciones, análisis de datos y visualización, lo que facilita la extracción de información significativa de grandes conjuntos de datos no estructurados. Además, Elasticsearch es altamente escalable y tolerante a fallos, lo que lo hace adecuado para manejar grandes volúmenes de datos y cargas de trabajo distribuidas.

#### Estructura de Carpetas:

- **Carpeta coordinator:**
  - *coordinator.py:* Script que implementa un servidor TCP que espera a recibir mensajes de los contenedores de los workers y una vez que ha recibido tantos mensajes como workers activa el puerto 1234 en el que se ejecutarán los servicios wiki y crossref.
  - *Dockerfile:* Dockerfile que construye la imagen encargada de ejecutar el script *coordinator.py*.
    
- **Carpeta databases:**
  - *docker-compose.yml* levanta tres servicios: Neo4j, MySQL y Elasticsearch. Neo4j se configura en modo único, con autenticación, plugins, y puertos expuestos para interacción. MySQL se configura con credenciales de usuario, una base de datos específica, y expone el puerto estándar de MySQL.
  - *initbd/init.sql* carga datos desde archivos CSV en tres tablas temporales separadas. Luego, mediante consultas de inserción, transfiere esos datos a una tabla principal llamada papers, actualizando registros existentes si es necesario. Finalmente, elimina las tablas temporales y verifica que los datos se hayan insertado correctamente en la tabla papers.

- **Carpeta dfs:**
  - *graph.ipynb:* script para procesar los datos utilizando PySpark. Realiza operaciones para unir, transformar y generar relaciones entre los datos de los documentos y los autores, y luego guarda esta información en archivos CSV para su posterior análisis. El script carga datos de archivos CSV y JSON, los une según identificadores únicos, crea relaciones entre documentos y autores, y extrae nodos individuales para documentos y autores. 
  - *crossref_service.ipynb:* Script que toma la información de un paper en formato JSON, extrae el nombre del publisher y realiza una búsqueda en la API Crossref para obtener su localización. Luego, añade estos datos, incluyendo el título original del paper y la localización del publisher, a un archivo CSV. Este proceso se realiza de forma asíncrona para manejar múltiples papers de manera eficiente. Además, aprovecha el módulo concurrent.futures.ThreadPoolExecutor para procesar los papers de forma concurrente. Por el tiempo de ejecución no se ejecuta en el workflow final.
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
  - *Integración con otros componentes:* Los datos extraídos por cada worker se almacenan en un volumen Docker compartido, lo que permite un acceso uniforme a los datos desde otros componentes del sistema, como las bases de datos Elasticsearch, MySQL y Neo4j.

- **Servicio de Coordinador:**  Este microservicio actúa como un orquestador, asegurando que los servicios se ejecuten en el orden adecuado y proporcionando una señal para habilitar la ejecución de servicios subsiguientes (wiki y crossref) una vez que los workers han completado su tarea.
  - *Contribución al manejo eficiente de datos:* El servicio de coordinador garantiza un flujo eficiente de trabajo al asegurar que los diferentes servicios se ejecuten en el orden correcto, minimizando el tiempo de inactividad y maximizando la utilización de los recursos disponibles. Asimismo, permite una gestión eficiente de los datos al controlar la secuencia de ejecución de los servicios, lo que asegura que los datos se procesen y enriquezcan de manera oportuna y coherente.
  - *Integración con otros componentes:* Se integra estrechamente con los workers encargados de la extracción de datos de las API de papers científicos, coordinando su ejecución y proporcionando una señal para habilitar la ejecución de servicios subsiguientes. Coordina la ejecución de los servicios adicionales que acceden a la wiki y a la API de Crossref, asegurando que se realicen después de que los workers hayan completado su tarea. Por último, interactúa con el volumen de Docker llamado "data" para acceder a los datos descargados y facilitar su posterior procesamiento y manipulación en los servicios subsiguientes de almacenamiento y tratamiento de datos.

- **Almacenamiento de Datos en Volúmenes Docker:** Los datos extraídos por los workers se almacenan en volúmenes Docker para facilitar su acceso desde otros servicios y garantizar su persistencia a lo largo del tiempo.
  - *Contribución al manejo eficiente de datos:* Almacenar los datos en volúmenes Docker permite un acceso rápido y eficiente a los mismos desde cualquier componente del sistema. Esto reduce la latencia y mejora el rendimiento en comparación con el almacenamiento en sistemas de archivos externos o bases de datos.
  - *Integración con otros componentes:* Los volúmenes Docker proporcionan una capa de abstracción para los datos, lo que simplifica su integración con otros servicios, como las bases de datos Elasticsearch y Neo4j.

- **Sistema de procesamiento distribuido(Spark):**
  Para enriquecer la información recopilada de los papers científicos, se implementa un proceso utilizando Apache Spark. Los datos almacenados en los volúmenes Docker son accedidos por los nodos del clúster Spark, permitiendo un procesamiento distribuido y eficiente.

  - *Escalabilidad:* Spark puede escalar fácilmente desde una sola máquina hasta miles de nodos, lo que le permite procesar grandes cantidades de datos de forma eficiente. Esta escalabilidad es esencial para manejar el elevado volumen de datos de artículos científicos y la información complementaria procedente de múltiples API.
  - *Tolerancia a fallos:* Los conjuntos de datos distribuidos resistentes (RDD) y las API DataFrame de Spark proporcionan tolerancia a fallos integrada. Si un nodo falla durante el procesamiento, Spark puede volver a calcular los datos perdidos utilizando la información de linaje, lo que garantiza la fiabilidad de las tareas de procesamiento.
  - *Rendimiento:* Al distribuir las tareas entre varios nodos, Spark puede realizar el procesamiento en paralelo, lo que reduce significativamente el tiempo necesario para la transformación y el análisis de los datos. Esto es crucial para cumplir los requisitos de rendimiento de las aplicaciones de big data. 

- **Servicios de Bases de Datos** Estos servicios almacenan y gestionan los datos de manera estructurada, lo que permite realizar consultas y análisis complejos sobre ellos.
  
  - **Neo4j** 
    - La arquitectura gráfica nativa de Neo4j permite la representación directa de relaciones como ciudadanos de primera clase. Esto es ideal para nuestro proyecto, en el que las relaciones entre artículos, autores, editores y temas son fundamentales para el análisis.
    - Esta estructura refleja intuitivamente las conexiones del mundo real que necesitamos analizar.
    - A diferencia de las bases de datos relacionales, Neo4j puede gestionar eficientemente consultas que requieren múltiples uniones, lo que resulta beneficioso para explorar redes complejas de literatura científica.
    - Las herramientas de visualización de gráficos integradas en Neo4j ayudan a explorar y comprender visualmente las relaciones en los datos, proporcionando una experiencia de análisis más intuitiva.

  - **SQL** 
    -  Este modelo es muy eficaz para almacenar datos estructurados, como la información complementaria (por ejemplo, metadatos sobre documentos) obtenida de las API.
    - SQL proporciona conformidad ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad), asegurando un procesamiento de transacciones fiable y la consistencia de los datos.   
    - Soporta la indexación de tablas, lo que mejora significativamente el rendimiento de las consultas de lectura. Esto es fundamental para la recuperación eficiente de datos, especialmente cuando se trata de grandes conjuntos de datos.

  - **Elastic Search**
    - ElasticSearch soporta búsqueda de texto completo, permitiendo a los usuarios buscar a través de la totalidad del texto dentro de los documentos. Esto es particularmente útil para la consulta de documentos científicos donde los usuarios pueden buscar temas específicos, palabras clave, autores o frases.
    - Proporciona potentes capacidades de agregación, permitiendo a los usuarios realizar análisis de datos complejos directamente dentro de sus consultas. Las agregaciones se pueden utilizar para calcular estadísticas, histogramas, etc., proporcionando información valiosa a partir de los datos.
    - La indexación eficiente es el núcleo del rendimiento de ElasticSearch. Sus mecanismos de indexación están diseñados para manejar grandes conjuntos de datos y soportar búsquedas rápidas.


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

## Garantía de Disponibilidad de los Datos

Asegurar la disponibilidad de datos es fundamental en las infraestructuras de big data para mantener la fiabilidad y accesibilidad de la información. En nuestro proyecto, utilizamos varias estrategias y tecnologías para garantizar que los datos permanezcan disponibles incluso ante fallos de hardware u otras interrupciones. 
ElasticSearch implementa la replicación de datos permitiendo que cada índice tenga uno o más fragmentos de réplica además del fragmento primario, almacenados en diferentes nodos del clúster. Si un nodo falla, un fragmento de réplica puede ser promovido a primario, asegurando la accesibilidad de los datos. Neo4j soporta la replicación a través de clústeres, donde los datos se replican a múltiples instancias, garantizando alta disponibilidad y tolerancia a fallos. 
MySQL utiliza la replicación maestro-esclavo, donde la base de datos maestra maneja las operaciones de escritura y propaga los cambios a las bases de datos esclavas; en caso de fallo, una esclava puede ser promovida a maestra, manteniendo la disponibilidad.

Distribuir datos y tareas de procesamiento a través de múltiples nodos permite a nuestra infraestructura tolerar fallos sin interrupciones significativas. Tanto Spark como ElasticSearch redirigen tareas y datos a nodos saludables en caso de fallos, asegurando una operación continua. Las copias de seguridad regulares de los datos almacenados en Neo4j, MySQL y ElasticSearch aseguran que los datos pueden ser restaurados en caso de fallos catastróficos, utilizando estrategias de respaldo automatizadas para minimizar la pérdida de datos y el tiempo de inactividad.

El balanceo de carga en ElasticSearch distribuye las solicitudes de búsqueda e indexación a través de los nodos del clúster, evitando cuellos de botella y asegurando un rendimiento consistente. En MySQL, los balanceadores de carga distribuyen las consultas a múltiples instancias, optimizando el uso de recursos y manteniendo alta disponibilidad al prevenir la sobrecarga en una sola instancia. Estas estrategias combinadas aseguran que nuestro sistema de big data es robusto, resistente a fallos, escalable y capaz de manejar grandes volúmenes de datos con alta disponibilidad y rendimiento.

## Garantía de Escalabilidad de datos
La escalabilidad horizontal se logra con Apache Spark, cuya arquitectura permite añadir más nodos de trabajo al clúster, distribuyendo la carga de datos y tareas de procesamiento complejas. ElasticSearch también escala horizontalmente al agregar más nodos al clúster, distribuyendo tareas de búsqueda e indexación, lo que permite manejar cargas crecientes de manera eficiente. Neo4j puede escalarse horizontalmente añadiendo más nodos para distribuir la carga de trabajo de la base de datos de grafos, gestionando datasets más grandes y consultas más complejas.

MySQL, aunque principalmente escala horizontalmente, también soporta la escalabilidad vertical mediante el uso de hardware más potente, como CPUs y memoria, lo cual ayuda a manejar datasets más grandes y consultas más complejas dentro de una sola instancia. 
ElasticSearch soporta la escalabilidad elástica, permitiendo añadir o remover nodos dinámicamente según la carga y el volumen de datos actual, ajustando la asignación de recursos en tiempo real. Spark también puede asignar recursos dinámicamente, escalando durante los picos de procesamiento y reduciendo durante los periodos de inactividad, optimizando así el uso de recursos y costos.

La gestión de clústeres se facilita con herramientas como Kubernetes, que pueden manejar los clústeres de Spark y ElasticSearch, automatizando el despliegue, escalado y operación de aplicaciones en contenedores, asegurando una utilización eficiente de recursos. La monitorización continua del uso de recursos y métricas de rendimiento permite al sistema escalar automáticamente los recursos según umbrales predefinidos, garantizando un rendimiento y disponibilidad óptimos.

# Eficiencia del Proyecto

La eficiencia es un aspecto crítico de nuestro proyecto de infraestructura de big data, asegurando que las operaciones de procesamiento, almacenamiento y recuperación de datos estén optimizadas para ofrecer un alto rendimiento mientras se minimiza el consumo de recursos. La eficiencia de nuestro proyecto se logra mediante las siguientes estrategias y tecnologías:

## Eficiencia en el Procesamiento de Datos

### Apache Spark:

- **Procesamiento en Memoria:** La capacidad de Spark para realizar cálculos en memoria reduce significativamente el tiempo requerido para tareas de procesamiento iterativas, como las relacionadas con la extracción, transformación y análisis de datos. Esto conduce a una ejecución más rápida en comparación con los sistemas de procesamiento basados en disco.
- **Procesamiento Paralelo:** Distribuyendo tareas en múltiples nodos de trabajo, Spark aprovecha el procesamiento paralelo, lo que mejora la velocidad y eficiencia de los flujos de trabajo de procesamiento de datos.
- **Planes de Ejecución Optimizados:** El optimizador Catalyst de Spark genera planes de ejecución optimizados para consultas de datos, garantizando el uso eficiente de recursos computacionales y reduciendo el tiempo de procesamiento.

### ElasticSearch:

- **Indexación Eficiente:** Los mecanismos eficientes de indexación de ElasticSearch, como los índices invertidos, aseguran que los datos se almacenen de manera que permita una búsqueda y recuperación rápidas, minimizando el tiempo y los recursos computacionales necesarios para realizar consultas de búsqueda.
- **Compresión:** ElasticSearch emplea técnicas de compresión para reducir la huella de almacenamiento de los datos indexados, asegurando un uso eficiente del espacio en disco manteniendo tiempos de acceso rápidos.

### Neo4j:

- **Representación Compacta de Grafos:** El motor de almacenamiento de grafos nativo de Neo4j está diseñado para almacenar relaciones como entidades de primer nivel, permitiendo un almacenamiento compacto y eficiente de relaciones de datos complejas.
- **Travesía Eficiente:** Los algoritmos de travesía de Neo4j están optimizados para estructuras de grafos, permitiendo una exploración rápida de datos conectados, lo que es fundamental para analizar las relaciones entre documentos científicos, editores y temas.

### MySQL:

- **Almacenamiento de Datos Normalizado:** Al utilizar esquemas normalizados, MySQL minimiza la redundancia de datos, lo que conduce a un uso eficiente del espacio de almacenamiento y mantiene la integridad de los datos.
- **Indexación:** MySQL soporta diversas estrategias de indexación, como árboles B y hash, que mejoran la velocidad de las operaciones de recuperación de datos.

### Eficiencia en la Recuperación de Datos

#### ElasticSearch:

- **Capacidades de Búsqueda de Texto Completo:** Las potentes capacidades de búsqueda de texto completo de ElasticSearch permiten la recuperación rápida y precisa de documentos basada en consultas de texto.
- **Puntuación de Relevancia y Optimización de Consultas:** Las características de puntuación de relevancia y optimización de consultas de ElasticSearch garantizan que se devuelvan rápidamente los resultados de búsqueda más relevantes, mejorando la experiencia del usuario y reduciendo la carga computacional en el sistema.

#### Neo4j:

- **Lenguaje de Consulta Cypher:** El lenguaje de consulta Cypher de Neo4j está diseñado específicamente para bases de datos de grafos, permitiendo la consulta eficiente y expresiva de datos de grafos.
- **Algoritmos de Grafos:** Los algoritmos de grafos integrados de Neo4j están optimizados para el rendimiento, lo que permite el análisis eficiente de grandes conjuntos de datos de grafos.

### Balanceo de Carga:

- **ElasticSearch:** El balanceo de carga entre nodos garantiza que ningún nodo se convierta en un cuello de botella, distribuyendo uniformemente la carga de búsqueda e indexación.

- **Uso de Múltiples Workers:** La implementación de múltiples workers distribuye la carga de trabajo de extracción de datos, permitiendo un procesamiento más eficiente y rápido. Esto garantiza un uso más efectivo de los recursos disponibles y reduce el tiempo total de extracción de datos.

- **Utilización de Contenedores Docker:** La elección de usar contenedores Docker proporciona un entorno ligero y eficiente para ejecutar aplicaciones. Al compartir el mismo kernel del sistema operativo del host, los contenedores minimizan el sobrecosto y permiten una mayor portabilidad de las aplicaciones entre diferentes entornos.

- **Almacenamiento de Datos en Volúmenes Docker:** Al optar por almacenar los datos en volúmenes Docker, se optimiza el acceso a los datos y se reduce la latencia. Esto mejora la eficiencia de las operaciones de lectura y escritura en comparación con el acceso a través de una red.


## Fiabilidad del Proyecto

La fiabilidad del proyecto es un aspecto crucial, dado que involucra la extracción, procesamiento y almacenamiento de grandes volúmenes de datos científicos. A continuación, se detalla cómo se asegura la fiabilidad en cada una de las etapas del proyecto:

### Extracción de Datos con Docker Workers

- **Aislamiento y Consistencia**: El uso de contenedores Docker asegura que cada worker opere en un entorno aislado y consistente, minimizando la posibilidad de conflictos y garantizando que el código se ejecute de manera idéntica en cualquier entorno.

- **Paralelización y Redundancia**: Al utilizar múltiples workers con diferentes claves API, se distribuye la carga de trabajo, lo que no solo mejora la eficiencia sino que también añade redundancia. Si un worker falla, los otros pueden continuar con el proceso de extracción.

- **Manejo de Errores**: Los scripts de Python en cada worker incluyen mecanismos de manejo de errores y reintentos para asegurar que la extracción de datos sea lo más completa y precisa posible.

### Procesamiento de Datos con Apache Spark

- **Resiliencia y Tolerancia a Fallos**: Spark está diseñado para ser resiliente y tolerante a fallos. Si un nodo del clúster falla durante el procesamiento, Spark redistribuirá automáticamente las tareas a otros nodos disponibles.

- **Optimización de Tareas**: Spark optimiza las tareas de procesamiento para maximizar la eficiencia y minimizar los tiempos de ejecución, lo que contribuye a la fiabilidad de los resultados obtenidos.

### Almacenamiento de Datos en Bases de Datos

- **Bases de Datos Robustas**: Neo4j y MySQL son bases de datos maduras y bien establecidas que ofrecen mecanismos de recuperación ante fallos y copias de seguridad automáticas, garantizando la persistencia y disponibilidad de los datos.
- **Índices y Consultas Eficientes**: La indexación adecuada en Elasticsearch y MySQL asegura que las consultas sean rápidas y precisas, mejorando la accesibilidad y usabilidad de los datos.

## Alcance del Proyecto

El alcance del proyecto abarca varias etapas y tecnologías, diseñadas para crear una infraestructura robusta y escalable para la extracción, procesamiento, análisis y almacenamiento de datos científicos. A continuación, se describen los componentes clave y las capacidades del proyecto:

### Extracción de Datos Inicial

- **Implementación de Docker Workers**: Configuración y despliegue de cuatro contenedores Docker, cada uno ejecutando scripts de Python para extraer datos en formato JSON desde una API de artículos científicos.
- **Paralelización del Proceso**: Uso de múltiples claves API para distribuir y paralelizar el proceso de extracción, optimizando el tiempo y la eficiencia de recolección de datos.

### Fusión y Consolidación de Datos

- **Unificación de Datos**: Fusión de los archivos JSON generados por los diferentes workers en un único archivo JSON, asegurando una consolidación completa y precisa de la información recolectada.

### Procesamiento de Datos con Apache Spark

- **Despliegue del Clúster de Spark**: Configuración de un clúster de Spark con un maestro y seis nodos de trabajo para manejar el procesamiento distribuido de datos.
- **Enriquecimiento de Datos**: Extracción de información adicional desde otras fuentes API, incluyendo detalles sobre la ubicación, el editor y el tema principal de cada artículo.
- **Generación de Archivos CSV**: Transformación y almacenamiento de los datos enriquecidos en archivos CSV, facilitando su uso posterior en bases de datos y otras aplicaciones.

### Almacenamiento y Gestión de Datos

- **Base de Datos Neo4j**: Implementación de una base de datos de grafos Neo4j para modelar y consultar relaciones complejas entre entidades como autores, artículos y editores.
- **Base de Datos MySQL**: Almacenamiento estructurado de datos en una base de datos relacional MySQL, permitiendo consultas eficientes y gestión de grandes volúmenes de información.
- **Elasticsearch**: Almacenamiento de los archivos JSON en Elasticsearch, proporcionando capacidades avanzadas de búsqueda y análisis de texto completo.

### Visualización y Análisis de Datos

- **Integración con JupyterLab**: Utilización de JupyterLab para proporcionar un entorno interactivo de análisis de datos, permitiendo a los investigadores explorar y visualizar los datos de manera eficiente.
- **Análisis Interactivo**: Capacidades para realizar análisis interactivo de datos, incluyendo consultas ad hoc, generación de informes y visualización de gráficos y relaciones.

### Ampliación y Escalabilidad

- **Escalabilidad Horizontal**: Capacidad de añadir más Docker workers y nodos Spark para manejar mayores volúmenes de datos o incrementar la velocidad de procesamiento según sea necesario.
- **Modularidad**: Diseño modular que permite la integración de nuevas fuentes de datos y la ampliación de funcionalidades sin afectar el núcleo del sistema.

#### Objetivos Específicos

- **Recolección de Datos Científicos**: Obtener datos detallados y actualizados de artículos científicos desde diversas fuentes API.
- **Enriquecimiento de Información**: Añadir metadatos relevantes a los artículos científicos, mejorando la calidad y utilidad del dataset.
- **Almacenamiento Eficiente**: Utilizar bases de datos especializadas para almacenar y gestionar los datos de manera óptima.
- **Facilitación del Análisis**: Proveer herramientas y entornos que faciliten el análisis avanzado de los datos por parte de investigadores y científicos de datos.

## Instalación

Clona el repositorio usando Git. Abre tu terminal o símbolo del sistema y ejecuta el siguiente comando:

```bash
git clone https://github.com/bnvulpe/PapersLab.git --config core.autocrlf=false
```
## Uso

Después de descargar o clonar el repositorio, navega hasta el directorio del proyecto en tu terminal o símbolo del sistema.

Una vez ubicado en la carpeta docker-configuration:
```bash
cd docker-configuration
```

Para GIT BASH:
```bash

1. export PWD_PARENT=$(dirname "$(pwd)")

2. docker build -t docker_configuration .

3. docker run -d --name docker_configuration -v PWD_PARENT:/app/project docker_configuration

4. docker cp $(docker ps -a --filter "name=docker_configuration" --format "{{.ID}}"):/app/docker-compose.yml $(dirname "$(pwd)")

5. cd ..

6. docker-compose up --build --detach

7. Una vez el servicio crossref haya finalizado su ejecución: docker-compose stop 
```

Una vez verificamos que el archivo all_data.json en dfs folder

```bash

1. cd spark

2. ./build.sh

3. docker-compose --env-file .env up --build --detach

4. una vez sacados todos los datos (avisa en logs el jupyter): 

docker stop $(docker ps -a --format "{{.ID}} {{.Names}}" | grep "spark" | awk '{print $1}')

5. cd ../databases

6. docker compose up -d

Una vez jupyter ha importado los datos a Elasticsearch (avisa en logs el jupyter), en la dirección localhost:8889 ya encontraremos Elasticsearch para hacer las queries necesarias para el procesamiento y analisis de los datos a conveniencia. Para trabajar con Neo4j se deberá acceder a localhost:7687, iniciar sesión con neo4j/password y realizar los imports del archivo /databases/init.txt

```
Para desmontar todo en raiz ejecutar

```
./teardown.sh
```
## License

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.
