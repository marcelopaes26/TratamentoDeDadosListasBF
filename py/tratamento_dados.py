import pandas as pd
import re

# Diretório da planilha a ser trabalhada
planilha = 'C:/Users/diego.pissetti/Documents/Marcelo/Python/TratamentoDeDadosListasBF/planilhas/Lembrete Cobrança Venc 10 - Copia.xlsx'

# Força leitura de colunas como texto para evitar notação científica
colunas_texto = ['CPF_CNPJ', 'DDD', 'Fone 1', 'Fone 2', 'Fone 3', 'TELEFONE']
df_original = pd.read_excel(planilha, sheet_name=None, dtype={col: str for col in colunas_texto})

# Fazer uma cópia da aba Base 10 para tratar
df_tratados = df_original['Base 10'].copy()

# Fazer uma cópia da aba Black para remover os telefones
df_black = df_original['Black'].copy()

# Fazer uma cópia da aba Judicial para remover os contratos
df_judicial = df_original['Judicial'].copy()

def limpar_ddd(ddd):
    if pd.isna(ddd):
        return ''
    return re.sub(r'/D','', ddd).zfill(2)

def limpar_fone(fone, ddd):
    if pd.isna(fone):
        return ''
    fone = ''.join(filter(str.isdigit, str(fone)))

    if len(fone) == 9:
        # Celular sem DDD
        return f'{ddd}{fone}'

    elif len(fone) == 8:
        # Pode ser fixo ou celular antigo sem o 9º dígito
        # Se não começa com 2, 3, 4 ou 5, é provavelmente celular antigo - adiciona o 9
        if fone[0] not in '2345':
            return f'{ddd}9{fone}' # celular antigo, adiciona o 9

    elif len(fone) == 11:
        # Já tem DDD, retorna como está
        # Caso o DDD iniciar com 0 e não ter o dígito 9, será feita a seguinte validação:
        if (fone.startswith('0')):
            return f'{fone[1:]}9{fone[2:]}'
        return f'{fone}'

    elif len(fone) == 10:
        # Número com DDD mas sem 9º dígito
        if fone[2] not in '2345':
          return f'{fone[:2]}9{fone[2:]}'

    elif len(fone) == 12:
        # Número com DDD iniciando em zero e com o 9º dígito
        if fone.startswith('0'):
          return f'{fone[1:]}'

    return '' # ignora fixo com DDD

def is_celular(numero):
    # Considera celular somente se tiver 11 dígitos e o 3º for 9
    return numero and len(numero) == 11 and numero[2] == '9'

def selecionar_telefone(ddd, f1, f2, f3):
    ddd = ''.join(filter(str.isdigit, str(ddd))) if pd.notna(ddd) else ''
    fones = [f1, f2, f3]

    # Tenta retornar celular válido
    for f in fones:
        f_limpo = limpar_fone(f, ddd)
        if is_celular(f_limpo):
            return f_limpo

    # Se não tiver celular, retorna em branco
    return ''

# Extrai os primeiros 8 dígitos do Nome Agente, os quais são o Código Carteira
# OBS: não está sendo usada no momento, mas pode ser útil em algumas situações
def extrai_cod_carteira(nome_agente):
  if (pd.isna(nome_agente)):
    return ''
  return f'{nome_agente[:8]}'

# Remove números, pontos e espaços antes do nome do cliente
def limpar_nome(nome):
  if (pd.isna(nome)):
    return ''
  # Remove tudo o que não for letra no início e final da string
  return re.sub(r'^[^a-zA-Z]+|[^a-zA-Z]+$', '', nome)

# Aplicar a remoção de contratos que estão na Judicial
df_tratados = df_tratados[~df_tratados['Contrato'].isin(df_judicial['CONTRATO'])]

# Chama a função limpar_nome() no Data Frame
df_tratados['NOME'] = df_tratados['Nome Cliente'].apply(limpar_nome)

# Chama a função selecionar_telefone() no Data Frame
df_tratados['FONES'] = df_tratados.apply(
    lambda row: selecionar_telefone(row['DDD'], row['Fone 1'], row['Fone 2'], row['Fone 3']),
    axis=1
)

# Remover vazios da coluna FONES
df_tratados = df_tratados[df_tratados['FONES'].str.strip() != '']

# Renomear as colunas Regional, Unidade, Cód. Carteira e Vlr Emprestado
df_tratados = df_tratados.rename(columns={
    'Regional': 'REGIONAL',
    'Unidade': 'UNIDADE',
    'Código Carteira': 'CÓD. CARTEIRA',
    'Vlr Carteira Ativa': 'VLR'
}).copy()

# Aplicar a remoção de telefones que estão na Black
df_tratados = df_tratados[~df_tratados['FONES'].isin(df_black['TELEFONE'])]

# Agrupar por FONES (caso tenha cliente duplicado com o mesmo número de telefone)
# e somar o valor emprestado
df_tratados = df_tratados.groupby('FONES', as_index=False).agg({
    'REGIONAL': 'first',
    'UNIDADE': 'first',
    'CÓD. CARTEIRA': 'first',
    'VLR': 'sum',
    'NOME': 'first',
    'FONES': 'first'
})

# Colunas ordenadas
df_tratados = df_tratados[['REGIONAL', 'UNIDADE', 'CÓD. CARTEIRA', 'VLR', 'NOME', 'FONES']]

# Adicionar a nova aba Envio MKT na planilha original
df_original['Envio MKT'] = df_tratados

# Salvar resultado com todas as abas na mesma planilha
with pd.ExcelWriter(planilha, engine='openpyxl', mode='w') as writer:
    for aba, df in df_original.items():
       df.to_excel(writer, sheet_name=aba, index=False)

print(f'Planilha salva em: {planilha}')
