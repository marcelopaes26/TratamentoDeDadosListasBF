# Tratamento de Dados – Listas BF

Scripts em Python para **tratamento e padronização de dados** das listas de clientes do Banco da Família, com foco em **nomes** e **telefones** para campanhas de disparos via **Tallos**.  
Cada script da pasta [`py/`](./py) atende **uma campanha específica** (regras pontuais), mas todos seguem a **mesma base de processamento**.

---

## 🧭 Visão Geral do Fluxo

1. **Entrada**: planilha Excel (`.xlsx`) com a aba **`Base`** (**obrigatória** – exportada diretamente do Power BI).  
   Opcionalmente, podem existir as abas **`Black`** e **`Judicial`**:
   - **`Black`**: lista de clientes que **não desejam mais receber contato**, números inválidos ou desatualizados. Usada para exclusão total dos registros correspondentes.
   - **`Judicial`**: contratos de clientes **em processo judicial** (usada para exclusões quando a campanha é de cobrança).
2. **Tratamento comum** (em todos os scripts):
   - Leitura forçada de colunas como **texto** (evita notação científica/zeros à esquerda).
   - **Normalização de telefones** (celular válido com 11 dígitos e dígito 9 na 3ª posição).
   - Limpeza de **nomes** (remoção de caracteres/resíduos).
   - **Deduplicação** por cliente (geralmente por `CPF_CNPJ`) e/ou telefone conforme a campanha.
   - Reordenação/renomeação de colunas para a saída.
3. **Regras específicas por campanha** (variam de script para script), por exemplo:
   - **Exclusões**: registros com bloqueio em `Black` e/ou `Judicial`.
   - **Segmentos/Produtos**: filtros como remover **`BF CONVÊNIO`** ou lidar com carteiras como **`BF-SEDE`** (com exceções como `BF-SEDE1`, `BF-SEDE3` quando aplicável).
   - **Faixas e status**: seleção por *Mora* (0–30 dias) vs. *Risco* (>30 dias), valores, regionais, etc.
4. **Saída**: mantém todas as abas originais e cria a aba **`Envio MKT`** com os dados tratados e prontos para o Tallos.

---

## 📂 Estrutura do Repositório

```
/
├─ py/                  # scripts por campanha (mesma base, regras pontuais)
├─ README.md
└─ .gitignore
```

> Cada arquivo dentro de `py/` foca em **um tipo de campanha** (ex.: cobrança, inativos, risco até X, etc.), reaproveitando o pipeline comum e ajustando **apenas as regras necessárias** daquela operação.

---

## ⚙️ Funcionalidades (base comum)

- Leitura de colunas sensíveis como **texto** (evita perda de zeros/formatos).
- **Validação/normalização de telefones**:
  - Telefones com 9 dígitos → assume celular; garante DDD; exige 11 dígitos no final.
  - Telefones com 8 dígitos → trata como fixo/celular antigo; aplica regra de nono dígito quando aplicável.
  - Telefones com 10–12 dígitos → normaliza formatos com/sem DDD e com/sem dígito 9.
  - Mantém **somente celulares válidos** (11 dígitos e dígito 9 na 3ª posição).
- Limpeza de **nomes** (remoção de caracteres espúrios no início/fim).
- **Deduplicação** (por `CPF_CNPJ` e/ou telefone, conforme a campanha).
- **Saída padronizada** na aba `Envio MKT`.

---

## 📑 Estrutura esperada da planilha

**Abas:**
- `Base` (**obrigatória** – exportada do Power BI)
- `Black` (opcional – blacklist: clientes que não querem mais contato ou números inválidos)
- `Judicial` (opcional – clientes já em processo judicial, usado em campanhas de cobrança)

**Colunas mínimas em `Base`:**
- `CPF_CNPJ`
- `DDD`
- `Fone 1`, `Fone 2`, `Fone 3`
- `Nome Cliente`
- `Regional`, `Unidade`, `Código Carteira`, `Vlr Carteira Ativa`

---

## 🧪 Regras específicas por campanha (exemplos)

| Tema | Exemplos de variações por campanha |
|---|---|
| **Segmentação** | Somente *Mora* (0–30 dias) ou somente *Risco* (>30 dias); faixa de valor (ex.: Risco até 5.000) |
| **Exclusões** | Remover presentes em `Black` e/ou `Judicial`; excluir `Produto = BF CONVÊNIO`; tratar `Cód. Carteira = BF-SEDE` com exceções (`BF-SEDE1`, `BF-SEDE3`) |
| **Deduplicação** | Priorizar `CPF_CNPJ` (consolidação de valores) vs. priorizar **telefone único** para disparo |
| **Telefones** | Regras estritas de celular (11 dígitos, dígito 9 na 3ª posição); DDD obrigatório |
| **Ordenação/Prioridade** | Por valor, por regional/unidade, por situação (Mora/Risco) |

---

## ▶️ Como usar

1. **Escolha o script** em `py/` que corresponde à campanha que você vai rodar.
2. Abra o arquivo e ajuste a variável/caminho da **planilha** de entrada (aba `Base`).
3. Execute:

```bash
python py/nome_do_script.py
```

4. Ao final, o arquivo original é salvo **junto com a nova aba** `Envio MKT` (sem perder as abas originais).

---

## 📦 Dependências

- `pandas`
- `openpyxl`
- (módulos da biblioteca padrão, como `re`)

Instalação rápida:

```bash
pip install pandas openpyxl
```

---

## ✅ Saída (aba `Envio MKT`)

Colunas usuais na saída (podem variar minimamente conforme a campanha):

- `REGIONAL`
- `UNIDADE`
- `CÓD. CARTEIRA`
- `VLR`
- `NOME`
- `FONES` (apenas **celulares válidos**)

---

## 🧰 Boas práticas & observações

- **Valide a qualidade** de `DDD` e dos `Fone 1–3` para maximizar taxa de contatos válidos.
- Mantenha as abas `Black`/`Judicial` **atualizadas** (exclusões confiáveis reduzem retrabalho e ruído nos disparos).
- Se possível, **versione** os arquivos de entrada (backup) antes de rodar os tratamentos.

## 🛠️ Tecnologias Utilizadas
[![My Skills](https://skillicons.dev/icons?i=py,git,github,vscode)](https://skillicons.dev)
