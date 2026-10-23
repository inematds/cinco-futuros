# Plano: cinco-futuros

Este é um kit que você copia para a sua pasta. Nela, o seu agente (Claude Code ou Codex) faz três coisas:

1. Monta a sua agenda de preparação para os 5 futuros da IA.
2. Acompanha toda semana os sinais de qual futuro está chegando mais perto.
3. Reorganiza a agenda quando um sinal passa do limite.

Ele nasceu da série de vídeos "5 futuros da IA" (playlist no lives11: https://www.youtube.com/playlist?list=PLGR_G3hBAAaM). O mapa vem do Life 3.0, de Max Tegmark, adaptado, com o cenário AI 2027.

## Os 5 cenários
| # | Cenário | Pergunta que ele faz para você |
|---|---|---|
| 1 | Extinção total | se der muito errado, você e sua família aguentam o choque? |
| 2 | Zoológico humano | o que você ainda sabe fazer sem a IA? |
| 3 | Governo mundial da IA | quanto da sua vida depende de regras que você não controla? |
| 4 | Paraíso feito pela IA | se o emprego sumir, o que sustenta a sua renda e o seu propósito? |
| 5 | Utopia verdadeira | você está aprendendo a trabalhar junto com a IA? |

Ninguém sabe qual vai acontecer. Por isso o kit separa as ações em dois tipos:

- **Ações robustas:** valem em vários futuros ao mesmo tempo (reserva, saúde, habilidades próprias, comunidade, saber usar a IA). Elas sempre entram na agenda.
- **Ações específicas:** ganham peso quando os sinais apontam para um futuro.

Esse é o método clássico de planejamento de cenários da Shell: cada cenário tem indicadores de alerta precoce, chamados signposts.

## Como funciona
```
copiar kit/ → "agente, faz meu diagnóstico" → perfil.md
            → agenda.md (90 dias: robustas + específicas do seu perfil)
toda semana → coletor (script, sem IA, sem chave) baixa os dados → sinais.md
            → agente lê, atualiza o termômetro dos 5 futuros, avisa se algum sinal passou do limite,
              e reprioriza a agenda → diario.md
todo mês    → revisão: o que você fez, o que mudou no mundo, o próximo foco
```

## Estrutura do kit (o que a pessoa copia)
```
kit/
  AGENTS.md            regras do agente (Codex) — CLAUDE.md aponta para ele
  CLAUDE.md
  .claude/skills/
    diagnostico/       entrevista curta → perfil.md + exposição por cenário
    agenda/            gera/atualiza agenda.md (robustas + específicas)
    sinais/            roda o coletor, interpreta, atualiza termometro.md, alerta
    revisao/           revisão semanal e mensal → diario.md
  cenarios/1..5.md     o que é, como se vive, sinais (métrica + fonte + limiar), ações
  coletor/coleta.py    baixa dados públicos (Python puro, sem chave, sem API paga)
  estado/              perfil.md · agenda.md · sinais.md · termometro.md · diario.md
  agendar.md           como ligar o semanal: /loop, tarefa do app, ou cron + `claude -p` / `codex exec`
```

## Fontes de sinais (1ª rodada, conferir cada uma antes de usar)
| Fonte | O que mede | Acesso | Status |
|---|---|---|---|
| Epoch AI `all_ai_models.csv` | compute de treino, modelos, organizações | CSV aberto, CC BY 4.0 | testado 23/10: 3.628 linhas |
| Epoch `data_centers.csv`, `gpu_clusters.csv` | concentração de compute | CSV aberto | a testar |
| METR horizonte de tarefas | quanto tempo de trabalho o agente faz sozinho | "raw data" + GitHub | formato/licença a confirmar |
| AI Incident Database | incidentes de IA | snapshots semanais (~100 MB) | a testar |
| Anthropic Economic Index | uso de IA por ocupação | Hugging Face, CC BY 4.0 | a testar |
| Stanford Digital Economy Lab ("canários") | emprego de jovens em funções expostas | PDF/página | leitura manual |
| AI Index Stanford | capacidade, adoção, incidentes | relatório anual | leitura manual |
| EU AI Act / lei brasileira de IA | regulação | páginas oficiais | leitura manual |
| IBGE / CAGED | emprego no Brasil por ocupação | a pesquisar | lacuna |
| Manifold / Metaculus | previsões da comunidade | **API**: precisa de autorização do Nei (Metaculus pede token) | não usar sem OK |

## Reaproveita o sobreviver-ia
O repo `sobreviver-ia` já tem o kit de 14 dias, a IA e a Wikipedia offline, a auditoria de contas com SMS, o eval pessoal e o plano de 90 dias. O cinco-futuros aponta para essas ferramentas nas ações robustas e não copia nenhuma delas.

## Fases
1. ✅ (23/10, 1ª versão) **Cenários com sinais medidos:** `cenarios/*.md`, cada sinal com métrica, fonte, limiar e nível de confiança. Feito quando todo sinal tem fonte ou está marcado como "proposta".
2. **Coletor:** `coleta.py` gera `sinais.md`. Feito quando os testes rodam com fixtures e há uma coleta real que dá certo.
3. **Skills + agenda:** as skills diagnóstico, agenda, sinais e revisão. Feito quando uma pessoa de teste roda do zero e sai com perfil, agenda e termômetro.
4. **Guia PT/EN/ES + portal + vídeo**, no padrão INEMA.

## Regras
- Cenário é hipótese, não previsão. Todo número leva fonte, e o que não tem fonte vai marcado como "não confirmado".
- O kit não dá conselho financeiro. Ele mostra opções e riscos.
- Nada de API paga ou com chave. O agente é o que a pessoa já assina.
- Tom r7exp: a emoção primeiro e a verdade confirmando. A agenda fala com "você".

## Perguntas abertas
- Manifold e Metaculus são API: usamos ou não?
- Público: pessoa física só, ou também uma versão para empresa e equipe?
- O alerta vai para onde: só `diario.md`, ou também Telegram ou e-mail da pessoa?
