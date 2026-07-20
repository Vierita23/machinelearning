"""Funciones auxiliares de evaluación y visualización para clasificación.

Este módulo expone `np` y `plt` para que puedan usarse en el notebook mediante
`from evaluacion_funciones import *`, tal como espera la práctica.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def evaluacion(y_true, y_pred, metricas):
    """Aplica un diccionario de métricas sobre las etiquetas reales y predichas.

    Parameters
    ----------
    y_true : array-like
        Etiquetas reales.
    y_pred : array-like
        Etiquetas predichas por el modelo.
    metricas : dict
        Diccionario {nombre: funcion(y_true, y_pred)}.

    Returns
    -------
    dict
        Diccionario {nombre: valor_de_la_metrica}.
    """
    resultados = {}
    for nombre, funcion in metricas.items():
        resultados[nombre] = funcion(y_true, y_pred)
    return resultados


def mapa_modelo_clasif_2d(X, y, modelo, resultados, nombre, resolucion=0.02):
    """Dibuja las fronteras de decisión de un modelo entrenado con 2 atributos.

    Parameters
    ----------
    X : ndarray de forma (n_muestras, 2)
        Datos de entrada (deben tener exactamente 2 características).
    y : array-like
        Etiquetas de clase.
    modelo : estimador entrenado de scikit-learn
        Modelo con método `predict`.
    resultados : dict
        Métricas calculadas, se muestran en el título.
    nombre : str
        Nombre del algoritmo, se muestra en el título.
    resolucion : float
        Paso de la malla para pintar las regiones de decisión.
    """
    X = np.asarray(X)
    y = np.asarray(y)

    colores = ('#FF9999', '#99CC99', '#9999FF', '#FFCC99', '#CC99FF')
    clases = np.unique(y)
    cmap_fondo = ListedColormap(colores[:len(clases)])

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, resolucion),
                         np.arange(y_min, y_max, resolucion))

    Z = modelo.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.figure()
    plt.contourf(xx, yy, Z, alpha=0.3, cmap=cmap_fondo)
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())

    for idx, cl in enumerate(clases):
        plt.scatter(X[y == cl, 0], X[y == cl, 1],
                    c=colores[idx], edgecolors='black',
                    label='Clase %s' % str(cl))

    titulo = "%s" % nombre
    if isinstance(resultados, dict) and len(resultados) > 0:
        titulo += " -> " + ", ".join("%s: %.3f" % (k, v) for k, v in resultados.items())
    plt.title(titulo)
    plt.xlabel('Atributo 1')
    plt.ylabel('Atributo 2')
    plt.legend()
    plt.grid()
    plt.show()
