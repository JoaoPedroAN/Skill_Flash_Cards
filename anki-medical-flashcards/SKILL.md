---
name: anki-medical-flashcards
description: >-
  Realiza Fact-Check médico rigoroso de aulas, slides, fotos e anotações de alunos (cruzando com
  diretrizes oficiais e PubMed) e cria flashcards médicos de alta retenção baseados em evidências
  (PubMed DEAME framework, Woźniak, Matuschak, AnKing e Yousmle), exportando diretamente arquivos
  nativos do Anki (.apkg) nas 4 modalidades: (1) Atômico Puro, (2) Híbrido USMLE Step 1 (Cloze + Extra),
  (3) Mini-Vinheta Clínica (Step 2 CK / Conduta) e (4) Caderno de Erros de Questões (Dissecação de Questão Errada).
---

# Anki Medical Flashcard Generator Skill (`.apkg`)

Esta skill audita materiais de estudo médico (slides, PDFs, fotos de aula, anotações manuscritas, resumos de IA e questões de prova) por meio de um **Fact-Check científico obrigatório** e os transforma em pacotes nativos do Anki (**`.apkg`**) prontos para importação com Note Types estilizados (modo claro/escuro automático).

---

## 0. Etapa Obrigatória Pré-Criação: Fact-Check Médico e Auditoria do Material

> 🚫 **REGRA MANDATÓRIA: PROIBIÇÃO DE MARCAS REGISTRADAS E NOMES COMERCIAIS**
> **NUNCA** registrar marcas registradas ou nomes comerciais protegidos por direitos autorais de cursinhos preparatórios, plataformas educacionais ou editoras em nenhuma parte dos flashcards ou arquivos gerados — incluindo `deck_name`, `source`, `tags`, `front`, `back`, `text`, `extra`, nomes de arquivos `.json` ou pacotes `.apkg`.
>
> **Marcas terminantemente proibidas incluem (mas não se limitam a):**
> * *Medcurso / Med curso*, *Medgrupo / Med grupo*, *Medcof / Med coff*, *Prisma Medicina / Prisma medicina*, *FluidMed / Fluid med*, *Estratégia MED / Estratégia med*, *Hardwork Medicina*, *Sanar / SanarMed*, *SJT*, etc.
>
> **Padrão Obrigatório de Substituição e Anonimização:**
> 1. **Nome do Deck (`deck_name`):** Use sempre a taxonomia médica universal por especialidade e patologia (ex.: `Medicina::Cardiologia::Parada Cardiorrespiratoria e Ressuscitacao`, `Medicina::Neurologia::AVC Isquemico`).
> 2. **Campo `source`:** Cite exclusivamente diretrizes oficiais de sociedades médicas, ensaios clínicos ou livros-texto de referência (ex.: `Diretrizes AHA/SBC 2020-2025`, `Diretriz Brasileira de Fibrilação Atrial (SBC)`, `Harrison Medicina Interna`, `First Aid / Pathoma`).
> 3. **Conteúdo dos Cards (`front`, `back`, `text`, `extra`):** Extraia apenas conceitos fisiopatológicos e clínicos puros baseados em evidências. É expressamente proibido citar nomes de professores, jargões proprietários de cursinhos, logotipos ou referências a apostilas e aulas de plataformas comerciais.

> **Regra Áurea de Qualidade:** **NUNCA gere flashcards diretamente de anotações de alunos, transcrições de IA ou slides sem antes realizar um Fact-Check completo.** Consolidar um dado clínico incorreto na memória de longo prazo via repetição espaçada é grave tanto para provas (USMLE, Revalida, Residência) quanto para a segurança do paciente.

Sempre que o usuário fornecer materiais de estudo (slides, PDFs, apostilas, anotações ou resumos), execute obrigatoriamente estes **3 passos antes de gerar o `.apkg`**:

