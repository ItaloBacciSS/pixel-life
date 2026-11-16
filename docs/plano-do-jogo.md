# Pixel Life — Plano (v4)

Jogo idle no navegador onde o personagem é o próprio jogador. A evolução vem da vida real: o jogador registra o que fez no dia e o personagem reflete isso. O jogo continua "rodando" enquanto o jogador está fora (decaimento, sequências). É um jogo para a vida toda: progressão lenta, sem limite.

## Decisões tomadas

- **Plataforma:** web, acessível de vários aparelhos. Python (Flask) no servidor, HTML/CSS nas telas e um pouco de JavaScript (arquivos separados).
- **Visual:** pixel art arcade (decidido). Personagem grande num quarto em pixel art, fonte pixel (Press Start 2P, guardada no projeto), bordas grossas, sombras duras, barras de XP em blocos. Efeitos: texto flutuante "+XP", faíscas e brilho ao registrar, personagem pula, treme num tropeço, confete e aviso "LEVEL UP!" ao subir de nível, com sons curtos (botão liga/desliga no quarto). Tudo respeita `prefers-reduced-motion`.
- **Entrada de dados:** registro manual.
- **Dados:** banco de dados com login por usuário e senha (SQLite no PC, Postgres na nuvem). **Publicado**: Vercel (região gru1) + Neon Postgres em São Paulo, sincronizando entre aparelhos. Repositório público no GitHub (portfólio); deploy automático a cada push.
- **Calendário externo (Google etc.):** fase futura. Não é necessário para detectar dia sem registro — o próprio jogo sabe quais dias estão vazios.

## Registro

- Botões rápidos para ações comuns.
- Botão "+ nova ação": o jogador cria uma ação uma vez (nome, atributo(s), intensidade leve/média/pesada) e ela vira botão salvo.
- Campo de texto opcional como anotação em cada registro (diário). Não é interpretado pelo jogo por enquanto. Ideia futura: IA interpretar o texto.
- O jogador pode registrar dias passados, para esquecer de abrir o jogo não custar caro.
- Cada botão conta no máximo uma vez por dia (evita ganhar nível clicando várias vezes).

## Atributos (9)

| Área | Atributo | Decai? |
|---|---|---|
| Físico | Força | Sim, devagar |
| Físico | Vitalidade | Sim, mais rápido que os outros |
| Mente | Intelecto | Não |
| Mente | Foco | Sim |
| Trabalho/finanças | Carreira | Não (só perde por ação negativa) |
| Trabalho/finanças | Riqueza | Não (por enquanto) |
| Social/emocional | Carisma | Sim, bem devagar |
| Social/emocional | Equilíbrio | Sim |
| Espiritual | Fé | Sim, devagar |

Cada atributo tem nível e barra de XP. Uma ação pode dar XP em mais de um atributo. Existe também um nível geral do personagem. A lista de atributos pode crescer depois.

## Níveis

- Todos os atributos começam no nível 0 ("nascendo de novo").
- Sem 100% e sem nível máximo: o nível sobe para sempre; a interface mostra só a barra até o próximo nível.
- Custo para ir do nível *n* para o *n+1*: **100 + 20 × n** de XP (1→2 custa 120, 9→10 custa 280, 49→50 custa 1.080).
- Referência: ação média = 10 XP, cerca de 1.500 XP por ano em um atributo → nível 10 em ~1 ano, nível 20 em ~4 anos, nível 50 em ~20 anos.
- Escala de XP: leve 5, média 10, pesada 20.
- Decaimento e tropeços tiram XP só da barra atual; o nível nunca cai. O nível é a história, a barra é o momento.

## Perdas

- **Decaimento (passivo):** acontece com o tempo parado. Só começa depois da carência (dias sem ação positiva no atributo) e come só a barra atual (piso = 0 da barra). Nunca é aplicado no dia de hoje.
  Valores (carência / perda por dia): Vitalidade 2 / −4, Foco 3 / −3, Equilíbrio 3 / −3, Fé 4 / −2, Força 7 / −3, Carisma 14 / −1. Intelecto, Carreira e Riqueza não decaem.
