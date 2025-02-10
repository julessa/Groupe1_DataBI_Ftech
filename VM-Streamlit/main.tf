provider "aws" {
  region = "us-east-1"  # Adaptez la région si nécessaire
}

resource "aws_security_group" "streamlit_sg" {
  name        = "streamlit_sg"
  description = "Autoriser le trafic SSH et le port 8501 pour Streamlit"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Streamlit (par défaut sur le port 8501)"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "streamlit_instance" {
  ami           = "ami-04a4acda26ca36de0"  # Remplacez par l'AMI Ubuntu adaptée à votre région (par exemple, Ubuntu 20.04 LTS)
  instance_type = "t2.micro"
  key_name      = var.key_name

  # Injection du script de démarrage
  user_data = file("user_data.sh")

  vpc_security_group_ids = [aws_security_group.streamlit_sg.id]

  tags = {
    Name = "StreamlitApp"
  }
}

variable "key_name" {
  description = "Nom de la clé SSH à utiliser pour l'instance"
  type        = string
}
