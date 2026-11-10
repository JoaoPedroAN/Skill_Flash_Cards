---
name: anki-medical-flashcards
description: >-
  Realiza Fact-Check médico rigoroso de aulas, slides, fotos e anotações de alunos (cruzando com
  diretrizes oficiais e PubMed) e cria flashcards médicos de alta retenção baseados em evidências
  (PubMed DEAME framework, Woźniak, Matuschak, AnKing e Yousmle), exportando diretamente arquivos
  nativos do Anki (.apkg) nas 5 modalidades: (1) Atômico Puro, (2) Híbrido USMLE Step 1 (Cloze + Extra),
  (3) Mini-Vinheta Clínica (Step 2 CK / Conduta), (4) Caderno de Erros de Questões (Dissecação de Questão Errada)
  e (5) Oclusão de Imagem; todos aceitam imagens (ECG, radiografia, lesões, fluxogramas) e áudio (ausculta).
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
> 2. **Campos `source` e `source_year` (OBRIGATÓRIOS em todo card — o script recusa card sem `source`):**
>    * **Cite:** a diretriz mais recente da sociedade médica, artigos de referência (ensaio clínico, revisão sistemática, metanálise; formato `Autor et al., Revista`) ou livros-texto (Harrison, Goldman-Cecil, Sabiston, Robbins, Guyton, Nelson, Williams Obstetrics etc.). Ex.: `Diretriz AHA/ASA de AVC isquêmico agudo`, `Diretriz Brasileira de Fibrilação Atrial (SBC)`, `Harrison Medicina Interna`.
>    * **Nunca cite:** o material que o usuário forneceu (aula, slides, apostila, resumo) nem materiais de preparação para prova (First Aid, Pathoma, UWorld, AMBOSS, Sketchy, decks prontos, cursinhos). Esses servem só de ponto de partida; a referência do card é a fonte primária que confirmou o dado no Fact-Check.
>    * **`source_year`:** ano da diretriz/edição (ex.: `2026`). Confira no PubMed ou no site da sociedade; se não tiver certeza, deixe vazio — nunca invente.
> 3. **Conteúdo dos Cards (`front`, `back`, `text`, `extra`, `tags`):** Extraia apenas conceitos fisiopatológicos e clínicos puros baseados em evidências. É expressamente proibido citar nomes de professores, jargões proprietários de cursinhos, logotipos ou referências a apostilas e aulas de plataformas comerciais.
> 4. **Nomes de métodos e decks comerciais (AnKing, Zanki, Yousmle, Cheesy Dorian, UWorld, AMBOSS etc.):** servem apenas de referência metodológica para esta skill. **Não os cite em nenhuma parte dos cards** (texto, tags ou `source`).

> **Regra Áurea de Qualidade:** **NUNCA gere flashcards diretamente de anotações de alunos, transcrições de IA ou slides sem antes realizar um Fact-Check completo.** Consolidar um dado clínico incorreto na memória de longo prazo via repetição espaçada é grave tanto para provas (USMLE, Revalida, Residência) quanto para a segurança do paciente.

Sempre que o usuário fornecer materiais de estudo (slides, PDFs, apostilas, anotações ou resumos), execute obrigatoriamente estes **4 passos (0.1 a 0.4) antes de gerar o `.apkg`**:

### Passo 0.1 — Cruzamento Interno de Fontes (Aula Principal vs. Anotações/Resumos)
Leia todos os arquivos fornecidos (PDFs de slides, fotos da lousa/projeção, cadernos manuscritos e resumos automatizados) e procure ativamente por:
1. **Inversões de sinais matemáticos e operadores:** Troca de < por >, ou de ≥ por > (ex.: anotar `PC-ASPECTS > 6` quando a diretriz define `≥ 6`).
2. **Inversão de ramos de fluxogramas:** Trocar a conduta do ramo *"Sim"* pela do ramo *"Não"* (ex.: inverter metas pressóricas de pacientes *com reperfusão* vs. *sem reperfusão*).
3. **Mistura entre tabelas ou escores distintos:** Fundir o ponto de corte de uma escala diagnóstica usada para uma finalidade com o corte usado para outra (ex.: confundir o NIHSS de definição de *AVC Minor* para dupla antiagregação com o NIHSS de *timing* de anticoagulação).
4. **Doses, vias e janelas temporais:** Conferir mg/kg, dose máxima absoluta, tempo de infusão (*bolus* vs. infusão contínua) e janelas em horas/dias.
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
2. **Dois Sentidos Só Quando Ambos São High-Yield:** O objetivo do deck é poucos cards de alto impacto, não cobertura máxima. Por padrão, gere apenas a direção de maior valor clínico:
   * Achados clínicos / eletrocardiograma (ECG) / exames laboratoriais → **Diagnóstico provável**.
   * Diagnóstico + Gravidade → **Próximo passo / Conduta imediata**.

   Adicione o segundo sentido (campos `reverse_front` / `reverse_back` do modelo `atomic`) **somente** quando a prova cobra o fato nas duas direções (ex.: deficiência enzimática ↔ doença; antídoto ↔ intoxicação; achado patognomônico ↔ doença). O sentido inverso fica na mesma nota (não conta como card duplicado) e deve ter pergunta própria, curta e sem ambiguidade. Na dúvida, não inverta.
3. **Anti-Hiperatomização de Tríades e Critérios:** Nunca divida uma tríade clássica ou os critérios de um escore em 3 ou 4 cards separados e parecidos. Agrupe-os em:
   * Um único card `atomic` cuja resposta traga os itens de forma direta e concisa, **ou**
   * Um único `usmle_hybrid` usando `{{c1::...}}` compartilhado.
4. **Poda de Respostas Idênticas:** Se dois cards possuem a mesma resposta exata (ex.: dois cards cuja resposta seja *"Esmolol IV"* ou *"Laparotomia"*), avalie se ambos são indispensáveis. Se testarem o mesmo princípio clínico, elimine o menos contextualizado.

### Passo 0.5 — Regras de Escrita (Obrigatórias em Todos os Cards)
1. **Siglas sempre por extenso, seguidas da sigla, todas as vezes em que aparecerem** (em `front`, `back`, `text`, `extra`, `vignette`, `answer` etc.). Ex.: "acidente vascular cerebral isquêmico (AVCi)", "pressão arterial (PA)", "frequência cardíaca (FC)". Unidades de medida (mg, mmHg, bpm) não precisam ser expandidas.
2. **Sem LaTeX:** o Anki não lê `$...$`. Use símbolos Unicode: ≥ ≤ ≠ ± → ↑ ↓ ×, letras gregas (α β γ Δ μ), índices (β₂, α₁, CO₂, SpO₂) e frações simples (mg/kg, dP/dt).
3. **Tags hierárquicas** no formato `Grande_Area::Tema::Subtema` (ex.: `Clinica_Medica::Cardiologia::Insuficiencia_Cardiaca`, `Cirurgia::Trauma::Trauma_Abdominal`, `Preventiva::Epidemiologia::Testes_Diagnosticos`). Grandes áreas: `Clinica_Medica`, `Cirurgia`, `Pediatria`, `Ginecologia_Obstetricia`, `Preventiva`, `Ciclo_Basico`. Quando o usuário informar a incidência do tema na prova, acrescente `incidencia::alta`, `incidencia::media` ou `incidencia::baixa`; nunca estime incidência sem dado.

---

## 1. Quando Usar Cada um dos 5 Modelos de Flashcard

Após concluir o **Fact-Check (Etapa 0)**, classifique cada conceito médico validado em uma das **5 arquiteturas abaixo**:

### Caso 1: `atomic` — Flashcard Atômico Puro (Estilo Woźniak / Matuschak)
* **Quando usar:** Fatos arbitrários, farmacologia pontual (mecanismo de ação, antídotos, efeitos adversos clássicos), microbiologia, genética (translocações, genes), bioquímica (enzimas deficientes) e valores de corte laboratoriais.
* **Regras de ouro:**
  * **Frente (`front`):** Pergunta altamente específica e sem ambiguidade, testando **apenas 1 variável**.
  * **Verso (`back`):** Resposta curtíssima (**1 a 8 palavras**). Proibido usar listas longas ou parágrafos no campo de resposta principal.
  * **Contexto opcional (`extra`):** Uma frase curta (1–2 linhas) explicando o mecanismo ou mnemônico se necessário.
  * **Sentido inverso opcional (`reverse_front` + `reverse_back`):** Só quando os dois sentidos forem high-yield (ver Passo 0.4). Os dois campos devem vir juntos; o script recusa o card se vier só um.

### Caso 2: `usmle_hybrid` — Flashcard Híbrido USMLE Step 1 (Estilo *AnKing / Zanki* — Cloze + Campo `Extra` Enciclopédico)
* **Quando usar:** Estudo longitudinal de ciências básicas, fisiopatologia integrada ou revisão de blocos teóricos extensos onde você quer **velocidade na frente (3–6s)** aliada a **consulta imediata no verso (`Extra`)**.
* **Regras de ouro:**
  * **REGRA MANDATÓRIA DO CLOZE ÚNICO (`c1` EXCLUSIVO — 1 Nota = 1 Card):**
    * Use **SEMPRE e APENAS o índice `{{c1::...}}`**. É terminantemente proibido criar `{{c2::...}}` ou `{{c3::...}}` no mesmo card.
    * *Por que essa regra é inegociável:* No Anki, cada número de cloze adicional gera um card irmão separado a partir da mesma nota. Isso gera cards gêmeos quase idênticos (fadiga de revisão) e impede que o usuário exclua ou edite um card individual sem ter que reindexar clozes ou lidar com cartões vazios (*Empty Cards*).
    * Se a frase contiver dois termos correlatos ou uma tríade/parâmetro que devam ser lembrados juntos, use **o mesmo índice para todos**: `Na {{c1::Esclerose Tuberosa}}, a mutação ocorre nos genes {{c1::TSC1 ou TSC2}}...`. Dessa forma, o Anki gera **exatamente 1 card** ocultando os dois nós simultaneamente.
  * **Texto Cloze (`text`):** 1 a 2 frases com ancoragem clínica/fisiopatológica contendo o nó decisivo em `{{c1::...}}`. Nunca oculte metade da frase; oculte apenas o elemento chave.
  * **Campo Extra (`extra`):** Completo e estruturado ("One-Stop-Shop"). Inclua fisiopatologia resumida, pérolas de prova (*High-Yield Pearls*), tabelas comparativas em HTML simples ou mnemônicos para leitura rápida caso o usuário erre o card.
  * **Fonte (`source` + `source_year`):** Diretriz, artigo ou livro-texto atual e ano (ex.: *Northrup et al., Pediatr Neurol — critérios internacionais do complexo esclerose tuberosa*, 2021). O script recusa qualquer card com `c2`, `c3` etc.

### Caso 3: `clinical_vignette` — Flashcard Extenso de Mini-Vinheta Clínica (Estilo USMLE Step 2 CK / *Cheesy Dorian* / *Yousmle*)
* **Quando usar:** Ciclo clínico, internato, diagnóstico diferencial de casos clínicos e algoritmos de conduta (*Next Best Step in Management*).
* **Regras de ouro:**
  * **Vinheta Clínica (`vignette`):** Caso **curto e direcionado**: 1 a 2 frases, no máximo ~40 palavras. Inclua só os discriminadores que levam à resposta (demografia + queixa + 1 a 3 achados decisivos de exame, laboratório ou imagem). Corte tudo que não muda a resposta (sinais vitais normais, antecedentes irrelevantes, achados negativos que não descartam diferencial importante). Teste: se uma frase pode ser apagada sem mudar a resposta, apague.
  * **Pergunta Direcionada (`question`):** Pergunta de 2ª ou 3ª ordem na Taxonomia de Bloom: *"Qual é o diagnóstico mais provável?"*, *"Qual é o próximo melhor passo no manejo imediato?"*, ou *"Qual o mecanismo fisiopatológico responsável por este achado?"*.
  * **Resposta Direta (`answer`):** A conduta ou diagnóstico exato em destaque (1 linha).
  * **Raciocínio Clínico e Fluxograma (`extra`):** Curto: até 3 itens (por que é esse diagnóstico/conduta, o que mudaria a conduta, armadilha clássica de prova).

