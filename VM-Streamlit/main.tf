provider "aws" {
  region = "eu-west-3"
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
    description = "Streamlit (par defaut sur le port 8501)"
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
  ami           = "ami-04a4acda26ca36de0" 
  instance_type = "t2.micro"
  key_name      = var.key_name

  # Injection du script de démarrage (user_data.sh)
  user_data = file("user_data.sh")

  vpc_security_group_ids = [aws_security_group.streamlit_sg.id]

  tags = {
    Name = "StreamlitApp"
  }
}

variable "key_name" {
  description = "Nom de la clé SSH à utiliser pour l'instance"
  type        = string
  default     = "my_key"  # Remplacez "my_key" par le nom de votre key pair
}

output "instance_public_ip" {
  description = "Adresse IP publique de l'instance"
  value       = format("IPNET : http://%s:8501/", aws_instance.streamlit_instance.public_ip)
}
