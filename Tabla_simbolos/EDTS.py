class Program:
    def __init__(self, stmts): self.stmts=stmts

class Assign:
    def __init__(self, nombre, expr): self.nombre =nombre; self.expr=expr

class BinOp:
    def __init__(self, izq, op, der): self.izq=izq; self.op=op; self.der=der

class Num:
    def __init__(self, value): self.value=value

class Var:
    def __init__(self, nombre): self.nombre=nombre

class If:
    def __init__(self, cond, then_stmts, else_stmts): self.cond=cond; self.then_stmts=then_stmts; self.else_stmts=else_stmts

class While:
    def __init__(self, cond, cuerpo): self.cond=cond; self.cuerpo=cuerpo

class Return:
    def __init__(self, expr): self.expr=expr

def tokenize(codigo):
    tokens=[]
    i=0
    n=len(codigo)

    def es_letra(c): 
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_'
    
    def es_digito(c): 
        return '0' <= c <= '9'

    while i<n:
        c=codigo[i]

        if c in ' \t\r\n':
            i+=1
            continue

        if es_digito(c):
            s=c
            i+=1
            while i<n and es_digito(codigo[i]):
                s+=codigo[i]
                i+=1
            tokens.append(("NUM", s))
            continue

        if es_letra(c):
            s=c
            i+=1
            while i<n and (es_letra(codigo[i]) or es_digito(codigo[i])):
                s+=codigo[i]
                i+=1
            
            if s in ("if","else","while","return","end"):
                tokens.append((s.upper(), s))
            else:
                tokens.append(("ID", s))
            continue

        if c in "+-*/<>()=:": 
            if c==":":
                tokens.append(("COLON", ":"))
            elif c=="(":
                tokens.append(("LP", "("))
            elif c==")":
                tokens.append(("RP", ")"))
            elif c=="=":
                tokens.append(("EQ", "=")) 
            else:
                tokens.append(("OP", c))
            i+=1
            continue

        raise Exception("caracter invalido en input: "+repr(c))

    tokens.append(("EOF", None))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.t=tokens
        self.i=0
        self.current=self.t[self.i]

    def avanzar(self):
        self.i+=1
        if self.i<len(self.t):
            self.current=self.t[self.i]
        else:
            self.current=("EOF", None)

    def coincide(self, typ):
        if self.current[0]==typ:
            val=self.current[1]
            self.avanzar()
            return val
        raise Exception(f"se encontro: '{self.current}'; se esperaba: '{typ}'")

    def mirar(self):
        return self.current[0]

    def parse(self):
        stmts=[]
        while self.mirar()!="EOF":
            stmts.append(self.stmt())
        return Program(stmts)

    def stmt(self):
        if self.mirar()=="ID":
            nombre=self.coincide("ID")
            if self.mirar()!="EQ":
                raise Exception("Se esperaba '=' tras identificador")
            self.coincide("EQ")
            expr=self.expr()
            return Assign(nombre, expr)

        if self.mirar()=="IF":
            self.coincide("IF")
            cond=self.expr()
            self.coincide("COLON")
            then_stmts=self.block_until(("ELSE", "END"))
            else_stmts=[]
            if self.mirar()=="ELSE":
                self.coincide("ELSE")
                self.coincide("COLON")
                else_stmts=self.block_until(("END",))
            if self.mirar()=="END":
                self.coincide("END")
            else:
                raise Exception("se esperaba 'end' para cerrar if")
            return If(cond, then_stmts, else_stmts)

        if self.mirar()=="WHILE":
            self.coincide("WHILE")
            cond=self.expr()
            self.coincide("COLON")
            cuerpo=self.block_until(("END",))
            if self.mirar()=="END":
                self.coincide("END")
            else:
                raise Exception("se esperaba 'end' para cerrar while")
            return While(cond, cuerpo)

        if self.mirar()=="RETURN":
            self.coincide("RETURN")
            expr=self.expr()
            return Return(expr)

        if self.mirar()=="EOF":
            return None

        raise Exception(f"sentencia invalida: {self.current}")

    def block_until(self, end_tokens):
        stmts=[]
        while self.mirar() not in end_tokens and self.mirar()!="EOF":
            stm=self.stmt()
            if stm is not None:
                stmts.append(stm)
        return stmts

    def expr(self):
        return self.parse_level1()

    def parse_level1(self):
        izq=self.parse_level2()
        while self.mirar() in ("OP",) and self.current[1] in ("+","-"):
            op=self.current[1]; self.avanzar()
            der=self.parse_level2()
            izq=BinOp(izq, op, der)
        return izq

    def parse_level2(self):
        izq=self.parse_level3()
        while self.mirar() in ("OP",) and self.current[1] in ("*","/"):
            op=self.current[1]; self.avanzar()
            der=self.parse_level3()
            izq=BinOp(izq, op, der)
        return izq

    def parse_level3(self):
        izq=self.parse_atom()
        while self.mirar() in ("OP",) and self.current[1] in (">","<"):
            op=self.current[1]; self.avanzar()
            der=self.parse_atom()
            izq=BinOp(izq, op, der)
        return izq

    def parse_atom(self):
        if self.mirar()=="NUM":
            v=self.coincide("NUM"); return Num(int(v))
        if self.mirar()=="ID":
            n=self.coincide("ID"); return Var(n)
        if self.mirar()=="LP":
            self.coincide("LP")
            e=self.expr()
            self.coincide("RP")
            return e
        raise Exception(f"Error en expresión, token: {self.current}")

contador_temp=0
contador_label=0
def newTemp():
    global contador_temp
    contador_temp+=1
    return f"t{contador_temp}"

