# Scythe Honeypot

<div align="center">

```
                                    
  ▄▄▄▄▄                             
 ██▀▀▀▀█▄             █▄ █▄         
 ▀██▄  ▄▀            ▄██▄██         
   ▀██▄▄  ▄███▀ ██ ██ ██ ████▄ ▄█▀█▄
 ▄   ▀██▄ ██    ██▄██ ██ ██ ██ ██▄█▀
 ▀██████▀▄▀███▄▄▄▀██▀▄██▄██ ██▄▀█▄▄▄
                  ██                
                ▀▀▀                 
                  H O N E Y P O T
```

**Détecteur d'intrusion personnel — TUI moderne pour Windows**

[![Python](https://img.shields.io/badge/Python-3.12+-00DC82?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Textual](https://img.shields.io/badge/Built%20with-Textual-00DC82?style=flat-square)](https://textual.textualize.io/)
[![License](https://img.shields.io/badge/License-MIT-00DC82?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-00DC82?style=flat-square)](#)

*Partie de la suite **Scythe** — outils de sécurité opérationnelle pour utilisateurs avancés*

</div>

---

## 📖 Sommaire

- [À propos](#-à-propos)
- [Aperçu](#-aperçu)
- [Fonctionnalités](#-fonctionnalités)
- [Comment ça marche](#-comment-ça-marche)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Types de canaries](#-types-de-canaries)
- [Architecture du projet](#-architecture-du-projet)
- [Configuration](#-configuration)
- [Dépannage](#-dépannage)
- [Roadmap](#-roadmap)
- [La suite Scythe](#-la-suite-scythe)
- [Contribuer](#-contribuer)
- [Licence](#-licence)

---

## 🎯 À propos

**Scythe Honeypot** est un outil de **détection d'intrusion personnel** qui te permet de déposer des fichiers piégés (*canaries*) sur ta machine et d'être alerté en temps réel si quelqu'un les touche.

Le concept est simple mais redoutable : tu crées des fichiers qui *ressemblent* à des cibles juteuses pour un attaquant — un faux portefeuille crypto, une fausse clé SSH, un faux dump de base de données — et tu les déposes à des endroits stratégiques sur ton système. Si une personne malveillante (ou un malware) explore ta machine et **touche un de ces fichiers**, tu reçois une notification immédiate avec le nom du processus responsable.

C'est une stratégie de défense **passive et silencieuse** : pas d'agent intrusif, pas de scan permanent, juste des appâts qui dorment jusqu'à ce que quelqu'un morde.

### Pour qui ?

- 🛡️ **Utilisateurs soucieux de leur sécurité** — Détecte les intrusions sur ta machine perso
- 🔍 **Pentesters / red teamers** — Vérifie tes propres mécanismes de détection
- 🧑‍💻 **Sysadmins / DevOps** — Surveille des serveurs avec des appâts crédibles
- 📚 **Étudiants en cybersécurité** — Comprends concrètement ce qu'est un honeypot

---

## 👁️ Aperçu

```
┌──────────────────────────────────────────────────────────────────────┐
│ ↪ Scythe 0.1.0   Home                                                │
├──────────────────────────────────────────────────────────────────────┤
│ ╭─Quick Stats──╮  ╭─Active Canaries──────────────────────────────╮   │
│ │ ● Armed   3  │  │ ◆ #0001 · wallet_backup           ● ARMED    │   │
│ │ ▲ Triggd  1  │  │  Crypto Wallet · ~\Documents\wallet.dat      │   │
│ │ ↻ Total  12  │  │  Created 2h ago · 0 triggers                 │   │
│ ╰──────────────╯  │                  [⏸ Pause] [👁 View] [✕ Delete] │   │
│                   │                                              │   │
│                   │ ⚿ #0002 · ssh_keys             ▲ TRIGGERED   │   │
│                   │  SSH Private Key · ~\.ssh\id_rsa.pem         │   │
│                   │  Created 8h ago · 3 triggers                 │   │
│                   │                  [⏸ Pause] [👁 View] [✕ Delete] │   │
│                   ╰──────────────────────────────────────────────╯   │
│                                                                      │
│ ╭─Last Alert───╮  ╭─Recent Events────────────────────────────────╮   │
│ │ ssh_keys     │  │ 14:32 ssh_keys      MODIFIED  notepad.exe    │   │
│ │ MODIFIED     │  │ 09:15 wallet_backup OPENED    explorer.exe   │   │
│ │ notepad.exe  │  │ 09:14 company_db    READ      python.exe     │   │
│ │ 14:32 today  │  ╰──────────────────────────────────────────────╯   │
│ ╰──────────────╯                                                     │
│                                                                      │
│ ╭─Create New Canary──────────────────────────────────────────────╮   │
│ │ Name: [_______________]                                         │   │
│ │ Type: ( ) Wallet  (•) SSH key  ( ) Password  ( ) DB  ( ) PDF    │   │
│ │ Path: [C:\Users\...\Documents__________________________]        │   │
│ │ Detect: [x] Read  [x] Open  [ ] Copy  [x] Modify  [x] Capture   │   │
│ │                                       [ ▲ DEPLOY CANARY ]       │   │
│ ╰────────────────────────────────────────────────────────────────╯   │
├──────────────────────────────────────────────────────────────────────┤
│ a Add  d Delete  e Edit  v View  f Filter  ^q Quit  ● Connected      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Fonctionnalités

### Cœur du produit

- 🪤 **Création de canaries réalistes** — 6 types de fichiers piégés avec contenu crédible (magic bytes corrects, format de clé SSH valide, structure SQL crédible, etc.)
- 🔔 **Surveillance en temps réel** — Détection instantanée via `watchdog` dès qu'un fichier est modifié, déplacé, ou supprimé
- 🕵️ **Identification du processus responsable** — Capture le nom et le PID du processus qui a touché le fichier, via `psutil`
- 💾 **Persistence SQLite** — Tes canaries et l'historique des événements sont sauvegardés entre les sessions
- 🎯 **Notifications toast** — Alerte visuelle non-bloquante en bas à droite quand un canary est déclenché

### Interface

- 🎨 **TUI moderne** — Inspirée de [Bagels](https://github.com/EnhancedJax/Bagels), construite avec Textual
- 🌈 **Palette signature Scythe** — Vert principal (#00DC82) avec accents amber, cyan, rouge selon le contexte
- 🖱️ **Interactions souris** — Boutons cliquables, formulaires interactifs, tout est accessible souris ET clavier
- 📊 **Dashboard centralisé** — Stats live, dernière alerte, événements récents, et création de canaries dans une seule vue
- 🪟 **Modals stylisés** — Confirmations d'actions destructives, affichage de détails

### Gestion des canaries

- ▶️ **Pause / Resume** — Désactive temporairement un canary sans le supprimer
- 👁️ **Vue détaillée** — Toutes les infos d'un canary (chemin, options de détection, dates, compteur de triggers)
- ✕ **Suppression sécurisée** — Avec confirmation, supprime le canary de la DB ET le fichier sur disque
- 🎛️ **Options de détection granulaires** — Choisis ce qui déclenche une alerte (lecture, modification, copie, suppression)

---

## 🧠 Comment ça marche

### Le principe

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. Tu crées un canary               2. L'app surveille le      │
│     via le formulaire                   fichier en background   │
│                                                                 │
│        ┌────────────┐                    ┌─────────────────┐    │
│        │ wallet.dat │ ◄──── attaquant ──►│ watchdog thread │    │
│        └────────────┘                    └─────────────────┘    │
│                                                  │              │
│  3. L'attaquant touche le fichier                ▼              │
│     (lecture, copie, ouverture, etc.)    ┌─────────────────┐    │
│                                          │   psutil scan   │    │
│                                          └─────────────────┘    │
│                                                  │              │
│                                                  ▼              │
│  4. Tu reçois une alerte avec :          ┌─────────────────┐    │
│     - le nom du canary                   │  notify + DB    │    │
│     - l'événement (READ / MODIFY / etc.) │     write       │    │
│     - le processus responsable           └─────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Pourquoi un fichier "réaliste" ?

Un attaquant intelligent fait souvent un **scan rapide** des fichiers intéressants avant de les exfiltrer. Si ton fichier `wallet.dat` est vide (0 octet) ou contient juste "FAKE", il sera ignoré. **Scythe Honeypot génère des fichiers crédibles** :

- Le faux **wallet** contient les magic bytes Berkeley DB (`00 05 31 62`) suivis de plusieurs Ko de bytes aléatoires (qui ressemblent à du chiffré)
- La fausse **clé SSH** a un en-tête `-----BEGIN OPENSSH PRIVATE KEY-----` valide et 50 lignes de base64
- Le faux **dump SQL** contient `INSERT INTO users VALUES (...)` avec 50 fausses entrées
- Le faux **PDF** est un PDF minimal **valide** qui s'ouvre dans n'importe quel reader avec le texte "CONFIDENTIAL — Internal Use Only"

Bref, c'est suffisamment crédible pour passer un coup d'œil rapide.

---

## 📦 Installation

### Prérequis

- **Windows 10 / 11**
- **Python 3.12** ou supérieur — [télécharger ici](https://www.python.org/downloads/)
- **Git** (recommandé) — [télécharger ici](https://git-scm.com/download/win)

### Étape 1 — Cloner le dépôt

```powershell
git clone https://github.com/KronoxDev/scythe-honeypot.git
cd scythe-honeypot
```

Si tu n'as pas Git, télécharge le ZIP depuis GitHub et dézippe-le.

### Étape 2 — Créer un environnement virtuel

C'est une bonne pratique pour isoler les dépendances de Scythe Honeypot du Python global.

```powershell
python -m venv .venv
```

### Étape 3 — Activer l'environnement

```powershell
.\.venv\Scripts\Activate.ps1
```

> 💡 Si PowerShell te dit que les scripts sont désactivés :
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Tu dois voir `(.venv)` apparaître au début de ton prompt.

### Étape 4 — Installer les dépendances

```powershell
pip install -r requirements.txt
pip install -e .
```

La première fois, ça télécharge environ 50 Mo de dépendances (`textual`, `watchdog`, `psutil`, `pydantic`, `cryptography`).

### Étape 5 — Lancer l'application

```powershell
python -m scythe_honeypot
```

Et c'est parti 🚀

---

## 🎮 Utilisation

### Créer un premier canary

1. Dans la section **Create New Canary** en bas du dashboard :
   - **Name** : un nom interne (ex: `wallet_backup_2026`)
   - **Type** : choisis le type de fichier piège (Crypto Wallet, SSH Key, etc.)
   - **Path** : le **dossier** où déposer le fichier (ex: `C:\Users\Toto\Documents`)
   - **Detect** : coche les types d'événements qui déclencheront une alerte
2. Clique sur **▲ DEPLOY CANARY**
3. Une notification verte confirme la création
4. Le canary apparaît dans la liste **Active Canaries**

> ⚠️ **Important** : choisis bien le **path**. C'est le **dossier**, pas le chemin complet du fichier. L'app ajoute automatiquement le bon nom + extension.

### Tester qu'un canary fonctionne

1. Va dans le dossier où tu as déposé le canary (Explorateur Windows)
2. **Modifie le fichier** : ouvre-le avec Notepad, ajoute un caractère, sauve
3. **Reviens dans Scythe Honeypot** : tu devrais voir :
   - 🔔 Une notification orange : `⚠ CANARY TRIGGERED — wallet_backup → MODIFIED by notepad.exe`
   - Le statut du canary qui passe à `▲ TRIGGERED` avec une bordure orange
   - Une nouvelle ligne dans **Recent Events**
   - Le compteur **Triggered** qui s'incrémente

### Gérer un canary

Sur chaque card de canary, tu as 3 boutons :

| Bouton | Action |
|---|---|
| **⏸ Pause** | Désactive temporairement la surveillance (le fichier reste sur disque, mais aucune alerte) |
| **▶ Resume** | Réactive un canary mis en pause |
| **👁 View** | Ouvre une fenêtre détaillée (chemin, options, dates, compteur de triggers) |
| **✕ Delete** | Supprime définitivement le canary ET le fichier sur disque (avec confirmation) |

### Raccourcis clavier

| Touche | Action |
|---|---|
| `Tab` | Naviguer entre les éléments interactifs |
| `Espace` | Cocher/décocher une checkbox |
| `Entrée` | Activer un bouton |
| `Échap` ou `Ctrl+Q` | Quitter l'application |

---

## 📁 Types de canaries

Chaque type de canary génère un fichier au **format réaliste** pour passer une inspection rapide.

| Type | Extension | Description | Use case typique |
|---|---|---|---|
| **Crypto Wallet** | `.dat` | Header Berkeley DB valide + bytes aléatoires (~5 Ko) | À mettre dans `Documents`, `Desktop`, profil utilisateur |
| **SSH Private Key** | `.pem` | Format OpenSSH valide avec base64 simulé | À mettre dans `~\.ssh\`, `Documents\keys\` |
| **Password File** | `.txt` | Liste de credentials simulés (admin:hash, api_key=...) | À mettre dans `Documents`, dossiers de travail |
| **Database Dump** | `.sql` | Vrai début de dump MySQL avec INSERT statements | À mettre dans dossiers de projet, backups |
| **Confidential PDF** | `.pdf` | PDF minimal valide ouvrant sur "CONFIDENTIAL — Internal Use Only" | À mettre dans `Documents`, dossiers RH/Finance fictifs |
| **Source Archive** | `.zip` | Header ZIP valide + payload aléatoire | À mettre dans `Downloads`, dossiers projet |

> 💡 **Conseil** : place les canaries à des endroits **plausibles** pour un attaquant. Un `wallet.dat` dans `C:\Windows\System32` n'a aucun sens. Un `wallet.dat` dans `Documents\Crypto\` est crédible.

---

## 🏗️ Architecture du projet

```
scythe-honeypot/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── src/
    └── scythe_honeypot/
        ├── __init__.py
        ├── __main__.py              # Point d'entrée (python -m scythe_honeypot)
        ├── app.py                   # Application Textual principale
        ├── styles.tcss              # CSS centralisé (tout le theming)
        ├── ascii_art.py             # Logo SCYTHE
        ├── core/                    # Logique métier
        │   ├── canary.py            # Modèle Pydantic du canary
        │   ├── canary_factory.py    # Génération de contenu réaliste
        │   ├── canary_service.py    # Orchestration (deploy, delete, etc.)
        │   ├── event.py             # Modèle TriggerEvent
        │   └── monitor.py           # Surveillance via watchdog + psutil
        ├── storage/
        │   └── database.py          # Wrapper SQLite (canaries + events)
        ├── widgets/                 # Composants UI réutilisables
        │   ├── header.py            # Barre du haut
        │   ├── footer.py            # Barre du bas avec shortcuts
        │   ├── stats_panel.py       # Quick Stats
        │   ├── last_alert.py        # Dernière alerte
        │   ├── events_table.py      # Table des événements récents
        │   ├── canaries_list.py     # Liste scrollable de cards
        │   ├── canary_card.py       # Card d'un canary individuel
        │   ├── canary_creator.py    # Formulaire de création
        │   ├── canary_details_modal.py  # Modal "View"
        │   └── confirm_modal.py     # Modal "Delete confirmation"
        └── screens/
            └── home.py              # Vue dashboard principale
```

### Choix techniques

- **Textual** — Framework TUI moderne avec CSS, async, mouse, animations natifs
- **Pydantic** — Validation et sérialisation des modèles de données
- **SQLite** — Persistence locale (bibliothèque standard Python)
- **watchdog** — Surveillance fichier cross-platform
- **psutil** — Identification de processus
- **cryptography** — Génération de bytes aléatoires sécurisés

### Flow d'un trigger

```
┌─ Thread watchdog ─┐                ┌─ Thread UI Textual ─┐
│                   │                │                     │
│ FileModifiedEvent │                │   _refresh_dashboard│
│        │          │                │           ▲         │
│        ▼          │                │           │         │
│ CanaryEventHandler│                │  notify("triggered")│
│        │          │                │           ▲         │
│        ▼          │                │           │         │
│ on_trigger callback ───call_from_thread───►  _handle_trigger_on_ui
│                   │                │           │         │
└───────────────────┘                │           ▼         │
                                     │ db.record_trigger() │
                                     │                     │
                                     └─────────────────────┘
```

Le thread `watchdog` détecte les events filesystem, identifie le processus avec `psutil`, et utilise `call_from_thread()` de Textual pour passer le résultat au thread UI proprement (sans race conditions).

---

## ⚙️ Configuration

### Emplacement de la base de données

Par défaut, Scythe Honeypot stocke ses données dans :

```
%USERPROFILE%\.scythe-honeypot\canaries.db
```

Soit typiquement : `C:\Users\<TonUser>\.scythe-honeypot\canaries.db`

C'est là que tu trouveras tous les canaries enregistrés et l'historique des événements.

### Variables et thème

Tout le styling visuel est dans `src/scythe_honeypot/styles.tcss`. Si tu veux changer la palette de couleurs, modifie les variables en haut du fichier :

```css
$scythe-green: #00DC82;     /* couleur d'accent principale */
$scythe-green-dim: #00A862; /* variante atténuée */
$amber: #F59E0B;            /* warnings, triggered canaries */
$red: #EF4444;              /* erreurs, suppressions */
$cyan: #06B6D4;             /* infos, métadonnées */
$bg-primary: #0A0A0A;       /* fond principal */
$bg-secondary: #141414;     /* fond des panels */
```

### Mode développement (hot reload du CSS)

Pour développer avec rechargement à chaud :

```powershell
textual run --dev scythe_honeypot.app:ScytheHoneypotApp
```

Modifie `styles.tcss`, sauvegarde, et l'app se met à jour en live.

Pour avoir la console de debug en parallèle :

```powershell
# Terminal 1
textual console

# Terminal 2
textual run --dev scythe_honeypot.app:ScytheHoneypotApp
```

---

## 🔧 Dépannage

### `ModuleNotFoundError: No module named 'scythe_honeypot'`

Tu n'as pas installé le package en mode éditable. Lance :

```powershell
pip install -e .
```

### `pip install` échoue avec une erreur SSL ou réseau

Vérifie ta connexion, ou utilise un mirror :

```powershell
pip install -r requirements.txt --index-url https://pypi.org/simple/
```

### Les caractères Unicode (bordures, icônes) s'affichent comme `▒▒▒`

Ta console n'est pas en UTF-8. Le code force déjà la codepage UTF-8 au démarrage, mais si ça persiste :

- Utilise **Windows Terminal** (gratuit sur le Microsoft Store) au lieu de cmd.exe classique
- Ou lance manuellement : `chcp 65001` avant de lancer l'app

### Aucune notification quand je modifie un canary

Vérifications dans l'ordre :
1. Le canary est-il bien en statut **● ARMED** (pas DISARMED) ?
2. L'option **Modify** est-elle cochée dans la création du canary ?
3. Le fichier est-il bien à l'endroit indiqué ? Va le voir dans l'explorateur Windows.
4. Est-ce que ton antivirus bloque watchdog ? Mets une exception sur le dossier Scythe.

### Le processus n'est pas identifié (`—` à la place du nom)

`psutil` doit attraper le processus **pendant** qu'il a le fichier ouvert. C'est best-effort :
- Pour des éditeurs qui gardent le fichier ouvert (VS Code, Notepad++) → ça marche bien
- Pour des reads ultra-rapides (cat, type) → souvent le processus a déjà fermé le handle quand on regarde

C'est une limitation connue qu'on pourra améliorer avec ETW ou une API Windows plus bas niveau dans une prochaine version.

### `Address already in use` ou erreur DB locked

L'app est déjà lancée dans une autre fenêtre. Ferme l'autre instance.

---

## 🗺️ Roadmap

### Implémenté ✅

- [x] Dashboard TUI complet avec palette Scythe
- [x] Création de canaries avec 6 types de fichiers réalistes
- [x] Persistence SQLite (canaries + events)
- [x] Surveillance temps réel avec watchdog
- [x] Identification de processus avec psutil
- [x] Notifications toast
- [x] Pause / Resume / Delete des canaries
- [x] Modal de détails et de confirmation

### Prévu 🚧

- [ ] **Auto-start au démarrage de Windows** (registry / Task Scheduler)
- [ ] **Capture de l'arbre des processus parents** (PPID + grand-parent + ...)
- [ ] **Webhooks Discord / Telegram** pour alertes à distance
- [ ] **Détection des READ sur Windows** via `ReadDirectoryChangesW` natif
- [ ] **Screen Logs séparé** avec filtres par canary, event type, période
- [ ] **Export rapport** (Markdown / JSON / CSV)
- [ ] **Mode Decoy Folder** — dossier piégé entier au lieu d'un fichier
- [ ] **Templates de canaries** — déployer 5+ canaries en 1 clic
- [ ] **Settings screen** — préférences notifications, hotkeys, stealth
- [ ] **Stats graphiques** avec sparklines (events par jour, top processes)
- [ ] **Mode stealth** — process renommé pour passer inaperçu
- [ ] **Intégration Scythe Messaging** — alertes via canal P2P chiffré

---

## 🌿 La suite Scythe

Scythe Honeypot fait partie d'un **écosystème d'outils OPSEC** :

| Projet | Description | Statut |
|---|---|---|
| **Scythe Messaging** | Messagerie P2P avec Diffie-Hellman et serveur TURN | Existant |
| **Scythe Cord** | Plugin Discord avec chiffrement et stéganographie | Existant |
| **Scythe Honeypot** | Détection d'intrusion personnelle (ce projet) | Actif |
| **Scythe Locate** | Outil GEOINT / OSINT d'analyse d'images | À venir |

Tous les outils Scythe partagent une **philosophie commune** :
- Privilégier la sécurité de l'utilisateur
- Tourner en local (pas de cloud, pas de télémétrie)
- UX moderne et soignée
- Open source

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voilà comment procéder :

1. **Fork** le projet
2. Crée une branche pour ta feature : `git checkout -b feature/amazing-feature`
3. Commit tes changements : `git commit -m 'Add amazing feature'`
4. Push sur ta branche : `git push origin feature/amazing-feature`
5. Ouvre une **Pull Request**

### Pour signaler un bug

Ouvre une issue avec :
- Une description claire du problème
- Les étapes pour reproduire
- Ta version de Python (`python --version`)
- Ta version de Windows
- Le traceback complet si applicable

### Idées de contribution faciles

- Améliorer la liste de signatures réalistes pour les types existants
- Ajouter de nouveaux types de canaries (clés API, certificats, .env files)
- Internationalisation (anglais, espagnol, etc.)
- Tests unitaires
- Documentation

---

## 📜 Licence

Ce projet est sous licence **MIT** — voir le fichier [LICENSE](LICENSE) pour les détails.

```
MIT License

Copyright (c) 2026 KronoxDev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 💬 Contact & Crédits

**Auteur** : Seïka

---

<div align="center">

**Laisse une ⭐ bg**

*Made with 💚 for security-conscious users*

```
↪ Scythe — Tools for those who watch the watchers
```

</div>