- **Ações negativas (ativas):** botões para registrar tropeços. Os nomes são definidos pelo jogador.
  - Um tropeço tira menos do que uma ação boa dá, exceto na **Fé**, onde o impacto deve ser perceptível.
  - Uma ação negativa pode afetar mais de um atributo.
  - Recuperação: depois de um tropeço, a próxima ação certa do mesmo atributo rende um pouco mais de XP por um tempo.
- **Privacidade:** os dados ficam na conta do jogador, no banco; ninguém além dele vê o registro de tropeços na interface. A página `/privacidade` explica o que é guardado (a Fé é dado sensível e está citada lá). Falta incluir um contato na página.

## Contadores

- Dias sem tropeçar (geral): zera com qualquer tropeço.
- Dias sem tropeçar na Fé: zera só com tropeços de Fé.
- Guardar o recorde de cada um.

## Dia sem registro

- Conta como dia parado e alimenta o decaimento, mas o jogador pode registrar o dia depois para corrigir.

## Botões iniciais (XP sugerido, a ajustar jogando)

**Força:** Treino de academia (10), Treino longo ou pesado (20), Alongamento (5).
**Vitalidade:** Dormi bem (10), Bebi água suficiente (5), Comi bem o dia todo (10), Caminhada (5), Cardio (10).
**Intelecto:** Estudei 1h (10), Li por 30 min (5), Aula ou curso (10).
**Foco:** Sessão de foco sem celular (10), Cumpri a lista de tarefas do dia (10), Dia sem redes sociais (10).
**Carreira:** Entrega concluída (15), Avanço em projeto (10), Contato profissional relevante (5).
**Riqueza:** Poupei dinheiro (10), Dia sem gasto supérfluo (5), Revisei as finanças (10).
**Carisma:** Tempo com a família (10), Tempo com amigos (10), Falei com alguém distante (5), Ajudei alguém (5).
**Equilíbrio:** Meditação (5), Hobby (10), Descanso de qualidade (5), Tempo ao ar livre (5).
**Fé:** Leitura da Bíblia (10), Oração (5), Reunião (15), Pregação (20), Adoração em família (10), Preparação para a reunião (5).

**Negativos:** Sair da dieta (Força −5, Vitalidade −3), Dormir pouco (Vitalidade −8, Foco −3), Não entregar algo (Carreira −10), Gasto impulsivo (Riqueza −8), Procrastinação (Foco −8), Briga ou mágoa (Carisma −5, Equilíbrio −3), Tropeço na Fé (Fé −25).

## Estado do protótipo (v1)

Pronto e testado (48 testes automáticos + conferência no navegador, desktop e celular):

- Login e conta (senha com hash), com opção de fechar o cadastro depois de criar a conta (`REGISTRATION_OPEN=0`).
- Regras num único arquivo (`app/data/rules.json`): atributos, XP dos botões, tropeços, decaimento e cores.
- Estado do personagem sempre derivado do histórico de registros (registrar dia passado ou ajustar números recalcula tudo).
- API: estado, registrar, desfazer, criar ação personalizada. Um registro por botão por dia, sem dias futuros.
- Tela: personagem em pixel art (SVG), 9 atributos com nível e barra, botões positivos e tropeços, navegação entre dias, "+ Nova ação", contadores de dias sem tropeçar (geral e Fé) com recorde, aviso de subida de nível.
- Fuso do jogador configurável (`TIMEZONE`, padrão America/Sao_Paulo), porque o servidor na nuvem roda em UTC.

Estrutura: `app/` (config, models, routes, services, data), `templates/`, `static/` (css, js, img), `tests/`, `docs/`.

## Personagem, itens e perfil (pronto)

