
# 📊 Tratamento de Dados - Lista de Cobrança

Este script em Python realiza o tratamento e padronização de dados de uma planilha Excel contendo listas de cobrança de aposentados. Ele processa a aba `Export`, realiza limpeza e normalização de colunas como telefones e nomes, e salva o resultado final em uma nova aba chamada `Envio MKT`, mantendo todas as abas originais da planilha.

---

## ⚙️ Funcionalidades

- Força a leitura de colunas como texto para evitar notação científica e perda de zeros à esquerda.
- Normaliza e formata números de telefone (com regras específicas para celulares e DDDs).
- Remove caracteres indesejados no início/final do nome do cliente.
- Agrupa registros duplicados pelo CPF/CNPJ, somando valores financeiros.
- Renomeia e reordena colunas para facilitar o uso em campanhas de marketing.
- Salva a planilha com todas as abas originais mais uma aba nova com os dados tratados.

---

## 📁 Estrutura Esperada da Planilha

A planilha original deve conter ao menos as seguintes abas:

- `Export` (obrigatória – é a única aba tratada)
- `Black`
- `Judicial`

As colunas mínimas necessárias na aba `Export` são:
- `CPF_CNPJ`
- `DDD`
- `Fone 1`, `Fone 2`, `Fone 3`
- `Nome Cliente`
- `Regional`, `Unidade`, `Código Carteira`, `Vlr Carteira Ativa`

---

## 📌 Regras de Tratamento de Telefones

- Telefones com 8 dígitos: assume fixo ou celular antigo, adicionando o nono dígito se necessário.
- Telefones com 9 dígitos: assume celular e adiciona DDD.
- Telefones com 10 a 12 dígitos: trata diferentes formatos com ou sem DDD, com ou sem dígito 9.
- Apenas números celulares válidos (com 11 dígitos e dígito 9 na 3ª posição) são considerados.
- Telefones inválidos ou não celulares são descartados.

---

## 💾 Como Usar

1. Altere a variável `planilha` no início do script para o caminho completo da sua planilha `.xlsx`.
2. Execute o script:
```bash
python nome_do_arquivo.py
```
3. Ao final, a planilha será salva no mesmo caminho com todas as abas originais mais a nova aba `Envio MKT`.

---

## 🧰 Dependências

- pandas
- openpyxl
- re (builtin)

Instale as dependências com:
```bash
pip install pandas openpyxl
```

---

## ✅ Resultado

A planilha final conterá:

- Abas originais: `Export`, `Black`, `Judicial`
- Aba nova: `Envio MKT`, com as colunas:
  - `REGIONAL`
  - `UNIDADE`
  - `CÓD. CARTEIRA`
  - `VLR`
  - `NOME`
  - `FONES` (apenas celulares válidos)

---
