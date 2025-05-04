# 🛠️ app_order

Sistema web de Ordens de Serviço (OS) com autenticação, controle de status e envio de imagem na conclusão da OS.

## 🔑 Funcionalidades

- Registro e login de usuários
- Perfis: Funcionário e Administrador
- Solicitação, acompanhamento e conclusão de OS
- Envio obrigatório de foto e comentário na finalização
- Painéis separados por perfil com permissões específicas

## 📚 Tecnologias

- Django 5.2
- Python 3.11
- Bootstrap 5
- PostgreSQL
- Docker
- Pillow (upload de imagem)

---

> 🧪 **Status:** developing...

---

# Passo a passo: 

- Abra o diretorio na pasta raiz "APP"

- Contruir e inicar os containers: `docker-compose up --build` 
- Ou se preferir rodar em segundo plano: `docker-compose up -d --build`
- Verifique os containers em execução: `docker-compose ps`
- Após confirmar execução, acesse a aplicação na porta 8000: http://localhost:8000
- Crie seu superusuario para ter acesso: `docker-compose exec web python manage.py createsuperuser`