### Caso 4: `question_error` — Transformação de Erro de Questão em Flashcard (Caderno de Erros Inteligente)
* **Quando usar:** **EXCLUSIVAMENTE** quando o usuário fornecer uma questão de prova/simulado (*UWorld*, *AMBOSS*, *NBME*, Revalida ou Residência) que ele próprio errou ou ficou em dúvida, ou quando ele expressamente apontar um erro pessoal que deseja dissecar. **Nunca** utilize este modelo para anotações de aula, resumos ou slides de terceiros.
* **Protocolo Obrigatório de Dissecação do Erro (NUNCA copie a questão inteira com as 5 alternativas!):**
  1. **Classifique a Causa-Raiz do Erro (`error_type`):**
     * `Lacuna Factual`: Faltou um dado direto (dose, antídoto, gene, critério).
     * `Falha de Reconhecimento (Illness Script)`: Não reconheceu a doença descrita no caso clínico.
     * `Confusão com Distrator (Diagnóstico Diferencial)`: Ficou em dúvida entre a resposta certa (A) e outra opção parecida (B) e marcou B.
     * `Erro de Algoritmo / Conduta (Next Best Step)`: Sabia o diagnóstico, mas inverteu a prioridade da conduta (ex.: pediu exame demorado em paciente instável).
  2. **Formule a Frente (`prompt`):**
     * Se foi *Confusão com Distrator*: Formule uma pergunta de contraste direto ou uma mini-vinheta focada no achado que separa A de B.
     * Se foi *Erro de Conduta*: Apresente o cenário clínico com o sinal determinante de gravidade/estágio e pergunte a conduta imediata.
  3. **Formule a Resposta (`answer`):** Direta, clara e objetiva.
  4. **Preencha a Análise do Distrator (`why_not_distractor`):** Explique claramente **por que a alternativa marcada estava errada neste paciente** E **em qual cenário clínico aquela alternativa marcada SERIA a resposta correta** (transformando 1 erro em 2 acertos futuros).
  5. **Extraia o Objetivo Educacional (`educational_objective`):** A regra áurea generalizável (1 a 2 frases) que resolve qualquer questão futura sobre o mesmo princípio.

### Caso 5: `image_occlusion` — Oclusão de Imagem (Pré-Desenhada)
* **Quando usar:** quando a prova cobra **reconhecer uma estrutura ou um passo numa imagem**: anatomia radiológica, fluxogramas de diretriz, esquemas de fisiologia, lâminas, achados de eletrocardiograma (ECG). Woźniak (regra 8): a oclusão de imagem rende tanto quanto o cloze.
* **Como funciona:** cada área em `occlusions` vira **1 card**. Na frente a área fica coberta em laranja; no verso aparece com contorno vermelho e a resposta embaixo.
  * `mode: "hide_one"` (padrão): esconde só a área perguntada; as outras ficam visíveis (bom para estruturas independentes).
  * `mode: "hide_all"`: esconde todas (as outras em cinza); use quando ver uma área entregaria a vizinha (ex.: passos seguidos de um fluxograma).
