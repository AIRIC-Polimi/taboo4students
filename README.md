# AIRIC Taboo Challenge

[![Apri in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/AIRIC-Polimi/taboo4students?quickstart=1)

## Regole del gioco

Il gioco prevede l'interazione tra due giocatori virtuali (LLM-players): **agent** e **guesser**.  
- **Agent**: riceve una parola da far indovinare e una lista di parole bandite. Deve fornire un indizio che aiuti il guesser a indovinare la parola, rispettando le regole.  
- **Guesser**: riceve l'indizio dall'agent e prova a indovinare la parola obiettivo.

### Obiettivo

Il tuo obiettivo è sviluppare un sistema efficace per il giocatore virtuale **agent**, che deve fornire indizi utili al giocatore **guesser** per indovinare la parola obiettivo, rispettando le regole specifiche del livello di difficoltà selezionato. 
Per raggiungere questo scopo, dovrai concentrarti sulla modifica del file `my_agent_submission.py`, situato nella cartella `agent` (che potrai rinominare a piacimento, e anche duplicare nel caso in cui tu voglia testare diversi approcci alla challenge). In particolare, sarà necessario implementare una sottoclasse di `Agent` (la puoi chiamare come preferisci) ed implementare i metodi `get_name()` (perché la tua soluzione si possa riconoscere dalle altre quando verrà stilata la classifica finale), il metodo `get_hint()` (per risolvere primi livelli), ed il metodo `custom_similarity_search()` (per uno degli ultimi livelli, vedi sotto). Il metodo base, `get_hint()`, dovrà:

- generare indizi che rispettino le regole del livello di difficoltà scelto;
- massimizzare l'efficacia degli indizi per aiutare il guesser a indovinare correttamente la parola obiettivo;
- garantire che gli indizi siano conformi alle restrizioni imposte dai vari livelli (vedi sotto per i dettagli di ciascun livello).
  
Attenzione: Azure OpenAI ha dei filtri attivi riguardo contenuti inappropriati. Evita di inserire prompt che possano innescare tali filtri, come tentativi di jailbreaking, richieste di contenuti violenti, offensivi, espliciti o altri contenuti contrari alle policy di utilizzo. Se testi il tuo codice utilizzando lo script messo a disposizione (`scripts/test_solutions.py`) gli errori legati al filtro di contenuti stamperanno un messaggio di questo tipo nella console:

```
The given prompt has triggered the Azure OpenAI content filter; please try to eliminate sensitive words. Prompt: 'THIS IS THE PROMPT YOU SENT'.
```

### Livelli di difficoltà

Il gioco è strutturato in diversi livelli, ciascuno con regole aggiuntive:

- **Livello 1**:  
  - Modalità base di Taboo.  
  - L'indizio deve aiutare il guesser a indovinare la parola obiettivo, ma non può contenere nessuna delle parole bandite (né la parola obiettivo).

- **Livello 2**:  
  - Oltre alle regole del livello 1, la parola da indovinare deve essere riportata in francese dal guesser.  
    *Esempio*: Se la parola da indovinare è "gatto", il guesser deve rispondere "chat".

- **Livello 3**:  
  - Oltre alle regole del livello 1, l'indizio fornito dall'hinter deve essere scelto esclusivamente da una lista predefinita di indizi. L'indizio non può essere modificato in alcun modo: deve essere utilizzato esattamente come appare nella lista.
  - Per risolvere questo livello, è **necessario**:
    1. utilizzare gli strumenti forniti dalla classe `Agent` (e sue sottoclassi):
        - L'attributo `llm.hints_db`: un dizionario che mappa **tutti gli indizi a tua dispozione** ai loro embedding vettoriali (`{hint: hint_embedding}`).
        - Il metodo `llm.embed_text()`: per generare l'embedding di un nuovo testo
    2. Implementare il metodo `custom_similarity_search()` nella tua sottoclasse di `Agent`, in modo che restituisca i k indizi più rilevanti (tra quelli in `llm.hints_db`) rispetto un nuovo testo di input.

    Ricorda: Gli embedding sono rappresentazioni vettoriali che catturano il significato semantico di un testo. Pertanto, testi con significati simili avranno vettori "vicini" nello spazio vettoriale degli embedding!

  - Per semplificare l'utilizzo degli embedding, ecco un esempio pratico:
  ```python
  # Definisci la tua classe MyAgent come sottoclasse di Agent
  class MyAgent(Agent):
      def my_agent_method(self, text:str):
          # Genera l'embedding di un nuovo testo
          new_embedding = self.llm.embed_text(text)
          
          # Accedi al dizionario di indizi predefiniti
          print(f"Dict hints-embedding:\n{self.llm.hints_db}")
          
          # Mostra il testo e il suo embedding
          print(f"New text with embedding: {text} - {new_embedding}")
  ```

- **Livello 4**:  
  - Oltre alle regole del livello 1, l'indizio fornito dall'hinter può avere una lunghezza massima di 5 parole.

### Scoring delle soluzioni

Al termine della challenge, le soluzioni sottomesse (i.e., le implementazioni di `Agent` fornite da ciascun team, sotto forma di un singolo file python) verranno testate utilizzando lo script `scripts/test_solutions.py` (lo stesso che i partecipanti possono utilizzare localmente per testare la propria soluzione), il quale contiene il seguente meccanismo di scoring:

- un punto per ciascuna risposta corretta (i.e., tale per cui il *guesser* fornisce come risposta esattamente la parola da indovinare, carattere per carattere), per andare a costituire il punteggio totale per ciascun livello
- il punteggio totale di ciascun livello viene poi moltiplicato per il valore del livello stesso (calcolato come la radice cubica del numero corrispondente al livello, quindi ad esempio `1` per il livello 1, `1.2599` per il livello 2, e così via)
- i punti ottenuti nei vari livelli vengono sommati, il risultato viene utilizzato per ordinare le soluzioni e formare la classifica

## Configurazione

Per poter partecipare alla challenge, si può configurare il proprio ambiente di sviluppo in diverse modalità:

* utilizzando GitHub Codespaces, che da accesso ad un ambiente preconfigurato e già pronto all'uso tramite browser (opzionalmente collegabile a VSCode in locale)
* scaricando e configurando in maniera automatica questo repository, tramite lo script `scripts/repo_setup.py`
* clonando e configurando manualmente questo repository

NOTA: nel caso in cui si voglia scaricare e configurare il repostory localmente (sia in maniera automatica che in maniera manuale), è richiesta avere un'installazione funzionante di Python e un'ambiente di sviluppo configurato (consigliamo Visual Studio Code).

A prescindere dal metodo scelto per la configurazione, per verificare che tutto funzioni correttamente si può testare l'agent di esempio utilizzando lo script di test in questo modo: `python scripts/test_solutions.py --level 1 --quiet` (naturalmente, l'agent otterrà zero punti in quanto non ha un'implementazione realmente funzionante del metodo `get_hint()`). Lo script di test può essere configurato in vari modi (ad esempio, supporta l'utilizzo di diversi LLM di OpenAI, o il test di singoli livelli della challenge), per tutti i dettagli basta seguire il messaggio di help disponibile con `python scripts/test_solutions.py -h`.

