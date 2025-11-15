# TABLA DE SIMBOLOS Y EDTS

Este proyecto implementa un analizador para un subconjunto simple de Python, utilizando parte de la gramatica Python usando indentado con ':' y 'end' , para generar codigo de 3 direcciones y la tabla de simbolos, esto mediante el uso de analizadores lexico y sintactico, y generacion de un arbol sintactico decorado para la construcción de este.

# ESTRUCTURA DEL PROYECTO:

    •Tabla_simbolos
      |
      |___ EDTS.py
      |___prueba.py

# EXPLICACIÓN
  •Gramatica
  ----------------------------------------------------------------------
Para este proyecto se eligio una gramática simplificada del lenguaje Python adaptada de esta manera:

    if condicion:
        bloque
    else:
        bloque
    end
    
    while condicion:
        bloque
    end


No utiliza indentacion real sino delimitadores : y la palabra end al estilo pseudocodigo, esto permite una sintaxis clara y sencilla para construir el análisis léxico y sintáctico.

Esto permite 

-evitar la indentacion real de Python, que funciona de manera mas compleja

-mantiene estructuras válidas de control: if, else, while, return

-facilitar la construccion del AST

-generar el codigo de 3 direcciones.

  •ETDS (Esquema de Traducción Dirigida por Sintaxis)
----------------------------------------------------------------------
La ETDS se implementa directamente dentro de las clases del AST y del generador TAC.
cada nodo del AST tiene suficiente informacion para conocer su tipo, producir su direccion e inferir el tipo para la tabla de simbolos.

cada nodo recibe:

addr: ubicacion temporal o variable

type: tipo inferido 

codigo: reglas de traduccion TAC generadas bottom-up

Esto es una ETDS completa, el significado del programa se construye mientras se analiza su estructura.

 •Tabla de simbolos
----------------------------------------------------------------------
Se implementa un recorrido semantico independiente:

    symbolos=build_symbol_table(prog)


La tabla de simbolos registra:

variables declaradas por primera vez mediante una asignación con su tipo inferido por las expresiones

Ejemplo de salida:

    x : int
    y : int
    z : int


•Generacion de codigo en tres direcciones (TAC)
----------------------------------------------------------------------
El generador transforma el arbol en instrucciones de tres direcciones:
    
    ADDR x y t1
    STOR t1 z


este implementa los operadores aritmeticos y logicos de esta manera:
    
    ADDR (suma)
    SUBR (resta)
    MULR (multiplicación)
    DIVR (división)
    GT   (>)
    LT   (<)


Y las estructuras de control asi:

    IF cond IR A Ltrue
    IR A Lfalse
    Ltrue:
        ...
    IR A Lfin
    Lfalse:
        ...
    Lfin:


Y finalmente para while:

    Linicio:
        evaluar condición
        IF cond IR A Linicio_CUERPO
        IR A Lfin
    Linicio_CUERPO:
        ...
        IR A Linicio
    Lfin:

# Pruebas y resultados

A continuacion, se muestra algunas pruebas con programas de python junto a los resultados que mostro el programa al ejecutarlos:

PRUEBA 1
----------------------------------------------------------------------
x = 1

y = 2

z = x + y

    CODIGO TAC 
    STOR 1 x
    STOR 2 y
    ADDR x y t1
    STOR t1 z
    
    TABLA DE SIMBOLOS 
    x : int
    y : int
    z : int

PRUEBA 2
----------------------------------------------------------------------
x = 5

if x > 3:

    y = x * 2
    
end

    CODIGO TAC
    STOR 5 x
    GT x 3 t1
    IF t1 IR A L1
    IR A L2
    L1:
    MULR x 2 t2
    STOR t2 y
    IR A L3
    L2:
    L3:
    
    TABLA DE SIMBOLOS
    x : int
    y : int

PRUEBA  3
----------------------------------------------------------------------
i = 0

while i < 5:

    if i > 2:
    
        x = i * 10
        
    else:
    
        x = 0
        
    end
    
    i = i + 1
    
end

    CODIGO TAC
    STOR 0 i
    L1:
    LT i 5 t1
    IF t1 IR A L1_CUERPO
    IR A L2
    L1_CUERPO:
    GT i 2 t2
    IF t2 IR A L3
    IR A L4
    L3:
    MULR i 10 t3
    STOR t3 x
    IR A L5
    L4:
    STOR 0 x
    L5:
    ADDR i 1 t4
    STOR t4 i
    IR A L1
    L2:
    
    TABLA DE SIMBOLOS
    i : int
    x : int

PRUEBA 4
----------------------------------------------------------------------
x = 4

y = x + z
    
    Exception: Variable 'z' usada sin declararse




