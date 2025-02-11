# Guide d'installation et de déploiement avec Terraform

Ce guide vous permettra de configurer vos identifiants AWS, d'initialiser et d'exécuter votre infrastructure avec Terraform, et d'accéder à votre application Streamlit.

## 1. Configuration de l'environnement
# Obtenir vos identifiants AWS

Pour générer ou récupérer votre AWS Access Key et AWS Secret Access Key, suivez ces étapes :

1. Connectez-vous à la Console de gestion AWS.
2. Accédez à la section IAM (Identity and Access Management).
3. Sélectionnez "Utilisateurs" dans le menu de gauche.
4. Choisissez l’utilisateur concerné ou créez un nouvel utilisateur.
5. Rendez-vous dans l’onglet "Sécurité" ou "Security credentials".
6. Si aucune paire d’accès n’existe, cliquez sur "Créer une nouvelle clé d’accès".
7. Copiez ou téléchargez vos identifiants et conservez-les dans un endroit sécurisé.

Ces clés seront utilisées pour configurer votre environnement AWS et permettre à Terraform d’interagir avec vos ressources.

### a. Ajout des commandes dans votre profil de terminal

Pour éviter de saisir ces commandes à chaque démarrage de terminal, ajoutez-les à votre fichier `~/.bash_profile` ou `~/.zshrc` (selon votre shell). Par exemple :

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=eu-west-3
```

Rechargez votre profil en exécutant :

```bash
source ~/.bash_profile  # ou, selon votre shell :
source ~/.zshrc
```

### b. Utilisation d’un fichier de configuration

Vous pouvez également créer un fichier de configuration AWS pour gérer vos identifiants.

Créez ou modifiez le fichier `~/.aws/credentials` :

```
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
```

Ensuite, configurez le fichier `~/.aws/config` :

```
[default]
region = your_preferred_region
output = json
```

## 2. Déployer l’infrastructure avec Terraform

### a. Initialiser Terraform

Ouvrez un terminal dans le dossier contenant votre configuration Terraform, puis exécutez :

```bash
terraform init
```

Cette commande télécharge les plugins nécessaires (providers, etc).

### b. Prévisualiser le plan

Avant d’appliquer les changements, visualisez le plan d’exécution :

```bash
terraform plan
```

Examinez la sortie pour vérifier que Terraform va créer les ressources attendues.

### c. Appliquer le plan

Pour déployer votre infrastructure, lancez :

```bash
terraform apply
```

Tapez `yes` lorsqu’on vous le demande pour confirmer l'exécution du plan.

## 3. Vérifier et accéder à votre instance

Une fois l'infrastructure déployée, Terraform affichera l’IP publique de l’instance. Pour accéder à votre application Streamlit, ouvrez l’URL suivante dans votre navigateur :

```
http://<instance_public_ip>:8501
```

(Remplacez `<instance_public_ip>` par l’adresse affichée par Terraform.)

## 4. Dépannage et ressources supplémentaires

### Vérification de la connexion

Si votre application Streamlit ne répond pas sur le port 8501, vérifiez les points suivants :

- L’instance AWS est en cours d’exécution.
- Le groupe de sécurité (`aws_security_group.streamlit_sg`) autorise le trafic entrant sur le port 8501.
- Vos identifiants AWS et la région sont correctement configurés.

### Documentation utile

- [Documentation Terraform](https://www.terraform.io/docs)
- [Documentation AWS CLI](https://aws.amazon.com/documentation/cli/)

Ce guide vous permet d’installer, configurer et déployer votre infrastructure AWS avec Terraform étape par étape.