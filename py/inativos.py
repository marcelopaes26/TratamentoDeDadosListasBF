import pandas as pd
import re

# Diretório da planilha a ser trabalhada
origem = 'C:/Users/diego.pissetti/Documents/Marcelo/Python/TratamentoDeDadosListasBF/origem/Inativos 08-2025.xlsx'
destino = 'C:/Users/diego.pissetti/Documents/Marcelo/Python/TratamentoDeDadosListasBF/destino/Inativos 08-2025.xlsx'

# Força leitura de colunas como texto para evitar notação científica
colunas_texto = ['CPF_CNPJ', 'DDD', 'Fone 1', 'Fone 2', 'Fone 3', 'Fone 4', 'TELEFONE', 'Contrato', 'CONTRATO']
df_original = pd.read_excel(origem, sheet_name=None, dtype={col: str for col in colunas_texto})

# Fazer uma cópia da aba Base para tratar
df_tratados = df_original['Base'].copy()

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

def selecionar_telefone(ddd, f1, f2, f3, f4):
    ddd = ''.join(filter(str.isdigit, str(ddd))) if pd.notna(ddd) else ''
    fones = [f1, f2, f3, f4]

    # Tenta retornar celular válido
    for f in fones:
        f_limpo = limpar_fone(f, ddd)
        if is_celular(f_limpo):
            return f_limpo

    # Se não tiver celular, retorna em branco
    return ''

# Remove números, pontos e espaços antes do nome do cliente
def limpar_nome(nome):
  if (pd.isna(nome)):
    return ''
  # Remove tudo o que não for letra no início e final da string
  return re.sub(r'^[^a-zA-Z]+|[^a-zA-Z]+$', '', nome)

# Retirar os contratos de Óbito (Carteira Sede)
df_tratados = df_tratados[~df_tratados['Cód. Carteira'].isin(['BF-SEDE'])]

# Aplicar a remoção de contratos que estão na Judicial
df_tratados = df_tratados[~df_tratados['Contrato'].isin(df_judicial['CONTRATO'])]

# Chama a função selecionar_telefone() no Data Frame
df_tratados['FONES'] = df_tratados.apply(
    lambda row: selecionar_telefone(row['DDD'], row['Fone 1'], row['Fone 2'], row['Fone 3'], row['Fone 4']),
    axis=1
)

# Remover vazios da coluna FONES
df_tratados = df_tratados[df_tratados['FONES'].str.strip() != '']

# Renomear as colunas Regional, Unidade, Cód. Carteira e Vlr Carteira Ativa
df_tratados = df_tratados.rename(columns={
    'Regional': 'REGIONAL',
    'Unidade': 'UNIDADE',
    'Cód. Carteira': 'CÓD. CARTEIRA',
    'Contrato': 'CONTRATO',
    'Vlr Emprestado': 'VLR'
}).copy()

# Aplicar a remoção de telefones que estão na Black
df_tratados = df_tratados[~df_tratados['FONES'].isin(df_black['TELEFONE'])]

# Chama a função limpar_nome() no Data Frame
df_tratados['NOME'] = df_tratados['Nome'].apply(limpar_nome)

# Agrupar por FONES (caso tenha cliente duplicado com o mesmo número de telefone)
# e somar o valor emprestado e carteira ativa
df_tratados = df_tratados.groupby('FONES', as_index=False).agg({
    'REGIONAL': 'first',
    'UNIDADE': 'first',
    'CÓD. CARTEIRA': 'first',
    'CONTRATO': 'first',
    'NOME': 'first',
    'VLR': 'sum'
})

# Colunas ordenadas
df_tratados = df_tratados[['REGIONAL', 'UNIDADE', 'CÓD. CARTEIRA', 'CONTRATO', 'NOME', 'VLR', 'FONES']]

# Ordenar pelos 1000 primeiros registros com o maior valor para LGS e CTB 
# (Isso funciona, pois as outras regionais estão com registros menor que 1000)
# df_tratados = df_tratados.groupby('REGIONAL', group_keys=False).apply(lambda x: x.nlargest(1000, 'VLR'))

# Adicionar a nova aba Envio MKT na planilha original
df_original['Envio MKT'] = df_tratados

print("Processando...")

# Salvar resultado com todas as abas na mesma planilha
with pd.ExcelWriter(destino, engine='openpyxl', mode='w') as writer:
    for aba, df in df_original.items():
       df.to_excel(writer, sheet_name=aba, index=False)

print(f'Planilha salva em: {destino}')
