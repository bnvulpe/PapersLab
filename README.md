1. INFRAESTRUCTURA

Identificar y describir los componentes clave de la infraestructura, incluyendo los servicios de contenedores a utilizar.


La infraestructura presentada se basa en microservicios diseñados para la extracción eficiente de datos de papers científicos utilizando múltiples API keys. Consiste en cuatro workers, uno para cada API key asociada a los miembros del grupo. Además, se implementa un volumen de Docker llamado "data" para almacenar los datos descargados, lo que facilita su posterior almacenamiento (en diferentes sistemas de bases de datos, Neo4j y MongoDB), tratamiento y manipulación en las siguientes etapas del proyecto.

La estructura de carpetas del proyecto es la siguiente:

- Carpeta docker-configuration:

docker-compose.yml.template: Template del Docker Compose utilizado para generar el archivo de configuración.
docker_compose_configuration.py: Script en Python que genera el Docker Compose deseado a partir del template, creando y asignando workers con las API keys correspondientes.
Dockerfile: Archivo para construir la imagen de Docker necesaria para ejecutar docker_compose_configuration.py.
docker-compose.yml: Docker Compose utilizado para montar la imagen anterior y crear el volumen donde se guardarán los datos.
.env: Archivo para almacenar las variables de entorno como BEGIN_YEAR, END_YEAR y CALL_LIMIT.
env_vars.txt: Archivo de texto donde se encuentran las 4 API keys (una en cada línea).

- Carpeta worker:

worker.py: Script encargado de la extracción de datos desde la API. Consta de varias funciones: 
	* query_api: función que se utiliza para realizar consultas a la API de Core. Esta función toma parámetros como la URL de la 	consulta, el cuerpo de la consulta, la clave de la API, entre otros, y devuelve los resultados de la consulta en formato JSON.
	* scroll: función  que se utiliza para manejar las consultas de desplazamiento continuo, permitiendo la extracción de grandes	conjuntos de datos paginados de la API.
	* save_json: guarda los datos extraídos en formato JSON en un archivo local.
	* main: Configura variables como la URL de la API, la clave de la API, el año de inicio y fin para la consulta, y el límite de 	llamadas a la API. Utiliza un bucle para realizar llamadas a la API con los parámetros configurados, guardando los resultados en 	archivos JSON locales. Se implementa una lógica de reintento en caso de errores de solicitud, y se respeta el límite de velocidad de 	la API mediante pausas entre las llamadas.
requirements.txt: Archivo que especifica las librerías necesarias para ejecutar el script.
Dockerfile: Dockerfile que construye la imagen responsable de ejecutar worker.py e instala las librerías especificadas en requirements.txt.


Explicar cómo cada componente contribuye al manejo eficiente de los datos y cómo se integran entre sí.

- Servicio de Extracción de Datos (Worker): Este microservicio se encarga de la extracción de datos desde una API dada utilizando un conjunto de API keys. Su función principal es recolectar los datos necesarios de manera eficiente y confiable.
Contribución al manejo eficiente de datos: El uso de varios workers distribuye la carga de trabajo y acelera el proceso de extracción de datos al paralelizar las solicitudes a la API. Esto optimiza el rendimiento y garantiza una extracción rápida y efectiva de grandes volúmenes de datos.
Integración con otros componentes: Los datos extraídos por cada worker se almacenan en un volumen Docker compartido, lo que permite un acceso uniforme a los datos desde otros componentes del sistema, como las bases de datos MongoDB y Neo4j.

- Almacenamiento de Datos en Volúmenes Docker: Los datos extraídos por los workers se almacenan en volúmenes Docker para facilitar su acceso desde otros servicios y garantizar su persistencia a lo largo del tiempo.
Contribución al manejo eficiente de datos: Almacenar los datos en volúmenes Docker permite un acceso rápido y eficiente a los mismos desde cualquier componente del sistema. Esto reduce la latencia y mejora el rendimiento en comparación con el almacenamiento en sistemas de archivos externos o bases de datos.
Integración con otros componentes: Los volúmenes Docker proporcionan una capa de abstracción para los datos, lo que simplifica su integración con otros servicios, como las bases de datos MongoDB y Neo4j.

- Servicios de Bases de Datos (MongoDB y Neo4j): Estos servicios almacenan y gestionan los datos de manera estructurada, lo que permite realizar consultas y análisis complejos sobre ellos.
Contribución al manejo eficiente de datos: Las bases de datos MongoDB y Neo4j están diseñadas para manejar grandes volúmenes de datos de manera eficiente. Proporcionan capacidades de indexación, consultas optimizadas y almacenamiento escalable que facilitan el acceso y la manipulación de los datos de forma eficiente.
Integración con otros componentes: Los datos almacenados en los volúmenes Docker pueden ser fácilmente cargados en las bases de datos MongoDB y Neo4j para su análisis posterior. Estos servicios proporcionan interfaces de programación y consultas que permiten acceder a los datos de manera programática desde otros servicios, como Jupyter y Spark.

---------------------------------------------------------------------------------------------------------------------------------

2. DATOS

