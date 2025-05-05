# 📚 Cheat Sheet Python - Fondamentali

---

## 1. 📌 Fondamenti di Python

### Variabili e Tipi di Dati
- Le variabili memorizzano dati di vario tipo:
    ```python
    string_var = "Ciao, Mondo!"  # Stringa
    int_var = 42                 # Intero
    float_var = 3.14             # Float
    bool_var = True              # Booleano
    list_var = [1, 2, 3]         # Lista
    dict_var = {"chiave1": "valore1", "chiave2": ["valore2", 5]}  # Dizionario
    ```

> **Nota:** Python è tipizzato dinamicamente: il tipo di variabile è determinato automaticamente.

---

## 2. 🔧 Funzioni

- Le funzioni sono blocchi di codice riutilizzabili.
- Sintassi base:
    ```python
    def nome_funzione(parametri):
        # Blocco di codice
        return risultato
    ```

- Esempio:
    ```python
    def somma(a, b):
        return a + b

    risultato = somma(5, 3)  # Output: 8
    ```

> **Tip:** Se non si usa `return`, la funzione restituisce `None`.

---

## 3. 🧩 Programmazione Orientata agli Oggetti (OOP)

### Classi e Oggetti
- Una **classe** definisce il modello per creare **oggetti**(istanze), che possono contenere dati (attributi) e funzioni (metodi):
    ```python
    class Persona:
        def __init__(self, nome, eta):
            self.nome = nome
            self.eta = eta

        def saluta(self):
            return f"Ciao, mi chiamo {self.nome}!"

    p1 = Persona("Alice", 25)
    print(p1.saluta())  # Output: Ciao, mi chiamo Alice!
    ```
- `__init__` è il costruttore: viene chiamato automaticamente quando si crea un nuovo oggetto (`Persona(...)`) e serve per inizializzarne gli attributi.
- `self` rappresenta l’istanza corrente e deve essere sempre il primo parametro dei metodi: consente di accedere agli attributi e agli altri metodi dell’oggetto.

### Ereditarietà e Sottoclassi
- Una **sottoclasse** eredita tutti gli attributi e metodi dalla classe genitore (superclasse):
    ```python
    class Studente(Persona):
        def __init__(self, nome, eta, corso):
            super().__init__(nome, eta)  # Chiama il costruttore della classe genitore
            self.corso = corso
            
        def studia(self):
            return f"{self.nome} sta studiando {self.corso}"
            
        def saluta(self):  # Sovrascrive il metodo della classe genitore
            return f"{super().saluta()} Sono uno studente di {self.corso}."
    
    s1 = Studente("Marco", 20, "Informatica")
    print(s1.saluta())  # Output: Ciao, mi chiamo Marco! Sono uno studente di Informatica.
    ```
- `super()` permette di accedere ai metodi della classe genitore
- Una sottoclasse può aggiungere nuovi metodi o attributi
- Una sottoclasse può sovrascrivere (override) i metodi della classe genitore

---

## 4. 🔄 Condizioni e Cicli

### Condizionali
```python
x = 10
if x > 5:
    print("x è maggiore di 5")
elif x == 5:
    print("x è uguale a 5")
else:
    print("x è minore di 5")
```

### Cicli

- **For** su intervallo:
    ```python
    for i in range(5):
        print(i)  
    # Output:
    # 0 
    # 1 
    # 2 
    # 3 
    # 4
    ```

- **For** su lista:
    ```python
    frutti = ["mela", "banana", "ciliegia"]
    for frutto in frutti:
        print(frutto) 
    # Output:
    #  mela
    #  banana
    #  ciliegia
    ```

- **For** su dizionario:
    ```python
    persona = {"nome": "Alice", "età": 25}
    for chiave, valore in persona.items():
        print(f"{chiave}: {valore}") 
    # Output:
    #  nome: Alice
    #  età: 25
    ```

- **While**:
    ```python
    n = 0
    while n < 5:
        print(n)
        n += 1
    # Output: 
    # 0 
    # 1
    # 2
    # 3
    # 4
    ```

> **Tip:** Usa `break` per uscire da un ciclo, `continue` per saltare all'iterazione successiva.

---

## 5. ✂️ Manipolazione delle Stringhe

- Le stringhe sono **immutabili** (non modificabili direttamente).
- Operazioni comuni:
    ```python
    testo = "Ciao, Mondo!"

    print(testo.lower())       # 'ciao, mondo!'
    print(testo.upper())       # 'CIAO, MONDO!'
    print(testo.split(","))    # ['Ciao', ' Mondo!']
    print("-".join(["a", "b", "c"]))  # 'a-b-c'
    print(testo.strip())       # Rimuove spazi all'inizio/fine
    print(testo.replace("Ciao", "Salve"))  # 'Salve, Mondo!'
    print(f"Messagio da formattare: {testo}") # 'Messaggio da formattare: Ciao, Mondo!"
    ```

### Slicing di Stringhe
```python
parola = "taboo"

print(parola[0])    # 't'
print(parola[-1])   # 'o'
print(parola[1:4])  # 'abo'
print(parola[::-1]) # 'oobat' (invertita)
```

---

## 6. 📋 Liste e Dizionari

### Liste
- Collezione ordinata di elementi:
    ```python
    lista = [1, 2, 3]

    lista.append(4)       # [1, 2, 3, 4]
    lista.remove(2)       # [1, 3, 4]
    lista[0] = 10         # [10, 3, 4]
    lista[-1] = 0         # [10, 3, 0]
    print(len(lista))     # 3
    ```

- Costruire liste in modo compatto:
    ```python
    numeri = [1, 2, 3, 4, 5]
    quadrati = [x**2 for x in numeri]
    print(quadrati)  # [1, 4, 9, 16, 25]
    ```

- Con condizione:
    ```python
    pari = [x for x in numeri if x % 2 == 0]
    print(pari)  # [2, 4]
    ```

> **Tip:** Le liste possono contenere tipi misti (es. numeri, stringhe, liste annidate).

### Dizionari
- Collezione di coppie chiave-valore:
    ```python
    dizionario = {"nome": "Alice", "età": 25}

    dizionario["città"] = "Roma"    # Aggiunge nuova chiave
    eta = dizionario.get("età")     # 25
    chiavi = dizionario.keys()      # dict_keys(['nome', 'età', 'città'])
    valori = dizionario.values()    # dict_values(['Alice', 25, 'Roma'])
    ```

> **Tip:** Usare `get` evita errori se una chiave non esiste (`None` come default).

---


## 7. 🛡️ Gestione degli Errori

- Gestisci eccezioni usando `try/except`:
    ```python
    try:
        risultato = 10 / 0
    except ZeroDivisionError:
        print("Non puoi dividere per zero!")
    except Exception as e:
        print(f"Errore generico: {e}")
    ```

---

## 8. 📦 Uso di Librerie Esterne

- Importare librerie:
    ```python
    import numpy as np

    array = np.array([1, 2, 3])
    print(array.mean())  # Output: 2.0
    ```
---