### Passo 0.1 — Cruzamento Interno de Fontes (Aula Principal vs. Anotações/Resumos)
Leia todos os arquivos fornecidos (PDFs de slides, fotos da lousa/projeção, cadernos manuscritos e resumos automatizados) e procure ativamente por:
1. **Inversões de sinais matemáticos e operadores:** Troca de $<$ por $>$, ou de $\ge$ por $>$ (ex.: anotar `PC-ASPECTS > 6` quando a diretriz define `≥ 6`).
2. **Inversão de ramos de fluxogramas:** Trocar a conduta do ramo *"Sim"* pela do ramo *"Não"* (ex.: inverter metas pressóricas de pacientes *com reperfusão* vs. *sem reperfusão*).
3. **Mistura entre tabelas ou escores distintos:** Fundir o ponto de corte de uma escala diagnóstica usada para uma finalidade com o corte usado para outra (ex.: confundir o NIHSS de definição de *AVC Minor* para dupla antiagregação com o NIHSS de *timing* de anticoagulação).
4. **Doses, vias e janelas temporais:** Conferir $\text{mg/kg}$, dose máxima absoluta, tempo de infusão (*bolus* vs. infusão contínua) e janelas em horas/dias.
5. **Omissões de resumos automatizados (IA):** Resumos gerados por ferramentas de transcrição costumam omitir valores numéricos, pontos de corte e contraindicações (Classe 3). Reponha todos esses números a partir da fonte primária.

### Passo 0.2 — Verificação Externa em Diretrizes e PubMed
* Confira as afirmações da aula e do material contra as **diretrizes médicas vigentes** (AHA/ASA, ESC, SBC, KDIGO, IDSA, ATLS, ACOG, etc.) e ensaios clínicos de referência usando busca web (`search_web`).
* Audite também os próprios slides da aula em busca de eventuais *typos* gráficos (ex.: um slide resumo que escreva `80 a 180 mg/dL` onde o estudo original e outro slide da mesma aula dizem `80 a 130 mg/dL`).

### Passo 0.3 — Entrega do Relatório de Fact-Check e Correção Factual
Apresente ao usuário (e, quando apropriado, salve em um arquivo Markdown de auditoria na pasta de estudos) os achados classificados em:
* 🚨 **Erro Crítico:** Conduta invertida, dose perigosa, troca de sinal matemático ou anotação/slide que recomenda algo proscrito (Classe 3 / Dano).
* ⚠️ **Imprecisão / Confusão de Critérios:** Mistura de pontos de corte, janelas incompletas ou terminologia fisiopatológica/radiológica imprecisa.
* 💡 **Complemento High-Yield:** Dados numéricos essenciais que estavam nos slides/diretrizes mas foram omitidos no material.

> **Importante:** Se você identificar erros ou divergências em anotações, slides ou resumos, aponte-os claramente no relatório de Fact-Check e gere os flashcards com os **dados corretos e atualizados**. **NUNCA crie flashcards do modelo `question_error` para anotações de terceiros ou erros de slides.** Cards de erro são reservados **exclusivamente** para questões de prova que o próprio usuário errou ou para erros que ele expressamente pedir para dissecar.

### Passo 0.4 — Auditoria Anti-Redundância e Princípio do Card Único (Obrigatório)
Antes de escrever o JSON final, execute uma triagem rígida para eliminar proliferação e cards repetitivos:
1. **Cardinalidade Estrita (1 Fato Decisivo = 1 Único Card no Deck):** É expressamente proibido testar o mesmo conceito ou decisão clínica em modelos diferentes. Se uma conduta virou `clinical_vignette`, **não** crie um card `atomic` nem um `usmle_hybrid` para a mesma conduta.
2. **Proibição de Cards Espelhados / Invertidos:** Não gere pares de perguntas recíprocas (ex.: *"Qual a causa de X?"* e *"A condição Y causa o quê?"*). Priorize sempre a direção de maior valor clínico:
   * Achados clínicos / ECG / Lab $\to$ **Diagnóstico provável**.
   * Diagnóstico + Gravidade $\to$ **Próximo passo / Conduta imediata**.
3. **Anti-Hiperatomização de Tríades e Critérios:** Nunca divida uma tríade clássica ou os critérios de um escore em 3 ou 4 cards separados e parecidos. Agrupe-os em:
   * Um único card `atomic` cuja resposta traga os itens de forma direta e concisa, **ou**
   * Um único `usmle_hybrid` usando `{{c1::...}}` compartilhado.