* **Coordenadas (`box`):** `[x, y, largura, altura]` em frações de 0 a 1 da imagem (canto superior esquerdo = 0,0).
* **Fluxo obrigatório:**
  1. Abra a imagem, estime as caixas e gere a **prévia numerada**: `python "<pasta da skill>\scripts\generate_apkg.py" -i cards.json --preview-occlusions <pasta>`.
  2. **Abra a prévia e confira** se cada caixa cobre todo o alvo (rótulo inteiro, sem cortar letras) e nada além dele. Ajuste e gere de novo até ficar certo.
  3. Mostre a prévia ao usuário antes de gerar o `.apkg`.
* **High-yield:** cubra só as estruturas que a prova cobra (em geral 3 a 6 por imagem), não todos os rótulos.

---

## 1.1. Imagens e Áudio (Qualquer Modelo)

Todos os modelos aceitam mídia opcional. O caminho é relativo à pasta do JSON.

| Campo | Onde aparece | Uso típico |
|---|---|---|
| `image_front` | Junto da pergunta | Eletrocardiograma (ECG), radiografia, lesão de pele, fundo de olho, lâmina → "Qual o diagnóstico?" |
| `image_back` | No verso (área Extra) | Fluxograma, esquema ou exame que reforça a resposta |
| `audio_front` | Toca ao abrir o card | Ausculta cardíaca/pulmonar → "Qual o achado?" |
| `audio_back` | No verso | Som que exemplifica a resposta |
| `media_credit` | Rodapé do verso | Autor, site e licença da mídia de terceiros |

**Regras obrigatórias:**
1. **De onde vem a mídia:**
   * Arquivos que o usuário fornecer (fotos, prints, slides): pode usar.
   * Apostilas e materiais de cursinho: **só se o usuário indicar explicitamente** aquele material.
   * Fora isso: busque na internet, em livros-texto e PDFs abertos, priorizando bancos com licença aberta (Wikimedia Commons, Radiopaedia, Open-i/NLM, artigos de acesso aberto). Confira a licença na página da própria imagem e preencha `media_credit` (autor, site, licença). Antes de baixar qualquer arquivo, peça autorização ao usuário informando nome, origem e tamanho.
2. **A mídia não pode entregar a resposta:** recorte legendas, setas com nome, marcas d'água e títulos; o script renomeia o arquivo para um nome neutro (`med_<código>.jpg`) automaticamente.
3. **Sem marcas:** recorte logotipos e nomes de cursinho, plataforma ou professor de qualquer imagem.
4. **Recorte no achado:** a imagem deve mostrar o que se pergunta, sem área inútil. O script reduz para no máximo 1.200 px e salva em JPEG (leve para o celular).
5. **High-yield:** use imagem quando a prova cobra **reconhecer** algo visualmente (ou áudio para ausculta). Não ilustre card que já funciona só com texto.
6. Mídia de terceiros não verificada ou de origem desconhecida: deixe isso claro em `media_credit` e não compartilhe o deck.

**Onde o áudio rende mais:** ausculta cardíaca (sopros de estenose aórtica e insuficiência mitral, terceira bulha (B3), quarta bulha (B4), atrito pericárdico), ausculta pulmonar (estertores, sibilos, roncos, estridor, atrito pleural), pediatria (tosse ladrante do crupe, guincho da coqueluche, gemido expiratório do recém-nascido), neurologia (disartria, afasia).

---

## 2. Como Gerar o Arquivo `.apkg` Automaticamente

Sempre que o usuário pedir para criar flashcards ou exportar para o Anki, gere um arquivo JSON seguindo o schema abaixo e execute o script `scripts/generate_apkg.py`, que fica dentro da pasta desta skill.

### 2.1. Formato do JSON de Entrada

