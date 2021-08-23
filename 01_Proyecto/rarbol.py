import pandas as pd
import numpy as np
from collections import Counter

class arbolRegresion():
    def __init__(
        self, 
        Y: list,
        X: pd.DataFrame,
        funcionCosto="RSS",
        minRegDiv=20,
        maxProfundidad=10,
        profundidad=None,
        tipoNodo=None,
        regla=None
        
        
    ):
        #Entrenado
        self.entrenado = False


        #Guardamos los hiper parametros
        self.minRegDiv = minRegDiv
        self.maxProfundidad = maxProfundidad

        #información del nodo
        self.tipoNodo = tipoNodo if tipoNodo else 'root'
        self.profundidad = profundidad if profundidad else 0

        #definimos la regla
        self.regla = regla if regla else ("No", "hay", "regla")

        #se verifica que los set sean del mismo tamaño y se guarda el total de registros.
        if Y.shape[0]==X.shape[0]:
            self.nRegistros=Y.shape[0]
            #print(f"La cantidad de registros son {self.nRegistros}")
        else:
            #print(f"X y Y tienen diferente tamaño")
            pass
        
        #Guadamos las datos en el nodo
        self.Y = Y 
        self.X = X

        #Guardamos función de costo
        if (funcionCosto == "RSS" or funcionCosto == "MSE"):
            self.funcionCosto = funcionCosto
            #print(f"La funcion de costo es {funcionCosto}")
        else:
            self.funcionCosto = "RSS"
            #print(f"La funcion de costo {funcionCosto} no esta especificada se utilizara RSS en su lugar")

        #pomedio de y este es elvalor de predicción del nodo en caso de ser una Hoja  
        self.yPromedio = np.mean(Y)

        #residuos de y contra promedio
        self.residuales = self.Y-self.yPromedio

        #se calcula el valor de la funcion de costo para el nodo
        self.ValorFuncionCosto = self.calculaFuncionCosto(self.funcionCosto)
        #print(f"El valor de la funcion de costo {self.funcionCosto} es {self.ValorFuncionCosto}")

        #creamos los nodos hijos
        self.nodoIzq = None
        self.nodoDer = None

        #mejor caracterisitica , valor y operador
        self.mejorCaracteristica = None
        self.mejorValor = None
        self.operador = None

        #Guardaremos una lista de caracteristicas guardadas solo en el nodo root para fin de hacer predicciones
        if (self.tipoNodo == "root"):
            #caracteristicas categoricas
            self.catCar = self.X.select_dtypes(include = 'object').copy()            
            #caracteristicas numericas
            self.numCar = self.X.select_dtypes(include = 'number').copy()
            self.totalCaracteristicas = len(self.catCar.columns)+len(self.numCar.columns)


        
    def calculaFuncionCosto(self,funcionCosto):
        #calculamos el valor de la funcion de costro del nodo así como se nos entrega
        if (self.funcionCosto=="MSE"):
            return np.sum(self.residuales ** 2) / self.nRegistros
        else:
            return np.sum(self.residuales ** 2)
    
    def numMedios(self,x):
        valores = sorted(x)
        resultado = list()
        for i in range(len(x)-1):
            resultado.append(valores[i]+(valores[i+1]-valores[i])/2)
        return resultado 
    
    def calculaMejordivision(self):
        caracteristica = None
        valor = None
        operador = None
        mejorCosto = np.Infinity
        izqTemp = None
        derTemp = None
        nodoIzq = izqTemp
        nodoDer = derTemp
        #caracteristicas categoricas
        catCar = self.X.select_dtypes(include = 'object').copy()
        
        #caracteristicas numericas
        numCar = self.X.select_dtypes(include = 'number').copy()

        for car in numCar:
           #print(f"calculando division numerica de {car}")
           medios = self.numMedios(self.X[car].unique())
           #print(f"La cantidad de medios es: {len(medios)}")
           for m in medios:
               #print(f"Probando la media: {m}")
               xIzqTemp = self.X[self.X[car] <= m]
               yIzqTemp = self.Y.loc[xIzqTemp.index]
               xDerTemp = self.X[self.X[car] > m]
               yDerTemp = self.Y.loc[xDerTemp.index]
               izqTemp = arbolRegresion(yIzqTemp,xIzqTemp,self.funcionCosto,self.minRegDiv,self.maxProfundidad,self.profundidad+1,"Interno")
               derTemp = arbolRegresion(yDerTemp,xDerTemp,self.funcionCosto,self.minRegDiv,self.maxProfundidad,self.profundidad+1,"Interno")
               if (izqTemp.ValorFuncionCosto + derTemp.ValorFuncionCosto < mejorCosto ):
                   mejorCosto = izqTemp.ValorFuncionCosto + derTemp.ValorFuncionCosto
                   caracteristica = car
                   valor = m
                   operador = "<="
                   nodoIzq = izqTemp
                   nodoDer = derTemp
        
        for car in catCar:
           cat = self.X[car].unique()
           for c in cat:
               xIzqTemp = self.X[self.X[car] == c]
               yIzqTemp = self.Y.loc[xIzqTemp.index]
               xDerTemp = self.X[self.X[car] != c]
               yDerTemp = self.Y.loc[xDerTemp.index]
               izqTemp = arbolRegresion(yIzqTemp,xIzqTemp,self.funcionCosto,self.minRegDiv,self.maxProfundidad,self.profundidad+1,"Interno")
               derTemp = arbolRegresion(yDerTemp,xDerTemp,self.funcionCosto,self.minRegDiv,self.maxProfundidad,self.profundidad+1,"Interno")
               if (izqTemp.ValorFuncionCosto + derTemp.ValorFuncionCosto < mejorCosto ):
                  mejorCosto = izqTemp.ValorFuncionCosto + derTemp.ValorFuncionCosto
                  caracteristica = car
                  valor = c
                  operador = "="
                  nodoIzq = izqTemp
                  nodoDer = derTemp
        regla = (caracteristica,operador,valor)
        #print(f"{regla[0]} {regla[1]} {regla[2]}")
        return (regla,nodoIzq,nodoDer)
        
    
    def entrenar(self):
        if (self.profundidad < self.maxProfundidad and self.nRegistros >= self.minRegDiv):
            #print("Calculando nodo")
            self.regla, self.nodoIzq, self.nodoDer = self.calculaMejordivision()
            if(self.nodoIzq==None):
                #print("cree una hoja")
                self.tipoNodo = "hoja"
            else:
                self.nodoIzq.entrenar()
                self.nodoDer.entrenar()
        else:
            #print("cree una hoja")
            self.tipoNodo = "hoja"
        self.entrenado = 1
    
    def imprimirArbol(self):
        nodoNivel = self.profundidad
        nivelActual = "|---"
        nivelSuperior = "|   "
        pre = ""
        if (self.tipoNodo == "hoja"):
            for i in range(nodoNivel):
                pre = pre + nivelSuperior
            preValor = pre + nivelSuperior
            pre = pre + nivelActual
            #print (f"{pre} {self.regla[0]} {self.regla[1]} {self.regla[2]}")
            print (f"{preValor} valor: {self.yPromedio}")
        else:
            for i in range(nodoNivel):
                pre = pre + nivelSuperior
            pre = pre + nivelActual
            print (f"{pre} {self.regla[0]} {self.regla[1]} {self.regla[2]}")
            self.nodoIzq.imprimirArbol()
            if (self.regla[1] =="<="):
                contrario = ">"
            else:
                contrario = "!="
            print (f"{pre} {self.regla[0]} {contrario} {self.regla[2]}")                
            self.nodoDer.imprimirArbol()
    
    def evalua(self, reg):
        if (self.tipoNodo == "hoja"):
            return (self.yPromedio)
        else:
            if (self.regla[1]=="<="):
                if (reg[self.regla[0]] <= self.regla[2]):
                    return self.nodoIzq.evalua(reg)
                else:
                    return self.nodoDer.evalua(reg)
            else:
                if (reg[self.regla[0]] == self.regla[2]):
                    return self.nodoIzq.evalua(reg)
                else:
                    return self.nodoDer.evalua(reg)

    def predecir(self,X):
        y = []
        if(len(X.columns)==self.totalCaracteristicas):
            for car in X.columns:
                if (car not in self.catCar and car not in self.numCar):
                    print(f"La caracteristica {car} no coincide")
                    return (-1)
        for i in range(len(X)):
            reg = X.iloc[i,:]
            y.append(self.evalua(reg))
        return y

    def calEntrenamieto(self):
        if (self.entrenado):
            yhat = self.predecir(self.X)
            yhat = pd.Series(yhat)
            r = self.Y.values - yhat.values
            u = (r ** 2).sum()
            v = ((self.Y - self.Y.mean()) ** 2).sum()
            return (1-(u/v))
        else:
            print(f"El modelo no se ha entrenado")
            return(-1)
    
    def calPrueba(self,X,Y):
        if (self.entrenado):
            yhat = self.predecir(X)
            yhat = pd.Series(yhat)
            r = Y.values - yhat.values
            u = (r ** 2).sum()
            v = ((Y - Y.mean()) ** 2).sum()
            return (1-(u/v))
        else:
            print(f"El modelo no se ha entrenado")
            return(-1)
        