4. **Poda de Respostas Idênticas:** Se dois cards possuem a mesma resposta exata (ex.: dois cards cuja resposta seja *"Esmolol IV"* ou *"Laparotomia"*), avalie se ambos são indispensáveis. Se testarem o mesmo princípio clínico, elimine o menos contextualizado.

---

## 1. Quando Usar Cada um dos 4 Modelos de Flashcard

Após concluir o **Fact-Check (Etapa 0)**, classifique cada conceito médico validado em uma das **4 arquiteturas abaixo**:

### Caso 1: `atomic` — Flashcard Atômico Puro (Estilo Woźniak / Matuschak)
* **Quando usar:** Fatos arbitrários, farmacologia pontual (mecanismo de ação, antídotos, efeitos adversos clássicos), microbiologia, genética (translocações, genes), bioquímica (enzimas deficientes) e valores de corte laboratoriais.
* **Regras de ouro:**
  * **Frente (`front`):** Pergunta altamente específica e sem ambiguidade, testando **apenas 1 variável**.
  * **Verso (`back`):** Resposta curtíssima (**1 a 8 palavras**). Proibido usar listas longas ou parágrafos no campo de resposta principal.
  * **Contexto opcional (`extra`):** Uma frase curta (1–2 linhas) explicando o mecanismo ou mnemônico se necessário.

### Caso 2: `usmle_hybrid` — Flashcard Híbrido USMLE Step 1 (Estilo *AnKing / Zanki* — Cloze + Campo `Extra` Enciclopédico)
* **Quando usar:** Estudo longitudinal de ciências básicas, fisiopatologia integrada ou revisão de blocos teóricos extensos onde você quer **velocidade na frente (3–6s)** aliada a **consulta imediata no verso (`Extra`)**.
* **Regras de ouro:**
  * **REGRA MANDATÓRIA DO CLOZE ÚNICO (`c1` EXCLUSIVO — 1 Nota = 1 Card):**
    * Use **SEMPRE e APENAS o índice `{{c1::...}}`**. É terminantemente proibido criar `{{c2::...}}` ou `{{c3::...}}` no mesmo card.
    * *Por que essa regra é inegociável:* No Anki, cada número de cloze adicional gera um card irmão separado a partir da mesma nota. Isso gera cards gêmeos quase idênticos (fadiga de revisão) e impede que o usuário exclua ou edite um card individual sem ter que reindexar clozes ou lidar com cartões vazios (*Empty Cards*).
    * Se a frase contiver dois termos correlatos ou uma tríade/parâmetro que devam ser lembrados juntos, use **o mesmo índice para todos**: `Na {{c1::Esclerose Tuberosa}}, a mutação ocorre nos genes {{c1::TSC1 ou TSC2}}...`. Dessa forma, o Anki gera **exatamente 1 card** ocultando os dois nós simultaneamente.
  * **Texto Cloze (`text`):** 1 a 2 frases com ancoragem clínica/fisiopatológica contendo o nó decisivo em `{{c1::...}}`. Nunca oculte metade da frase; oculte apenas o elemento chave.
  * **Campo Extra (`extra`):** Completo e estruturado ("One-Stop-Shop"). Inclua fisiopatologia resumida, pérolas de prova (*High-Yield Pearls*), tabelas comparativas em HTML simples ou mnemônicos para leitura rápida caso o usuário erre o card.
  * **Fonte (`source`):** Referência ou tópico (ex.: *First Aid / Pathoma / Nefrologia*).

### Caso 3: `clinical_vignette` — Flashcard Extenso de Mini-Vinheta Clínica (Estilo USMLE Step 2 CK / *Cheesy Dorian* / *Yousmle*)
* **Quando usar:** Ciclo clínico, internato, diagnóstico diferencial de casos clínicos e algoritmos de conduta (*Next Best Step in Management*).
* **Regras de ouro:**
  * **Vinheta Clínica (`vignette`):** Caso clínico enxuto de 2 a 4 frases contendo: (1) Demografia + Queixa principal/tempo de evolução, (2) Sinais vitais e achados críticos do exame físico, (3) Dados laboratoriais/imagem pertinentes.
  * **Pergunta Direcionada (`question`):** Pergunta de 2ª ou 3ª ordem na Taxonomia de Bloom: *"Qual é o diagnóstico mais provável?"*, *"Qual é o próximo melhor passo no manejo imediato?"*, ou *"Qual o mecanismo fisiopatológico responsável por este achado?"*.
  * **Resposta Direta (`answer`):** A conduta ou diagnóstico exato em destaque (1 linha).
  * **Raciocínio Clínico e Fluxograma (`extra`):** Explicação dos discriminadores positivos da vinheta e do algoritmo de manejo (1ª linha vs. 2ª linha, sinais de alarme).