```json
{
  "deck_name": "Medicina::Cardiologia e Emergencias",
  "cards": [
    {
      "type": "atomic",
      "front": "Qual é o antídoto específico para intoxicação grave por beta-bloqueadores refratária à atropina e expansão volêmica?",
      "back": "Glucagon IV (em bolus seguido de infusão contínua)",
      "extra": "Mecanismo: Ativa a adenilato ciclase aumentando o monofosfato cíclico de adenosina (AMPc) intracelular de forma independente dos receptores beta-adrenérgicos.",
      "source": "Goldfrank's Toxicologic Emergencies (livro-texto)",
      "source_year": "",
      "tags": ["Clinica_Medica::Toxicologia::Antidotos"]
    },
    {
      "type": "atomic",
      "front": "Qual enzima está deficiente na doença de von Gierke (glicogenose tipo I)?",
      "back": "Glicose-6-fosfatase",
      "reverse_front": "A deficiência de glicose-6-fosfatase causa qual glicogenose?",
      "reverse_back": "Doença de von Gierke (glicogenose tipo I)",
      "source": "Kishnani et al., Genet Med — diretriz do American College of Medical Genetics and Genomics (ACMG) para glicogenose tipo I",
      "source_year": "2014",
      "tags": ["Ciclo_Basico::Bioquimica::Glicogenoses"]
    },
    {
      "type": "usmle_hybrid",
      "text": "Na {{c1::Esclerose Tuberosa}}, a mutação nos genes {{c1::TSC1 (hamartina) ou TSC2 (tuberina)}} leva à hiperativação da via mTOR e ao desenvolvimento de rabdomiomas cardíacos e angiofibromas faciais.",
      "extra": "<ul><li><b>Padrão de herança:</b> Autossômica dominante.</li><li><b>Achados clássicos (EPILOIA):</b> Máculas hipomelanóticas em folha de freixo (<i>ash-leaf spots</i>), tubérculos corticais, nódulos subependimários, angiomiolipomas renais bilaterais.</li><li><b>Tratamento direcionado:</b> Inibidores de mTOR (Everolimo / Sirolimo).</li></ul>",
      "source": "Northrup et al., Pediatr Neurol — critérios diagnósticos e recomendações internacionais do complexo esclerose tuberosa",
      "source_year": "2021",
      "tags": ["Clinica_Medica::Neurologia::Sindromes_Neurocutaneas", "Ciclo_Basico::Genetica"]
    },
    {
      "type": "clinical_vignette",
      "vignette": "Homem de 62 anos, hipertenso, com dor torácica súbita e lancinante irradiada para o dorso. Angiotomografia computadorizada (angio-TC): dissecção restrita à aorta descendente, sem ruptura nem má perfusão.",
      "question": "Qual é a primeira medida farmacológica?",
      "answer": "Betabloqueador intravenoso (IV) (esmolol ou labetalol): frequência cardíaca (FC) < 60 bpm e pressão arterial sistólica (PAS) 100–120 mmHg.",
      "extra": "<ul><li><b>Diagnóstico:</b> dissecção Stanford tipo B não complicada → tratamento clínico.</li><li><b>Armadilha:</b> vasodilatador antes do betabloqueador causa taquicardia reflexa e propaga a dissecção.</li><li><b>Muda a conduta:</b> ruptura, má perfusão ou dor refratária → reparo endovascular (TEVAR).</li></ul>",
      "source": "Diretriz ESC de doenças arteriais periféricas e da aorta; diretriz ACC/AHA de doenças da aorta (2022)",
      "source_year": "2024",
      "tags": ["Clinica_Medica::Cardiologia::Doencas_da_Aorta"]
    },
    {
      "type": "question_error",
      "error_type": "Erro de Algoritmo / Conduta (Next Best Step)",
      "prompt": "Paciente vítima de colisão automobilística apresenta dor abdominal difusa, pressão arterial (PA) = 78/42 mmHg, frequência cardíaca (FC) = 132 bpm após 1 L de cristaloide/concentrado de hemácias e avaliação ultrassonográfica focada no trauma (FAST) positiva no espaço de Morrison. Qual é a conduta imediata?",
      "answer": "Laparotomia exploradora imediata (Centro Cirúrgico).",
      "why_not_distractor": "<b>Por que NÃO realizar Tomografia Computadorizada (TC) de abdome com contraste:</b> A TC exige transporte do paciente e tempo, sendo formalmente contraindicada no trauma abdominal fechado <b>hemodinamicamente instável</b> com FAST positivo. <br><b>Quando a TC seria a resposta certa:</b> Apenas se o paciente estivesse <b>hemodinamicamente estável</b> (PAS > 90 mmHg mantida), permitindo avaliar o grau de lesão de vísceras sólidas para tratamento conservador.",
      "educational_objective": "No trauma abdominal contuso com instabilidade hemodinâmica refratária e FAST (ou LPD) positivo, a conduta imediata é sempre laparotomia exploradora de emergência, nunca tomografia.",
      "source": "Diretriz WSES de trauma hepático (Coccolini et al., World J Emerg Surg); ATLS (American College of Surgeons)",
      "source_year": "2020",
      "tags": ["Caderno_de_Erros", "Cirurgia::Trauma::Trauma_Abdominal"]
    }
  ]
}
```

