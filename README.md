\# 4a-isi-projet-back — Pol-eat-heck



API back-end de l'application \*\*Pol-eat-heck\*\* : menus à la semaine et système de réservation.

Développée en \*\*Python / FastAPI\*\*, avec une base \*\*SQLite\*\*.



\## Collaborateurs

\- Meina EL Khattat — Base de données

\- Nour EL Houda Bouslimi — Back-end

\- Jude HOUANSOU — Front-end



\## Projets liés

\- Base de données : https://github.com/Nour-Bouslimi/4a-isi-projet-db

\- Front-end : https://github.com/Nour-Bouslimi/4a-isi-projet-front



\## Installation (Windows, cmd)

```cmd

git clone https://github.com/Nour-Bouslimi/4a-isi-projet-back.git

cd 4a-isi-projet-back

python -m venv .venv

.venv\\Scripts\\activate.bat

pip install -r requirements.txt

```



\## Lancer le serveur

```cmd

fastapi dev app/main.py

```

\- API : http://127.0.0.1:8000/api/

\- Documentation interactive (Swagger) : http://127.0.0.1:8000/docs



\## Dépendances

| Paquet | Rôle |

|---|---|

| `fastapi\[standard]` | Framework web, serveur uvicorn, doc `/docs` |

| `sqlmodel` | ORM : classes Python ↔ tables SQLite |

| `pyjwt` | Tokens d'authentification JWT |

| `pwdlib\[argon2]` | Hachage des mots de passe |

| `pytest` | Tests automatiques |



\## Conception



\### Architecture

```mermaid

flowchart LR

&#x20; F\[Front<br/>HTML/CSS/JS] -- "fetch JSON" --> A\[API FastAPI<br/>/api/\*]

&#x20; A --> DB\[(SQLite)]

```



\### Structure du projet

```

4a-isi-projet-back/

├── app/

│   ├── main.py        # point d'entrée : création de l'app FastAPI

│   └── routers/       # routes par ressource 

├── requirements.txt

└── README.md

```





