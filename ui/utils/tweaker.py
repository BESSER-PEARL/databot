# https://github.com/streamlit/streamlit/issues/3888
# Source: https://gist.github.com/scanzy/e6c2a75894affc7245fc93fa33a09c74
import random as rd
import functools as ft

import streamlit as st
import streamlit.components.v1 as components


# Domanda: come applicare stili css solo ad alcuni elementi streamlit?
# Risposta: iniettare js che aggiorni id e classe dell'elemento precedente


def InjectJs(js: str, atEveryRerun: bool = False) -> None:
    """Inietta nella pagina il codice JS specificato.
    La variabile "element" contiene il tag <div> aggiunto alla pagina.
    """

    components.html(
        "<script type='text/javascript'>\n" +

        # se il codice va iniettato ad ogni rerun
        # aggiunge un commento che varia sempre
        (f"// random number: {rd.random()}\n" if atEveryRerun else "") +

        # ottiene tutti gli iframe e cerca quello corrente
        "element = Array.from(parent.document.getElementsByTagName('iframe'))" +
        ".find(x => x.contentDocument == document).parentElement;\n" +

        # rende invisibile l'elemento creato
        "element.style.display = 'none';\n" +

        # inietta il codice JS
        js + "\n</script>",
        height=0,
    )


def AddAttributes(*, id: str = None, cls: str = None, css: str = None) -> None:
    """Aggiunge id e classe specificati all'elemento html precedente a questo.
    Consente di iniettare anche codice css, utilizzando "#id" per l'id dell'elemento.
    Sfortunatamente ad ogni rerun c'è un piccolo istante in cui le classi sono resettate. 
    Esempi:

    AddAttributes(id = "my-element-id")
    AddAttributes(cls = "my-awesome-class")
    AddAttributes(id = "my-element-id", css = "#my-element-id { font-size: 50px; }"
    """

    # codice JS da iniettare
    jsCode = ""

    # aggiunge la classe specificata all'elemento precedente
    if cls is not None:
        jsCode += f"element.previousElementSibling.classList.add('{cls}');\n"

    # aggiunge l'id specificato all'elemento precendete
    if id is not None:
        jsCode += f"element.previousElementSibling.id = '{id}';\n"

    # inietta il codice JS nella pagina
    InjectJs(jsCode, atEveryRerun=cls is not None)

    # inietta eventuale codice css
    if css is not None:
        InjectCss(css.replace("#id", ("#" + id) or "#id"))


def InjectCss(css: str) -> None:
    """Inietta nella pagina il codice CSS specificato.
    Esempio: InjectCss("#my-id { color: red; } .my-class { font-size: 10px; }")
    """

    # ottiene l'id html per in nuovo elemento da creare, con il css
    id = "tw-" + str(hash(css))

    # aggiunge il css
    st.markdown("<style>#" + id + " { display: none; } " +
                css + "</style>", unsafe_allow_html=True)

    # e nasconde il blocco appena creato
    AddAttributes(id=id)


class Tweaker(type):
    """Shadow del modulo streamlit, con funzione di aggiunta classi CSS."""

    def __getattr__(self, name):
        """Ottiene un wrapper per una funzione streamlit."""

        # ottiene la funzione streamlit corrispondente
        stFunc = getattr(st, name)

        @ft.wraps(stFunc)
        def newFunc(*args, id=None, cls=None, css=None, **kwargs):
            """Nuova funzione che utilizza cssClass."""

            # mostra il widget
            retVal = stFunc(*args, **kwargs)

            # se la classe CSS è specificata ed è una funzione
            # la chiama, utilizzando il valore del widget
            if cls is not None and callable(cls):
                cls = cls(retVal)

            # se specificati, applica gli attributi, e inietta il css
            if any([id, cls, css]):
                AddAttributes(id=id, cls=cls, css=css)

            return retVal

        # ritorna la funzione da utilizzare
        return newFunc


class st_tweaker(metaclass=Tweaker):
    """Shadow del modulo streamlit, con funzione di aggiunta classi CSS.
    Esempi di utilizzo:

    # id html
    st_tweaker.text_input(label = "My label", id = "my-element-id")

    # regole css
    st_tweaker.text_input(label = "My label, id = "my-element-id",
        css = "#id label p { font-size: 50px; }")

    # classe statica
    st_tweaker.text_input(label = "My label", cls = "green",
        css = ".green label p { color: green; }")

    # classe dinamica (dipendente dal valore)
    st_tweaker.text_input(label = "My label",
        cls = lambda value: "green" if value == "Hello!" else None,
        css = ".green label p { color: green; }",
    )
    """