### Caso 4: `question_error` — Transformação de Erro de Questão em Flashcard (Caderno de Erros Inteligente)
* **Quando usar:** **EXCLUSIVAMENTE** quando o usuário fornecer uma questão de prova/simulado (*UWorld*, *AMBOSS*, *NBME*, Revalida ou Residência) que ele próprio errou ou ficou em dúvida, ou quando ele expressamente apontar um erro pessoal que deseja dissecar. **Nunca** utilize este modelo para anotações de aula, resumos ou slides de terceiros.
* **Protocolo Obrigatório de Dissecação do Erro (NUNCA copie a questão inteira com as 5 alternativas!):**
  1. **Classifique a Causa-Raiz do Erro (`error_type`):**
     * `Lacuna Factual`: Faltou um dado direto (dose, antídoto, gene, critério).
     * `Falha de Reconhecimento (Illness Script)`: Não reconheceu a doença descrita no caso clínico.
     * `Confusão com Distrator (Diagnóstico Diferencial)`: Ficou em dúvida entre a resposta certa ($A$) e outra opção parecida ($B$) e marcou $B$.
     * `Erro de Algoritmo / Conduta (Next Best Step)`: Sabia o diagnóstico, mas inverteu a prioridade da conduta (ex.: pediu exame demorado em paciente instável).
  2. **Formule a Frente (`prompt`):**
     * Se foi *Confusão com Distrator*: Formule uma pergunta de contraste direto ou uma mini-vinheta focada no achado que separa $A$ de $B$.
     * Se foi *Erro de Conduta*: Apresente o cenário clínico com o sinal determinante de gravidade/estágio e pergunte a conduta imediata.
  3. **Formule a Resposta (`answer`):** Direta, clara e objetiva.
  4. **Preencha a Análise do Distrator (`why_not_distractor`):** Explique claramente **por que a alternativa marcada estava errada neste paciente** E **em qual cenário clínico aquela alternativa marcada SERIA a resposta correta** (transformando 1 erro em 2 acertos futuros).
  5. **Extraia o Objetivo Educacional (`educational_objective`):** A regra áurea generalizável (1 a 2 frases) que resolve qualquer questão futura sobre o mesmo princípio.

---

## 2. Como Gerar o Arquivo `.apkg` Automaticamente