### 2.1.1. Exemplo com Imagem, Áudio e Oclusão

```json
{
  "deck_name": "Medicina::Cardiologia::Exames",
  "cards": [
    {
      "type": "atomic",
      "front": "Qual o diagnóstico deste eletrocardiograma (ECG)?",
      "back": "Bloqueio atrioventricular (BAV) de 2º grau Mobitz II",
      "image_front": "midia/ecg_01.png",
      "media_credit": "Autor X, Wikimedia Commons, CC BY-SA 4.0",
      "source": "Diretriz ACC/AHA/HRS de bradicardia e distúrbios de condução",
      "source_year": "2018",
      "tags": ["Clinica_Medica::Cardiologia::Bradiarritmias"]
    },
    {
      "type": "atomic",
      "front": "Qual o achado nesta ausculta em foco aórtico?",
      "back": "Sopro sistólico ejetivo em crescendo-decrescendo (estenose aórtica)",
      "audio_front": "midia/ausculta_01.mp3",
      "media_credit": "Autor Y, site Z, licença W",
      "source": "Diretriz ACC/AHA de valvopatias",
      "source_year": "2020",
      "tags": ["Clinica_Medica::Cardiologia::Valvopatias"]
    },
    {
      "type": "image_occlusion",
      "image": "midia/rx_torax_pa.png",
      "header": "Radiografia de tórax em incidência posteroanterior (PA): qual estrutura está coberta?",
      "mode": "hide_one",
      "occlusions": [
        {"answer": "Botão aórtico", "box": [0.67, 0.19, 0.12, 0.04]},
        {"answer": "Átrio direito", "box": [0.02, 0.58, 0.14, 0.04]}
      ],
      "source": "Felson's Principles of Chest Roentgenology (livro-texto)",
      "media_credit": "Autor, site e licença da imagem",
      "tags": ["Clinica_Medica::Radiologia::Radiografia_de_Torax"]
    }
  ]
}
```

### 2.2. Comando para Executar o Gerador

O caminho do script depende da ferramenta onde a skill está instalada (use a pasta base da skill informada ao carregá-la):
* **Claude Code:** `C:\Users\joaop\.claude\skills\anki-medical-flashcards\scripts\generate_apkg.py`
* **Antigravity:** `C:\Users\joaop\.gemini\config\skills\anki-medical-flashcards\scripts\generate_apkg.py`

```powershell
python "<pasta da skill>\scripts\generate_apkg.py" --input "caminho/para/cards.json" --output "caminho/para/deck.apkg"
```

> **Nota Técnica:** O script `generate_apkg.py` cria os 5 Note Types (1 a 4 na versão v2, com campos `Source` e `Year`; 5 = Oclusão de Imagem) e empacota as imagens e áudios no banco de dados interno do Anki (`collection.anki2`). O Note Type Cloze usa o tipo Cloze nativo do Anki, mas **esta skill usa somente `{{c1::...}}`**: o script recusa `c2`, `c3` etc. (1 nota = 1 card).
>
> **Testes:** na pasta da skill, rode `python -m unittest discover -s tests -v`. Rode sempre depois de alterar o script.