Proponer una solución para el almacenamiento en crudo de los datos, que optimice el acceso y la recuperación de información.

Los datos extraídos se almacenarán en un volumen Docker llamado "data". Este enfoque garantiza un acceso centralizado y sencillo desde todos los servicios de bases de datos que se utilizarán, como Neo4j y MongoDB, así como desde herramientas de análisis como Jupyter y Spark. Al almacenar los datos en un volumen Docker, en primer lugar, garantizamos un acceso centralizado desde todos los servicios de bases de datos que utilizaremos, así como desde herramientas de análisis. Esto simplifica la gestión y evita la duplicación de datos en diferentes ubicaciones. En segundo lugar, se elimina la necesidad de transferirlos entre diferentes sistemas de archivos o dispositivos de almacenamiento, lo que agiliza el proceso de manipulación y análisis. Por último, Los volúmenes Docker son altamente escalables y pueden crecer según las necesidades del proyecto. Esta flexibilidad nos permite adaptarnos a cambios en el volumen de datos sin comprometer el rendimiento del sistema.

En resumen, esta solución proporciona una solución robusta y eficiente que optimiza el acceso, la manipulación y la recuperación de información, preparándonos para la siguiente fase de la práctica donde se realizará el tratamiento, manipulación y almacenamiento de los datos extraídos. El uso de un volumen Docker y la selección de formatos de almacenamiento adecuados aseguran un acceso programático sencillo y optimizado a los datos desde diversas herramientas y servicios.

---------------------------------------------------------------------------------------------------------------------------------
???

Formato de Almacenamiento:
Dado que se requerirá acceso programático a los datos a través de diferentes herramientas y servicios, proponemos almacenar los datos tanto en formato JSON como en formato CSV, dependiendo de su naturaleza y necesidades específicas.

Justificación del Uso de JSON y CSV:

JSON: El formato JSON es adecuado para representar datos estructurados y semiestructurados. Facilita la manipulación y el análisis de los datos en herramientas como Jupyter y Spark debido a su estructura flexible y legible. 

Estructura de Datos Flexible: El formato JSON es adecuado para representar datos estructurados y semiestructurados, lo que facilita su manipulación y análisis posterior en herramientas como Jupyter y Spark.

Compatibilidad con Diversas Plataformas: El formato JSON es ampliamente compatible y puede ser procesado por una variedad de herramientas y lenguajes de programación, lo que garantiza una interoperabilidad sin problemas en diferentes entornos de desarrollo.

Legibilidad y Mantenibilidad: Los datos en formato JSON son legibles tanto para humanos como para máquinas, lo que facilita la comprensión de la estructura y los atributos de los datos. Esto simplifica el proceso de desarrollo y mantenimiento del sistema en el futuro.

CSV: El formato CSV es ideal para datos tabulares y simplifica la importación de datos en bases de datos relacionales y no relacionales, como MongoDB y Neo4j. Esto permite una integración más fácil con las diferentes bases de datos que se utilizarán en la segunda parte de la práctica.

---------------------------------------------------------------------------------------------------------------------------------
Describir cómo se garantizará la disponibilidad y escalabilidad de los datos en el sistema propuesto.

En el sistema propuesto, la disponibilidad y escalabilidad de los datos se garantizan mediante una arquitectura basada en microservicios respaldada por el uso de volúmenes Docker. Esta combinación de tecnologías proporciona una infraestructura robusta y flexible para asegurar el acceso continuo a los datos y su escalabilidad según las necesidades del sistema.

La implementación de microservicios permite descomponer la aplicación en componentes independientes, cada uno encapsulando su propia lógica de negocio y datos. Al utilizar volúmenes Docker para almacenar los datos de estos microservicios, se asegura que los datos estén disponibles para cada instancia del servicio, incluso en casos de fallos o reinicios de los contenedores. Esto garantiza una alta disponibilidad de datos, ya que cada instancia tiene acceso al mismo estado persistente a través del volumen compartido.

Además, la arquitectura basada en microservicios facilita la escalabilidad del sistema. Al escalar horizontalmente los microservicios para manejar una carga de trabajo creciente, los volúmenes Docker aseguran que cada instancia del servicio tenga acceso a los mismos datos almacenados en el volumen compartido. Esto permite una escalabilidad fluida y sin interrupciones, ya que todas las instancias comparten el mismo estado de datos.

Por lo tanto, mediante la combinación de microservicios y volúmenes Docker, se garantiza una alta disponibilidad y escalabilidad de los datos en el sistema propuesto. Esta arquitectura proporciona una base sólida para satisfacer las demandas cambiantes de capacidad y carga de trabajo, asegurando el acceso continuo y eficiente a los datos en todo momento.

---------------------------------------------------------------------------------------------------------------------------------

3. CALIDAD

Justificar las decisiones de diseño basándose en los principios de calidad para infraestructuras virtuales discutidos en clase, como la eficiencia, la escalabilidad, la fiabilidad, la gestión de la carga, entre otros.