def newLabel():
    global contador_label
    contador_label+=1
    return f"L{contador_label}"

def gen_stmt_list(stmts, env):
    codigo=[]
    for s in stmts:
        codigo.extend(gen_stmt(s, env))
    return codigo

def gen_stmt(nodo, env):
    if isinstance(nodo, Assign):
        expr_nodo, expr_codigo=gen_expr(nodo.expr, env)
        if nodo.nombre not in env:
            env[nodo.nombre]={"type": expr_nodo.type}

        return expr_codigo+[f"STOR {expr_nodo.addr} {nodo.nombre}"]

    if isinstance(nodo, If):
        cond_nodo, cond_codigo=gen_expr(nodo.cond, env)
        Ltrue=newLabel()
        Lfalse=newLabel()
        Lfin=newLabel()
        codigo=cond_codigo

        codigo.append(f"IF {cond_nodo.addr} IR A {Ltrue}")
        codigo.append(f"IR A {Lfalse}")
        codigo.append(f"{Ltrue}:")
        codigo+=gen_stmt_list(nodo.then_stmts, env)
        codigo.append(f"IR A {Lfin}")
        codigo.append(f"{Lfalse}:")
        codigo+=gen_stmt_list(nodo.else_stmts, env)
        codigo.append(f"{Lfin}:")
        return codigo

    if isinstance(nodo, While):
        Linicio=newLabel()
        Lfin=newLabel()
        codigo=[f"{Linicio}:"]
        cond_nodo, cond_codigo=gen_expr(nodo.cond, env)
        codigo+=cond_codigo

        codigo.append(f"IF {cond_nodo.addr} IR A {Linicio}_CUERPO")
        codigo.append(f"IR A {Lfin}")
        codigo.append(f"{Linicio}_CUERPO:")
        codigo+=gen_stmt_list(nodo.cuerpo, env)
        codigo.append(f"IR A {Linicio}")
        codigo.append(f"{Lfin}:")
        return codigo

    if isinstance(nodo, Return):
        expr_nodo, expr_codigo=gen_expr(nodo.expr, env)
        return expr_codigo+[f"return {expr_nodo.addr}"]

    return []

def gen_expr(nodo, env):
    if isinstance(nodo, Num):
        nodo.addr=str(nodo.value)
        nodo.type="int"
        return nodo, []

    if isinstance(nodo, Var):
        if nodo.nombre not in env:
            raise Exception(f"Variable '{nodo.nombre}' usada sin declararse")
        nodo.addr=nodo.nombre
        nodo.type=env[nodo.nombre]["type"]
        return nodo, []

    if isinstance(nodo, BinOp):
        Lnodo, Lcodigo=gen_expr(nodo.izq, env)
        Rnodo, Rcodigo=gen_expr(nodo.der, env)

        if nodo.op==">":
            t=newTemp()
            codigo=Lcodigo+Rcodigo+[f"GT {Lnodo.addr} {Rnodo.addr} {t}"]
            tn=Num(0)

            tn.addr=t
            tn.type="int"
            return tn, codigo
        if nodo.op=="<":
            t=newTemp()
            codigo=Lcodigo+Rcodigo+[f"LT {Lnodo.addr} {Rnodo.addr} {t}"]
            tn=Num(0)
            tn.addr=t
            tn.type="int"
            return tn, codigo

        if nodo.op=="+":
            instr="ADDR"
        elif nodo.op=="-":
            instr="SUBR"
        elif nodo.op=="*":
            instr="MULR"
        elif nodo.op=="/":
            instr="DIVR"
        else:
            instr="OPR"

        t=newTemp()
        codigo=Lcodigo+Rcodigo+[f"{instr} {Lnodo.addr} {Rnodo.addr} {t}"]

        tn=Num(0)
        tn.addr=t
        tn.type="int"
        return tn, codigo

    raise Exception("expresion no reconocida en gen_expr")

def build_symbol_table(program):
    table={}
    def visit_stmt(s):
        if isinstance(s, Assign):
            t=infer_type(s.expr, table)
            table[s.nombre]=t
        elif isinstance(s, If):
            infer_type(s.cond, table)
            for st in s.then_stmts: 
                visit_stmt(st)

            for st in s.else_stmts: 
                visit_stmt(st)

        elif isinstance(s, While):
            infer_type(s.cond, table)
            for st in s.cuerpo: 
                visit_stmt(st)

        elif isinstance(s, Return):
            infer_type(s.expr, table)

    for st in program.stmts:
        visit_stmt(st)
    return table

def infer_type(expr, table):
    if isinstance(expr, Num): 
        return "int"
    
    if isinstance(expr, Var): 
        return table.get(expr.nombre, "error")
    
    if isinstance(expr, BinOp):
        lt=infer_type(expr.izq, table)
        rt=infer_type(expr.der, table)
        if "error" in (lt, rt): 
            return "error"
        return "int"
    return "error"

if __name__=="__main__":
    archivo=input("ingrese el archivo de prueba: ").strip()
    codigo=open(archivo, "r", encoding="utf-8").read()
    tokens=tokenize(codigo)
    parser=Parser(tokens)
    prog=parser.parse()

    symbolos=build_symbol_table(prog)

    env={k: {"type": v} for k, v in symbolos.items()}
    tac=gen_stmt_list(prog.stmts, env)

    print("\nCODIGO TAC ")
    for line in tac:
        print(line)

    print("\nTABLA DE SIMBOLOS ")
    for k, v in symbolos.items():
        print(f"{k} : {v}")