- Ao criar a conta, o jogador cai na criação do personagem: corpo (masculino ou feminino), cor da pele, do cabelo e da roupa, **3 penteados e 3 modelos de roupa por corpo** (todos liberados). Dá para mudar tudo depois na página Personagem.
- A página Personagem usa **setinhas** (`<` `>`) ao lado da prévia: coluna da esquerda com o básico (corpo, pele, penteado, cor do cabelo, modelo e cor da roupa) e coluna da direita com os itens por posição (cabeça, rosto, roupa, costas, peito, pulso, mão, pés). Itens bloqueados aparecem nas setinhas com o requisito. Salvar fica no cartão da prévia.
- O personagem é desenhado no servidor por camadas (`app/data/sprites.json`, renderizador em `app/services/sprites.py`), então as cores e os itens valem em qualquer aparelho.
- 13 itens com desenho nos dois corpos, cada um com seu requisito em `rules.json`: Regata (Força 3), Faixa (Força 10), Tênis (Vitalidade 3), Óculos (Intelecto 3), Livro (Intelecto 10), Fone (Foco 5), Roupa social (Carreira 3), Relógio (Riqueza 5), Jaqueta (Carisma 5), Bíblia (Fé 5), Medalha (7 dias sem tropeçar), Capa (30 dias sem tropeçar), Coroa (nível geral 10).
- Itens bloqueados aparecem em cinza com o requisito e o progresso (ex.: "Força nível 10 (3/10)"). Dá para provar um bloqueado na pré-visualização, mas ele não é salvo. Se um item equipado voltar a bloquear (nível caiu ao desfazer registros), ele sai sozinho.
- Menu no topo (Jogo, Personagem, Perfil, Sair). Perfil: ver conta, trocar senha (pede a atual) e excluir perfil (pede a senha e uma confirmação; apaga conta, registros, ações criadas e personagem).
- Observação de regra: "dias sem tropeçar" conta desde o primeiro registro, mesmo sem fazer outras ações. Se o jogador preferir exigir atividade, é preciso mudar a regra da sequência.

## Conquistas, mascote e quarto (pronto)

- 22 conquistas em `rules.json` (registros, dias de jogo, dias sem tropeçar, ações por atributo, nível de atributo, todos os atributos no nível 3, nível geral). Aparecem na página Progresso (bloqueadas mostram o progresso) e as 4 mais recentes ficam na estante do quarto. Ao ganhar uma, aparece o aviso "CONQUISTA!" com confete.
- As conquistas são calculadas a partir do histórico, como o nível. Se o jogador desfaz um registro e perde o requisito, a conquista some; ao refazer, ela é ganha de novo.
- Mascote (gato ou cachorro): feliz com 3 ou mais ações boas no dia, triste depois de 3 dias parado, normal no resto. Ele só faz pequenos movimentos no lugar (respira, pisca, saltita), sem andar pelo quarto. A **fala sai do personagem**, num balão ao lado da cabeça.
- Falas em `rules.json` (`mascote`): por humor (normal 10, feliz 10, triste 8), por período do dia (madrugada, manhã, tarde, noite) e para sequências (a partir de 3 dias). Escolhidas ao acaso a cada atualização, sem repetir a última; máximo de 40 caracteres cada (teste garante).
- Quarto que evolui: cada atributo que chega ao nível 2 coloca um objeto no quarto (halter, livros, garrafa, relógio, quadro, diploma, Bíblia, cofrinho, planta). Desenhos em `app/data/quarto.json`; um teste garante que nada se sobrepõe nem cobre o personagem.

## Quarto e mascote personalizáveis (pronto)

- Página Quarto: 6 temas de quarto (Clássico, Céu, Algodão-doce, Jardim, Cabana, Noite) e mascote gato ou cachorro, cada um com 5 cores de pelo. Tudo liberado desde o início, sem conquistar nada. Dá para ver o mascote nos três humores antes de salvar.
- Os temas trocam as cores do cenário (`static/img/cenario.svg`) segundo `app/data/quarto.json`; o mascote e as cores também ficam nesse arquivo. A escolha fica na tabela `Home`; quem não escolheu usa Clássico, gato laranja.
- Criação da conta: depois de cadastrar, o jogador cai só na montagem do personagem (corpo, pele, cabelo e roupa), sem menu e sem a lista de itens. Quarto e mascote ficam para a página Quarto.