- Eficiencia: 
  	* Uso de múltiples workers: La implementación de 4 workers distribuye la carga de trabajo de extracción de datos, lo que 	permite un procesamiento más eficiente y rápido. Esto garantiza un uso más efectivo de los recursos y reduce el tiempo 	total de extracción de datos.

	* Utilización de contenedores Docker: El uso de contenedores Docker proporciona un entorno ligero y eficiente para 	ejecutar aplicaciones, ya que comparten el mismo kernel del sistema operativo del host. Esto permite una utilización más 	eficiente de los recursos de hardware y una mayor portabilidad de las aplicaciones entre diferentes entornos.

	* Almacenamiento de datos en volúmenes Docker: Al almacenar los datos en un volumen Docker, se optimiza el acceso a los 	datos y se reduce la latencia, ya que los datos están disponibles localmente para cada contenedor que los necesite. Esto 	mejora la eficiencia de las operaciones de lectura y escritura en comparación con el acceso a través de una red.

- Escalabilidad:
	* Orquestación mediante Docker Compose: La utilización de Docker Compose facilita la gestión y escalabilidad de los 	servicios. La infraestructura puede escalar verticalmente agregando más recursos a cada worker o horizontalmente 	agregando más workers según sea necesario para manejar mayores volúmenes de datos.

	* Uso de volúmenes Docker: Al utilizar volúmenes Docker para almacenar datos, se facilita la escalabilidad horizontal al 	permitir la adición o eliminación dinámica de contenedores sin afectar la disponibilidad de los datos. Esto permite 	adaptarse rápidamente a cambios en la demanda del sistema.

- Fiabilidad:
	* Tolerancia a fallos: La distribución de la carga de trabajo entre varios workers aumenta la redundancia y la tolerancia 	a fallos. Si un worker falla, los otros pueden continuar ejecutándose, lo que garantiza la disponibilidad y la fiabilidad 	del sistema en general.

	* Gestión de fallos: Mediante el monitoreo constante de los workers y la implementación de estrategias de recuperación, 	como la reintentación de solicitudes o la restauración de contenedores, se garantiza una gestión efectiva de fallos para 	mantener la estabilidad del sistema.

- Gestión de la Carga:
	* Distribución equitativa de la carga: La asignación de trabajos a los workers se realiza de manera equitativa para 	evitar la sobrecarga de un worker específico. Esto garantiza una distribución uniforme de la carga de trabajo y optimiza 	el rendimiento del sistema en su conjunto.

---------------------------------------------------------------------------------------------------------------------------------

4. ALCANCE

Argumentar qué dimensiones del Big Data se han sacrificado, si es el caso, y justificar cómo esta decisión simplifica la
implementación de la infraestructura sin comprometer significativamente su funcionalidad.

Si bien en nuestro servicio se ha sacrificado la variedad de datos en favor del volumen y la variedad en el proceso final de almacenamiento, esta decisión simplifica la implementación de la infraestructura sin comprometer significativamente su funcionalidad: 

- La decisión de enfocarse en el volumen y la variedad en el proceso final de almacenamiento implica priorizar la cantidad y diversidad de los datos procesados y almacenados. Esto se traduce en un mayor énfasis en la cantidad de datos recopilados y la variedad de fuentes finales de almacenamiento, como Neo4j y MongoDB, en lugar de diversificar la gama de formatos de los datos durante la extracción inicial.

- Optar por conservar los datos en el formato JSON, tal como los devuelve la API, simplifica el proceso de extracción y almacenamiento inicial. Esto se debe a que el formato JSON es fácilmente manipulable y compatible con la mayoría de las herramientas y plataformas de análisis de datos, lo que reduce la complejidad en la fase inicial de procesamiento.

- Además, la elección de guardar la información obtenida de Wikidata en formato CSV para el estudio geográfico muestra un enfoque pragmático para el análisis posterior. Al priorizar la simplicidad en el formato de almacenamiento, se simplifica la manipulación y el análisis de estos datos específicos para el estudio geográfico previsto.

En conclusión, el sacrificio de la variedad de datos en favor del volumen y la variedad en el proceso final de almacenamiento simplifica la implementación de la infraestructura al reducir la complejidad en las etapas iniciales de extracción y almacenamiento, al tiempo que facilita la integración y el análisis posterior de los datos recopilados.

---------------------------------------------------------------------------------------------------------------------------------

POWERSHELL

in docker_configuration folder:

1. $env:PWD_PARENT = (Get-Item -Path ".\").Parent.FullName; docker-compose up --build --detach 

2. docker ps -a --filter "name=docker_configuration" --format "{{.ID}}"

3. use output ID for command : docker cp ID:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName

	example: docker cp aa2dd076eed7:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName

4. cd ..

5. Get-Content -Path .\docker-compose.yml | Out-File -FilePath ".\wiki\docker-compose.txt"

5. docker-compose up --build --detach



docker cp 2f3eb5a390ca:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName

Falta:
- Explicar la carpeta y ficheros wiki_data
- Añadir explicación de la elección del formato JSON y CSV o en el segundo o cuarto punto.
- Añadir comandos para otros tipos de terminales