### GitHub Codespaces

Per utilizzare GitHub Codespaces, è sufficiente cliccare [questo link](https://codespaces.new/AIRIC-Polimi/taboo4students?quickstart=1) (lo stesso contenuto nel badge all'inizio del README) e attendere che la configurazione automatica venga completata (la prima volta ci mette qualche minuto, eventuali restart successivi sono molto più veloci).

### Setup automatico tramite script

Per scaricare e configurare automaticamente il repository in locale utilizzando lo script preparato dagli organizzatori è sufficiente aprire un terminale (powershell su Windows) ed eseguire il comando sottostante, inserendo i dati richiesti (cartella nella quale clonare il repository, API KEY di Azure OpenAI fornita dagli organizzatori) quando viene richiesto.

Linux e macOS:
```
python3 <(curl -sSL https://raw.githubusercontent.com/AIRIC-Polimi/taboo4students/refs/heads/main/scripts/repo_setup.py)
```

Windows:
```
powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/AIRIC-Polimi/taboo4students/refs/heads/main/scripts/repo_setup.py | python - --output C:/INSERT/HERE/PATH/TO/CLONE/REPO --api-key INSERT_HERE_API_KEY"
```

Attiva l'ambiente virtuale appena creato con il seguente comando (varia a seconda del sistema operativo usato):

  Linux e macOS:
      
  ```bash
  source .venv-taboo/bin/activate
  ```
      
  Windows:
      
  ```bash
  .\.venv-taboo\Scripts\activate
  ```
      
VSCode dovrebbe automaticamente rilevare l'ambiente virtuale appena creato e suggerire di utilizzarlo per la workspace corrente. Accetta il suggerimento, oppure configurarlo manualmente selezionando l'interprete Python corretto la prima volta che esegui del codice.

### Clone e setup manuale

Segui questi passaggi per clonare e configurare manualmente il progetto in locale:

1. **Clonare la repository**
   - Scarica o clona la repository da GitHub. Per clonare la repository, usa il comando:
     
     ```bash
     git clone https://github.com/AIRIC-Polimi/taboo4students.git PATH/TO/WHERE/YOU/WANT/TO/CLONE
     ```

     Se invece preferisci scaricare la repository in formato ZIP, [clicca qui](https://github.com/AIRIC-Polimi/taboo4students/archive/refs/heads/main.zip).

2. **Aprire il progetto**
   - Apri il progetto nel tuo editor di scelta (è consigliato Visual Studio Code).

3. **Creare un ambiente virtuale**
  - Apri un terminale in Visual Studio Code e crea un ambiente virtuale con il comando `python3 -m venv .venv-taboo`.
  - Se ti viene segnalata la mancanza di python3-venv, puoi installarlo con il comando `sudo apt install python3.12-venv`
  - Attiva l'ambiente virtuale appena creato con il seguente comando (varia a seconda del sistema operativo usato):
    - Linux e macOS:
      
      ```bash
      source .venv-taboo/bin/activate
      ```
      
    - Windows:
      
      ```bash
      .\.venv-taboo\Scripts\activate
      ```
      
  VSCode dovrebbe automaticamente rilevare l'ambiente virtuale appena creato e suggerire di utilizzarlo per la workspace corrente. Accetta il suggerimento, oppure configurarlo manualmente selezionando l'interprete Python corretto la prima volta che esegui del codice.

4. **Installare le dipendenze**
   - Installa le dipendenze del progetto eseguendo il comando (dopo aver attivato l'ambiente virtuale):
     
     ```bash
     pip install -e PATH/TO/REPO
     ```

     Se vuoi essere sicuro che le dipendenze vengano installate all'interno dell'ambiente virtuale appena creato, puoi utilizzare il seguente comando:

     ```bash
     .venv-taboo/bin/pip install -e PATH/TO/REPO
     ```

5. **Configurare il file `.env`**
   - Crea un file `.env` copiando il formato dal file `.env.example`.
   - Inserisci la API KEY di Azure OpenAI fornita dagli organizzatori nel campo `AZURE_OPENAI_API_KEY` del file `.env`