## Cenário vivo (pronto)

- O quarto ganha uma janela que mostra o céu conforme a hora do jogador (madrugada, amanhecer, dia, entardecer, noite) e o clima conforme o humor do mascote (feliz = sol, normal = nuvens, triste = chuva). O ambiente escurece e esquenta de acordo com a hora.
- Para testar: `?hora=10&clima=sol` na URL do jogo.
- Personagem pisca; mascote respira e saltita; tudo desligado para quem prefere menos movimento.

## Publicação e contas (pronto)

- **Hospedagem:** Vercel (Flask na raiz via `index.py`, `vercel.json` com `gru1`) e Neon Postgres em sa-east-1. Variáveis: `SECRET_KEY` (obrigatória na Vercel), `TIMEZONE`, `DATABASE_URL` e `REGISTRATION_OPEN` (opcional).
- **Desempenho:** a região padrão (iad1) com o banco em São Paulo fazia cada clique levar ~4 s (~15 consultas × ~114 ms). Com a função em gru1, uma consulta leva ~5 ms. A página `/saude` mostra região e tempo de consulta.
- **Cadastro público** com nome de usuário único (`[A-Za-z0-9_.-]`, 3 a 40, sem diferenciar maiúsculas), senha de 8 a 128 caracteres que não pode ser comum nem igual ao usuário, e aceite da política de privacidade.
- **Código de recuperação:** 16 caracteres, mostrado uma vez, guardado só em hash, trocado a cada uso; dá para gerar outro no Perfil (pede a senha).
- **Limites de tentativa:** por usuário (5 em 15 min), por origem (20) e de cadastros (5 por hora), guardados no banco.
- **Cabeçalhos e requisições:** CSP restrita, X-Frame-Options, nosniff, Referrer-Policy, Permissions-Policy, HSTS na Vercel, e bloqueio (403) de requisições de outro site que alteram dados. Cookie seguro na Vercel; corpo de requisição limitado a 64 KB.
- **Banco:** `create_all` mais uma migração simples que só adiciona colunas novas (`app/migrations.py`).
- **Cache:** arquivos estáticos são revalidados (ETag/304) para um deploy novo nunca deixar JavaScript velho no navegador.
- Hipótese ainda não confirmada: o limite por origem depende de a Vercel enviar o IP real em `X-Real-IP`/`X-Forwarded-For`.
- 304 testes automáticos passando.

## Progresso, metas e riqueza (pronto)

- **Progresso:** resumo da semana (segunda a domingo: ações, tropeços, metas, dias sem tropeçar, melhor dia, XP por atributo, o que subiu de nível), gráfico de evolução do nível geral ou de cada atributo (um ponto por semana) e a galeria de conquistas.
- **Metas:** metas semanais do tipo "fazer tal ação N vezes por semana" (1 a 7, até 20 metas). Aparecem no jogo com barra de progresso e avisam "META CUMPRIDA!".
- **Riqueza com valor real:** saldo em reais guardado em centavos. O jogador registra entradas e saídas, pode acertar o saldo (o jogo registra a diferença), vê o gráfico e o histórico. O saldo aparece no cartão de Riqueza. O saldo é independente do XP: o XP de Riqueza continua vindo dos botões (Poupei dinheiro etc.).

## Próximos passos

1. **Estilo e cores** (etapa 4 do pacote visual, ainda não feita): paleta, contraste e acabamento.
2. App instalável no celular (PWA).
3. Sessão mais longa ("lembrar de mim") e encerrar as outras sessões ao trocar a senha.
4. Ajustar os números (XP, decaimento, requisitos das conquistas) jogando.
5. Decidir se o saldo deve dar XP de Riqueza automaticamente.
6. Contato na página de privacidade e conferir o IP de origem na Vercel.
7. Missões do dia: o jogador decidiu não fazer por enquanto.

## Pendente

- Riqueza com valores reais: atualização de saldo periódica, XP proporcional à renda (segunda versão).
- Personagem mudando de aparência conforme evolui.
- Calendário externo (fase futura).