Sempre que o usuário pedir para criar flashcards ou exportar para o Anki, gere um arquivo JSON seguindo o schema abaixo e execute o script [`scripts/generate_apkg.py`](file:///C:/Users/joaop/.gemini/config/skills/anki-medical-flashcards/scripts/generate_apkg.py).

### 2.1. Formato do JSON de Entrada

```json
{
  "deck_name": "Medicina::Cardiologia e Emergencias",
  "cards": [
    {
      "type": "atomic",
      "front": "Qual é o antídoto específico para intoxicação grave por beta-bloqueadores refratária à atropina e expansão volêmica?",
      "back": "Glucagon IV (em bolus seguido de infusão contínua)",
      "extra": "Mecanismo: Ativa a adenilato ciclase aumentando o AMPc intracelular de forma independente dos receptores beta-adrenérgicos.",
      "tags": ["Farmacologia", "Emergencia", "Atomico"]
    },
    {
      "type": "usmle_hybrid",
      "text": "Na {{c1::Esclerose Tuberosa}}, a mutação nos genes {{c1::TSC1 (hamartina) ou TSC2 (tuberina)}} leva à hiperativação da via mTOR e ao desenvolvimento de rabdomiomas cardíacos e angiofibromas faciais.",
      "extra": "<ul><li><b>Padrão de herança:</b> Autossômica dominante.</li><li><b>Achados clássicos (EPILOIA):</b> Máculas hipomelanóticas em folha de freixo (<i>ash-leaf spots</i>), tubérculos corticais, nódulos subependimários, angiomiolipomas renais bilaterais.</li><li><b>Tratamento direcionado:</b> Inibidores de mTOR (Everolimo / Sirolimo).</li></ul>",
      "source": "First Aid Step 1 / Neurologia & Genética",
      "tags": ["USMLE_Step1", "Genetica", "Neurologia", "AnKing_Style"]
    },
    {
      "type": "clinical_vignette",
      "vignette": "Homem de 62 anos, tabagista e hipertenso, chega à emergência com dor torácica lancinante de início súbito irradiada para a região interescapular há 1 hora. PA = 190/110 mmHg no braço direito e 145/85 mmHg no braço esquerdo; FC = 108 bpm. ECG mostra sobrecarga ventricular esquerda sem supradesnivelamento de ST. Angio-TC de tórax revela lâmina de dissecção restrita à aorta torácica descendente (distal à artéria subclávia esquerda), sem sinais de ruptura ou má perfusão visceral.",
      "question": "Qual é o próximo melhor passo imediato no manejo farmacológico deste paciente?",
      "answer": "Beta-bloqueador venoso (ex.: Esmolol ou Labetalol IV) para atingir FC < 60 bpm e PAS 100–120 mmHg.",
      "extra": "<b>Classificação:</b> Dissecção Aórtica Stanford Tipo B (DeBakey III) não complicada.<br><b>Regra de Manejo:</b> Controle de impulso cardíaco (<i>anti-impulse therapy</i>) reduzindo a força de cisalhamento ($dP/dt$) com beta-bloqueador ANTES de associar vasodilatadores diretos (como nitroprussiato de sódio), pois o vasodilatador isolado provoca taquicardia reflexa e propaga a dissecção.",
      "tags": ["USMLE_Step2CK", "Cardiologia", "Vignette"]
    },
    {
      "type": "question_error",
      "error_type": "Erro de Algoritmo / Conduta (Next Best Step)",
      "prompt": "Paciente vítima de colisão automobilística apresenta dor abdominal difusa, PA = 78/42 mmHg, FC = 132 bpm após 1L de cristaloide/concentrado de hemácias e FAST positivo no espaço de Morrison. Qual é a conduta imediata?",
      "answer": "Laparotomia exploradora imediata (Centro Cirúrgico).",
      "why_not_distractor": "<b>Por que NÃO realizar Tomografia Computadorizada (TC) de abdome com contraste:</b> A TC exige transporte do paciente e tempo, sendo formalmente contraindicada no trauma abdominal fechado <b>hemodinamicamente instável</b> com FAST positivo. <br><b>Quando a TC seria a resposta certa:</b> Apenas se o paciente estivesse <b>hemodinamicamente estável</b> (PAS > 90 mmHg mantida), permitindo avaliar o grau de lesão de vísceras sólidas para tratamento conservador.",
      "educational_objective": "No trauma abdominal contuso com instabilidade hemodinâmica refratária e FAST (ou LPD) positivo, a conduta imediata é sempre laparotomia exploradora de emergência, nunca tomografia.",
      "tags": ["Caderno_de_Erros", "Cirurgia", "Trauma"]
    }
  ]
}
```

### 2.2. Comando para Executar o Gerador

```powershell
python "C:\Users\joaop\.gemini\config\skills\anki-medical-flashcards\scripts\generate_apkg.py" --input "caminho/para/cards.json" --output "caminho/para/deck.apkg"
```

> **Nota Técnica:** O script [`generate_apkg.py`](file:///C:/Users/joaop/.gemini/config/skills/anki-medical-flashcards/scripts/generate_apkg.py) cria nativamente os 4 Note Types no banco de dados SQLite interno do Anki (`collection.anki2`), inclusive configurando o Note Type `USMLE Hybrid Cloze` com a flag oficial `type = 1` (Cloze nativo do Anki) para que múltiplas ocultações (`{{c1::...}}`, `{{c2::...}}`) funcionem perfeitamente no Anki Desktop, AnkiWeb, AnkiDroid e AnkiMobile.
