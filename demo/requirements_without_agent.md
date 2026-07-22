# Documento de Requisitos

## Introducción

Sistema de gestión de estudiantes que permite registrar estudiantes, inscribirlos en cursos y consultar su historial de calificaciones. El sistema proporciona operaciones CRUD para estudiantes y cursos, gestión de inscripciones y seguimiento de calificaciones.

## Glosario

- **Sistema**: El sistema de gestión de estudiantes en su totalidad
- **Estudiante**: Persona registrada en el sistema con datos personales (nombre, correo electrónico, identificador único)
- **Curso**: Unidad académica con nombre, código y capacidad máxima de estudiantes
- **Inscripción**: Relación entre un Estudiante y un Curso que indica que el Estudiante está matriculado en dicho Curso
- **Calificación**: Valor numérico (0-100) asignado a un Estudiante en un Curso específico
- **Historial_de_Calificaciones**: Registro completo de todas las Calificaciones obtenidas por un Estudiante en todos los Cursos en los que ha estado inscrito
- **Validador**: Componente del Sistema responsable de verificar la integridad y formato de los datos de entrada

## Requisitos

### Requisito 1: Registro de Estudiantes

**Historia de Usuario:** Como administrador, quiero registrar estudiantes en el sistema, para poder llevar un control de los alumnos activos.

#### Criterios de Aceptación

1. WHEN el administrador proporciona datos válidos (nombre, correo electrónico), THE Sistema SHALL crear un nuevo registro de Estudiante con un identificador único generado automáticamente.
2. WHEN el administrador proporciona un correo electrónico que ya existe en el sistema, THE Validador SHALL rechazar el registro y retornar un mensaje indicando que el correo electrónico ya está en uso.
3. WHEN el administrador proporciona datos incompletos o con formato inválido, THE Validador SHALL rechazar el registro y retornar un mensaje describiendo los campos con error.
4. THE Sistema SHALL almacenar para cada Estudiante: identificador único, nombre completo y correo electrónico.

### Requisito 2: Consulta y Gestión de Estudiantes

**Historia de Usuario:** Como administrador, quiero consultar, actualizar y eliminar estudiantes registrados, para mantener la información actualizada.

#### Criterios de Aceptación

1. WHEN el administrador solicita la lista de estudiantes, THE Sistema SHALL retornar todos los registros de Estudiante existentes.
2. WHEN el administrador solicita los datos de un Estudiante por su identificador, THE Sistema SHALL retornar el registro completo del Estudiante.
3. WHEN el administrador solicita los datos de un Estudiante con un identificador inexistente, THE Sistema SHALL retornar un mensaje indicando que el Estudiante no fue encontrado.
4. WHEN el administrador actualiza los datos de un Estudiante existente, THE Sistema SHALL modificar el registro y confirmar la operación exitosa.
5. WHEN el administrador elimina un Estudiante, THE Sistema SHALL remover el registro del Estudiante y todas sus Inscripciones asociadas.

### Requisito 3: Gestión de Cursos

**Historia de Usuario:** Como administrador, quiero crear y gestionar cursos, para poder ofrecer materias a los estudiantes.

#### Criterios de Aceptación

1. WHEN el administrador proporciona datos válidos (nombre, código, capacidad máxima), THE Sistema SHALL crear un nuevo registro de Curso.
2. WHEN el administrador proporciona un código de Curso que ya existe, THE Validador SHALL rechazar la creación y retornar un mensaje indicando que el código ya está en uso.
3. WHEN el administrador solicita la lista de cursos, THE Sistema SHALL retornar todos los registros de Curso existentes.
4. WHEN el administrador solicita los datos de un Curso por su código, THE Sistema SHALL retornar el registro completo del Curso.
5. THE Sistema SHALL almacenar para cada Curso: código único, nombre y capacidad máxima de estudiantes.

### Requisito 4: Inscripción de Estudiantes en Cursos

**Historia de Usuario:** Como administrador, quiero inscribir estudiantes en cursos, para registrar su participación académica.

#### Criterios de Aceptación

1. WHEN el administrador inscribe un Estudiante válido en un Curso con capacidad disponible, THE Sistema SHALL crear una nueva Inscripción y confirmar la operación.
2. WHEN el administrador intenta inscribir un Estudiante en un Curso que ha alcanzado su capacidad máxima, THE Sistema SHALL rechazar la Inscripción y retornar un mensaje indicando que el Curso está lleno.
3. WHEN el administrador intenta inscribir un Estudiante que ya está inscrito en el mismo Curso, THE Validador SHALL rechazar la operación y retornar un mensaje indicando la inscripción duplicada.
4. WHEN el administrador intenta inscribir un Estudiante inexistente o en un Curso inexistente, THE Validador SHALL rechazar la operación y retornar un mensaje indicando la entidad no encontrada.
5. WHEN el administrador cancela una Inscripción, THE Sistema SHALL remover la relación entre el Estudiante y el Curso.

### Requisito 5: Registro de Calificaciones

**Historia de Usuario:** Como administrador, quiero asignar calificaciones a estudiantes en sus cursos, para llevar un registro académico preciso.

#### Criterios de Aceptación

1. WHEN el administrador asigna una Calificación (valor entre 0 y 100) a un Estudiante inscrito en un Curso, THE Sistema SHALL registrar la Calificación y confirmar la operación.
2. WHEN el administrador asigna una Calificación a un Estudiante que no está inscrito en el Curso especificado, THE Validador SHALL rechazar la operación y retornar un mensaje indicando que la Inscripción no existe.
3. WHEN el administrador proporciona un valor de Calificación fuera del rango 0-100, THE Validador SHALL rechazar la operación y retornar un mensaje indicando el rango válido.
4. WHEN el administrador actualiza una Calificación existente, THE Sistema SHALL modificar el valor y confirmar la operación.

### Requisito 6: Consulta del Historial de Calificaciones

**Historia de Usuario:** Como administrador, quiero consultar el historial de calificaciones de un estudiante, para evaluar su desempeño académico.

#### Criterios de Aceptación

1. WHEN el administrador solicita el Historial_de_Calificaciones de un Estudiante, THE Sistema SHALL retornar todas las Calificaciones del Estudiante agrupadas por Curso.
2. WHEN el administrador solicita el Historial_de_Calificaciones de un Estudiante sin Calificaciones registradas, THE Sistema SHALL retornar una lista vacía.
3. WHEN el administrador solicita el Historial_de_Calificaciones de un Estudiante inexistente, THE Sistema SHALL retornar un mensaje indicando que el Estudiante no fue encontrado.

### Requisito 7: Serialización de Datos

**Historia de Usuario:** Como desarrollador, quiero que los datos de estudiantes, cursos y calificaciones se serialicen y deserialicen correctamente, para garantizar la integridad en el almacenamiento y transmisión.

#### Criterios de Aceptación

1. THE Sistema SHALL serializar registros de Estudiante a formato JSON válido.
2. THE Sistema SHALL deserializar datos JSON válidos a registros de Estudiante.
3. FOR ALL registros válidos de Estudiante, serializar y luego deserializar SHALL producir un objeto equivalente al original (propiedad round-trip).
4. FOR ALL registros válidos de Curso, serializar y luego deserializar SHALL producir un objeto equivalente al original (propiedad round-trip).
5. IF el Sistema recibe datos JSON con formato inválido, THEN THE Validador SHALL retornar un error descriptivo indicando el problema de formato.
