# vtherm_climate_replication

Squelette initial d'une integration Home Assistant destinee a servir de plugin pour Versatile Thermostat.

## Structure

- `custom_components/vtherm_climate_replication/` : composant Home Assistant.
- `.devcontainer/` : environnement VS Code reproducible en Python 3.14.
- `tests/` : validations de base du squelette.

## Devcontainer

Le devcontainer utilise l'image officielle Dev Containers Python 3.14.

Le travail se fait directement avec le Python du conteneur. Aucun environnement virtuel n'est cree ni attendu dans ce depot.

Les dependances Python sont decrites dans `requirements.txt` et `requirements-dev.txt`. Elles sont reinstallees automatiquement a la creation puis a chaque demarrage du devcontainer.

Une fois le depot ouvert dans VS Code, lancer "Reopen in Container" pour travailler directement dans l'environnement configure.

## Lancer Home Assistant en local

Une configuration minimale Home Assistant est fournie dans `.homeassistant/configuration.yaml`.

Le bootstrap du devcontainer recree automatiquement `.homeassistant` et le lien vers `custom_components` a chaque creation et a chaque redemarrage du conteneur.

Dans VS Code, ouvrir la palette de commandes puis lancer `Tasks: Run Task`, et choisir `Home Assistant: Run local`.

La tache :
- utilise la configuration locale `.homeassistant`
- relie `custom_components` dans ce dossier pour charger l'integration du depot
- demarre Home Assistant avec le Python du devcontainer