# Pixel Life

Jogo web de estilo idle/arcade em pixel art em que **o personagem é você mesmo**. Você registra o que fez no dia (treinar, estudar, orar, guardar dinheiro...) e o personagem evolui de verdade, sem precisar jogar: a vida real é o controle.

> Projeto pessoal, feito para ser simples de ler: Flask + HTML + CSS, com o mínimo de JavaScript.

## O que tem

- **9 atributos** com níveis e XP: Força, Vitalidade, Intelecto, Foco, Carreira, Riqueza, Carisma, Equilíbrio e Fé.
- **Registro diário** de ações (prontas ou criadas por você), com sequências (streaks) e tropeços que pesam na evolução.
- **Personagem customizável** em pixel art, com itens que aparecem conforme você evolui.
- **Quarto e mascote** (gato ou cachorro) personalizáveis; o quarto muda com o seu progresso e o mascote reage ao seu humor.
- **Conquistas**, **metas semanais** e **resumo/evolução** com gráfico.
- **Riqueza real**: controle de saldo em reais com gráfico por dia.
- **Contas com login**, alteração de senha, exclusão de perfil e limite de tentativas de login.

## Stack

- Python 3 e Flask 3 (app factory), Flask-SQLAlchemy.
- SQLite no desenvolvimento e Postgres em produção.
- Front-end com HTML, CSS e módulos ES simples, sem frameworks. Os sprites e o quarto são SVGs gerados no servidor.
- Testes com pytest.

## Como rodar localmente

```bash
python -m venv venv
# Windows: venv\Scripts\activate    |    Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Abra http://127.0.0.1:5000 e crie uma conta.

## Testes

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Estrutura

```
app/
  routes/      rotas (páginas e API), uma por assunto
  services/    regras do jogo (progresso, conquistas, metas, riqueza, quarto...)
  data/        regras e catálogos em JSON (atributos, itens, conquistas, quarto)
  models.py    tabelas
  config.py    configuração por variáveis de ambiente
templates/     páginas HTML
static/        CSS, JS e imagens
tests/         testes automatizados
api/index.py   entrada para o deploy na Vercel
```

## Deploy (Vercel + Neon)

1. Suba o repositório no GitHub e importe o projeto na Vercel (framework: Other).
2. Conecte um banco Postgres da Neon ao projeto (cria a `DATABASE_URL`).
3. Defina as variáveis de ambiente:

| Variável | Para quê |
|---|---|
| `SECRET_KEY` | Chave da sessão (obrigatória na Vercel). |
| `DATABASE_URL` | Conexão com o Postgres. |
| `TIMEZONE` | Fuso do jogador (padrão `America/Sao_Paulo`). |
| `REGISTRATION_OPEN` | `0` fecha o cadastro de novas contas. |

## Licença

Projeto pessoal, sem licença definida.
