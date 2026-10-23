# Pesquisa 1: sinais e preparação por cenário (23/10/2026)

A pesquisa foi feita por um agente pesquisador, só com busca web resumida; a maioria das páginas não foi aberta. Cada item precisa ser conferido na fonte antes de entrar no kit.

## Método
- **Signposts (Shell, "intuitive logics"):** cada cenário traz indicadores de alerta precoce, para você perceber a virada a tempo. Fontes: Aalto, https://ckir.aalto.fi/?p=240 · CMR "Three decades of scenario planning in Shell".
- **Canaries in technology mines (Cremer e Whittlestone, Cambridge/CSER):** marcos de progresso da IA levantados com especialistas, mais um mapa causal para achar os marcos que destravam outros. Fontes: https://www.repository.cam.ac.uk/handle/1810/310700 · https://cser.ac.uk/resources/canaries-technology-mines
- Não existe lista pública de sinais organizada pelos 5 cenários do Tegmark. O mapa abaixo é proposta nossa.

## Fontes de dados
- **Epoch AI:** CSV aberto, CC BY 4.0, atualizado todo dia. Arquivos: https://epoch.ai/data/all_ai_models.csv · data_centers.csv · gpu_clusters.csv. Testado em 23/10: 3.628 modelos.
- **METR horizonte de tarefas:** https://metr.org/horizon-chart-embed. Tem "raw data" e código no GitHub; formato e licença não confirmados.
- **AI 2027:**
  - Tracker de terceiros: https://ai2027-tracker.com/guides/ai-2027-vs-reality/
  - Avaliação feita pelos autores: https://blog.ai-futures.org/p/grading-ai-2027s-2025-predictions. Eles medem o ritmo real em cerca de 65 a 75% do previsto e situam a decolagem entre fim de 2027 e meados de 2029.
- **Manifold:** API de leitura sem chave, https://docs.manifold.markets/api. Precisa de autorização do Nei.
- **Metaculus:** precisa de token, e os termos podem restringir o uso por IA (não verificado).
- **Dashboard que agrega previsões:** https://agi.goodheartlabs.com
- **AI Incident Database:** snapshots semanais em JSON/CSV, https://incidentdatabase.ai/research/snapshots/
- **Anthropic Economic Index:** Hugging Face, CC BY 4.0, https://huggingface.co/datasets/Anthropic/EconomicIndex
- **Stanford AI Index 2026:** relatório anual.
- **Stanford DEL "Canaries in the Coal Mine":** emprego de jovens de 22 a 25 anos em funções expostas à IA. A queda relativa passou de 13% para 16% e depois para 19% nas versões de 2025–2026. O estudo é correlacional.
- **IMD AI Safety Clock:** proprietário, sem dados abertos.
- **EU AI Act / Digital Omnibus:** acordo provisório em 07/05/2026 adia o alto risco do Anexo III para 02/12/2027. Conferir no Official Journal.

## Sinais e ações por cenário (proposta, sem fonte quando não há link)
1. **Extinção**
   - Sinais: incidentes graves com agentes (AIID); engano ou sabotagem em avaliações de segurança; corrida sem freio (a lacuna EUA–China fechou, segundo o AI Index 2026); regras adiadas; salto do horizonte METR.
   - Ações: reserva de caixa, água, remédios e documentos; comunicação offline; comunidade local; saúde; apoiar governança; não paralisar.
2. **Zoológico humano**
   - Sinais: delegação crescente de decisões pessoais à IA; perda de habilidades próprias; plataformas fechadas; dependência de um único provedor.
   - Ações: manter habilidades sem IA; guardar dados em formato aberto; ter modelo local como plano B; cultivar relações reais; revisar o que você não faz mais sozinho.
3. **Governo mundial da IA**
   - Sinais: tratados com poder real sobre compute; licenciamento obrigatório e vigilância; concentração de compute (Epoch); identidade digital obrigatória.
   - Ações: privacidade e segurança digital; participar de consultas públicas; diversificar ativos; conhecer a regulação do seu setor.
4. **Paraíso feito pela IA**
   - Sinais: automação desloca contratações (canários de Stanford); experimentos de renda básica; queda de custo de bens e serviços; uso substitutivo crescendo no Economic Index; debate sobre redistribuição.
   - Ações: cortar dívida e custo fixo; diversificar renda; desenvolver supervisão e julgamento; ter propósito fora do emprego; acompanhar as políticas de transição.
5. **Utopia verdadeira**
   - Sinais: humanos mantêm controle (interpretabilidade, auditoria); ganhos de produtividade distribuídos; melhora em saúde e educação; padrões abertos.
   - Ações: aprender a delegar, revisar e verificar o trabalho da IA; montar portfólio real; participar de comuns abertos; ensinar outras pessoas; cuidar da saúde.

## Kit copiável
- O Claude Code tem skills em `.claude/skills/`. Para rodar no horário certo, há três caminhos ([doc](https://code.claude.com/docs/en/scheduled-tasks)):
  - `/loop`, que dura até 7 dias;
  - as tarefas do app desktop;
  - as Routines na nuvem, ainda em research preview.
- Alternativa que funciona em qualquer ambiente: `cron` chamando `claude -p` ou `codex exec`.
- Não há kit pronto parecido: o espaço é original.

## Lacunas
- Métodos da RAND.
- Licença do METR.
- Newsletters de sinais.
- **Dados do Brasil (IBGE, CAGED, lei de IA)**.
- Automações do Codex.
- Aprovação final do Omnibus.
