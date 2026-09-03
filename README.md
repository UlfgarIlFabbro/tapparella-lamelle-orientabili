# Tapparella Lamelle Orientabili

Integrazione custom per **Home Assistant** dedicata alle tapparelle **Cherubini con lamelle orientabili**, utilizzando uno **Shelly 2PM / Plus 2PM** configurato in modalità tapparella.

L'integrazione crea automaticamente due entità per ogni tapparella:

- `cover` → controllo della tapparella
- `lock` → controllo dello stato delle lamelle

L'integrazione è progettata per gestire **più tapparelle contemporaneamente** senza dover modificare il codice quando viene aggiunta una nuova tapparella.

## Funzionamento

Ogni tapparella può trovarsi in uno dei seguenti stati logici:

| Stato | Tapparella | Lamelle |
|---|---|---|
| **CLOSED** | chiusa | bloccate |
| **OPEN** | aperta | bloccate |
| **TILT** | aperta | sbloccate / lamelle aperte |

### Comandi

- **SU** → apre completamente la tapparella
- **GIÙ** → chiude completamente la tapparella
- **Lamelle** → apre/chiude le lamelle
- **Pressione prolungata** → comando fisico per l'orientamento delle lamelle

La gestione dello stato viene mantenuta anche attraverso i comandi fisici collegati allo Shelly.

## Gestione di più tapparelle

Una delle caratteristiche principali dell'integrazione è la gestione automatica delle tapparelle.

Ogni nuova tapparella viene semplicemente aggiunta dall'interfaccia dell'integrazione.

**Non è necessario modificare il codice dell'integrazione né aggiungere manualmente la nuova tapparella a un gruppo.**

Le nuove tapparelle vengono automaticamente riconosciute dai comandi globali e dalle card Home Assistant.

## Comandi globali

L'integrazione mette a disposizione tre servizi:

### `tapparella_lamelle_orientabili.open_all`

Apre tutte le tapparelle gestite dall'integrazione.

### `tapparella_lamelle_orientabili.close_all`

Chiude tutte le tapparelle gestite dall'integrazione.

### `tapparella_lamelle_orientabili.open_all_tilt`

Porta tutte le tapparelle nello stato **TILT**, cioè con tapparella aperta e lamelle sbloccate.

I comandi vengono eseguiti sulle tapparelle gestite dall'integrazione senza necessità di utilizzare un gruppo Home Assistant separato.

## Card di gruppo

Le card Home Assistant possono utilizzare direttamente i tre servizi dell'integrazione:

```yaml
service: tapparella_lamelle_orientabili.open_all
```

```yaml
service: tapparella_lamelle_orientabili.close_all
```

```yaml
service: tapparella_lamelle_orientabili.open_all_tilt
```

Le card possono inoltre verificare automaticamente lo stato di **tutte le tapparelle TLO presenti**, senza dover indicare manualmente i nomi delle entità.

### Indicazione dello stato

Le card possono diventare verdi solamente quando **tutte** le tapparelle si trovano nello stesso stato completo:

- tutte **CLOSED** → verde su "CHIUDI TUTTE"
- tutte **OPEN** → verde su "ALZA TUTTE"
- tutte **TILT** → verde su "APRI TUTTE LE LAMELLE"
- stati misti → nessuna card verde

In questo modo l'indicazione visiva rappresenta realmente lo stato dell'intero gruppo.

## Requisiti

- Home Assistant
- Motore Cherubini compatibile con orientamento delle lamelle
- Isolatore Cherubini **A510052** o compatibile
- Shelly **2PM / Plus 2PM**
- Shelly configurato in modalità **Roller / Cover**
- Input Shelly configurati in modalità **Detached**

## Configurazione Shelly

Configurazione utilizzata:

- **SU** → Open Cover
- **GIÙ** → comando HTTP per la chiusura completa
- **HOLD** → Close Cover / comando per l'orientamento delle lamelle

Il comando HTTP utilizzato per la chiusura completa è:

```text
http://127.0.0.1/roller/0?go=close&duration=1
```

Per portare il motore nello stato TILT viene invece utilizzato:

```text
http://127.0.0.1/roller/0?go=close
```

## Installazione tramite HACS

Aggiungere questo repository come **Custom Repository** in HACS e selezionare **Integration**.

Repository:

`UlfgarIlFabbro/tapparella-lamelle-orientabili`

Dopo l'installazione riavviare Home Assistant.

Successivamente:

**Impostazioni → Dispositivi e servizi → Aggiungi integrazione → Tapparella Lamelle Orientabili**

e aggiungere gli Shelly desiderati.

## Aggiunta di una nuova tapparella

Quando viene installato un nuovo Shelly:

1. Aggiungerlo normalmente all'integrazione ufficiale Shelly di Home Assistant.
2. Configurarlo come tapparella.
3. Aprire **Tapparella Lamelle Orientabili**.
4. Selezionare **Aggiungi dispositivo**.
5. Selezionare il nuovo Shelly.
6. Assegnare il nome desiderato.

Da quel momento la nuova tapparella viene automaticamente gestita dall'integrazione e inclusa nei comandi globali.

Non è necessario modificare le card o creare un nuovo gruppo.

## Matter / Google Home

Le entità create dall'integrazione possono essere utilizzate con le funzionalità di esposizione di Home Assistant e, se configurate, possono essere rese disponibili tramite **Matter** e successivamente utilizzate nei sistemi compatibili.

## Note

Questa integrazione è stata sviluppata specificamente per la gestione di tapparelle Cherubini con lamelle orientabili attraverso Shelly.

La gestione dello stato è volutamente basata sulla combinazione di:

- stato `cover`
- stato `lock`

in modo da distinguere correttamente una tapparella completamente aperta da una tapparella con lamelle orientate.

## Versione

**1.4.1**

### Novità della versione 1.4.1

- Gestione automatica di più tapparelle
- Aggiunti servizi `open_all`, `close_all` e `open_all_tilt`
- Gestione dinamica delle tapparelle senza gruppi Home Assistant
- Stato TILT gestito tramite `cover` + `lock`
- Comandi globali idempotenti
- Supporto alla futura aggiunta di nuove tapparelle senza modificare il codice
- Attributi `tlo` e `tlo_slug` per il riconoscimento automatico delle entità
- Migliorata la gestione delle card di gruppo
