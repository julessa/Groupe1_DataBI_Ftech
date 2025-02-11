# Guide d'installation et de lancement de l'instance AWS avec Terraform

Ce document vous guide pas à pas pour créer votre compte AWS, configurer votre environnement, et déployer une instance EC2 qui héberge votre application Streamlit grâce à Terraform. Vous n'avez besoin d'aucun code supplémentaire : suivez simplement les instructions ci-dessous.

---

## 1. Créer un compte AWS

1. Rendez-vous sur [aws.amazon.com](https://aws.amazon.com/) et inscrivez-vous pour obtenir un compte (profitez de l'offre gratuite si vous êtes éligible).
2. Une fois le compte créé, connectez-vous à la [console AWS](https://console.aws.amazon.com/).

---

## 2. Installer Terraform

1. Téléchargez et installez Terraform depuis le [site officiel](https://www.terraform.io/downloads.html).
2. Vérifiez l'installation en ouvrant un terminal et en tapant :
   ```bash
   terraform version
