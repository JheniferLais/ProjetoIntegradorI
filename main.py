import os
import oracledb

# Limpando informações remanescentes do terminal...
os.system('cls')

# Configurando o acesso ao Banco de Dados...
connection = oracledb.connect(user="SYSTEM", password="123456", dsn="localhost:1521/xe")
cursor = connection.cursor()

# Configurando o alfanumerio e as chaves para criptografia e descriptografia...
alfanumerico = 'zabcdefghijklmnopqrstuvwxy'
chave_cripto = [[4, 3], [1, 2]]
chave_descripto = [[42, -63], [-21, 84]]

#----------------------------------------------------------------------------------------

# Função para criptografar/descriptografar...
def hill_criptografia(desc_prod, chave):

    # Converte a descrição em índices numéricos do alfabeto...
    index = []
    for letra in desc_prod:
        if letra in alfanumerico:
            index.append(alfanumerico.index(letra))

    # Valida se a descrição é par
    if len(index) % 2 != 0:
        index.append(index[-1])

    resultado = ''
    # Processa os índices em pares efetua a multipliação e aplica a criptografia
    for i in range(0, len(index), 2):
        resultado += (alfanumerico[(chave[0][0] * index[i] + chave[0][1] * index[i + 1]) % 26] +
                      alfanumerico[(chave[1][0] * index[i] + chave[1][1] * index[i + 1]) % 26])

    return resultado

# Função para calcular a tabela do produto e mostra-la...
def calculo_print_tabela(cod_prod, nome_prod, desc_prod, cp, cf, cv, iv, ml):

    # Calcula o valor de venda do produto...
    pv = cp / (1 - ((cf + cv + iv + ml) / 100))

    # Calcula os outros custos...
    oc_por = cf + cv + iv  # Outros custos '%'
    cf_num = (pv * cf) / 100  # Custo fixo 'valor'
    cv_num = (pv * cv) / 100  # Comissão 'valor'
    iv_num = (pv * iv) / 100  # Impostos 'valor'
    oc_num = cf_num + cv_num + iv_num  # Outros custos 'valor'
    rb_num = pv - cp  # Receita bruta 'valor'
    r_num  = rb_num - oc_num  # Rentabilidade 'valor'
    cp_por = (cp * 100) / pv  # Custo do produto '%'
    rb_por = 100 - cp_por  # Receita bruta '%'
    r_por = rb_por - oc_por  # Rentabilidade '%'

    # Classifica a tipo de lucro...
    if r_por > 20:
        class_lucro = 'Lucro Alto'
    elif 10 <= r_por <= 20:
        class_lucro = 'Lucro Médio'
    elif 0 < r_por < 10:
        class_lucro = 'Lucro Baixo'
    elif r_por == 0:
        class_lucro = 'Equilíbrio'
    else:
        class_lucro = 'Prejuízo'

    # Printa no terminal as informações do produto
    print(f'''                      
=====================================================
 Código: {cod_prod:<20}               
 Produto: {nome_prod:<30}
 Descrição: {desc_prod:<40}                    
=====================================================
¦ Preço de Venda            ¦ R${pv:<10.2f} ¦ {100:<5}% ¦
¦ Custo de Aquisição        ¦ R${cp:<10.2f} ¦ {cp_por:<5.0f}% ¦
¦ Receita Bruta             ¦ R${rb_num:<10.2f} ¦ {rb_por:<5.0f}% ¦
¦ Custo Fixo/Administrativo ¦ R${cf_num:<10.2f} ¦ {cf:<5.0f}% ¦
¦ Comissão de Vendas        ¦ R${cv_num:<10.2f} ¦ {cv:<5.0f}% ¦
¦ Impostos                  ¦ R${iv_num:<10.2f} ¦ {iv:<5.0f}% ¦
¦ Outros Custos             ¦ R${oc_num:<10.2f} ¦ {oc_por:<5.0f}% ¦
¦ Rentabilidade             ¦ R${r_num:<10.2f} ¦ {r_por:<5.0f}% ¦
=====================================================
 Classificação de Lucro:  {class_lucro:<20}
=====================================================''')

# Funções CRUD do sistema...
def cadastrar_produto():

    # Pede ao usuario o codigo do produto...
    cod_prod = int(input('Código do produto: '))

    # Valida se o codigo já está cadastrado...
    cursor.execute(f'SELECT * FROM ESTOQUE WHERE COD_PROD = {cod_prod}')
    cod = cursor.fetchone()
    if cod:
        print('\n--->>> Código inválido! <<<---')
        return

    # Inicia o cadastro do produto...
    nome_prod = str(input('Nome do produto: '))              # Nome do produto
    desc_prod = str(input('Descrição do produto: ')).lower() # Descrição do produto
    cp = float(input('Custo de aquisição do produto: '))     # Custo do produto pago ao fornecedor
    cf = float(input('Custo fixo/administrativo(%): '))      # Custo fixo (espaço físico, despesas, funcionarios...)
    cv = float(input('Comissão de vendas(%): '))             # Comissão sobre a venda do produto
    iv = float(input('Impostos(%): '))                       # Impostos sobre a venda do produto
    ml = float(input('Margem de lucro do produto(%): '))     # Margem de lucro sobre a venda do produto

    # Calcula as informações do produto e mostra na tela...
    calculo_print_tabela(cod_prod, nome_prod, desc_prod, cp, cf, cv, iv, ml)

    # Criptografa a descrição do produto...
    desc_cripto = hill_criptografia(desc_prod, chave_cripto)

    # Insere o produto no Banco de Dados...
    cursor.execute(f"INSERT INTO estoque VALUES ({cod_prod}, '{nome_prod}', '{desc_cripto}', {cp}, {cf}, {cv}, {iv}, {ml})")
    connection.commit()
    print('\n--->>> PRODUTO CADASTRADO COM SUCESSO!!! <<<---')
def alterar_produto():

    # Pede ao usuario o codigo do produto...
    cod_prod = int(input('Código do produto: '))

    # Valida se o codigo não está cadastrado...
    cursor.execute(f'SELECT * FROM ESTOQUE WHERE COD_PROD = {cod_prod}')
    produto = cursor.fetchone()
    if not produto:
        print('\n--->>> Código inválido! <<<---')
        return

    # Print do menu de alteração...
    menu_alteracao = int(input('''
===================================================
¦    Qual informação do produto deseja alterar:   ¦
===================================================
¦ [1].Nome do produto    ¦ [5].Custo fixo         ¦
¦ [2].Descrição          ¦ [6].Comissão de vendas ¦
¦ [3].Custo do produto   ¦ [7].Impostos           ¦
¦ [4].Margem de lucro    ¦                        ¦
===================================================
Opção: '''))

    # Escolha da alteração
    alteracao = str(input('Nova informação para do produto: '))

    # Classifica a alteração escolhida e a da nome a coluna..
    if menu_alteracao == 1:
        coluna = 'nome_prod'
    elif menu_alteracao == 2:
        alteracao = hill_criptografia(alteracao, chave_cripto)
        coluna = 'desc_prod'
    elif menu_alteracao == 3:
        coluna = 'cp'
    elif menu_alteracao == 4:
        coluna = 'ml'
    elif menu_alteracao == 5:
        coluna = 'cf'
    elif menu_alteracao == 6:
        coluna = 'cv'
    elif menu_alteracao == 7:
        coluna = 'iv'
    else:
        print('\n--->>> Opção inválida! <<<---')
        return

    # Realiza a alteração no Banco de Ddados...
    cursor.execute(f"UPDATE estoque SET {coluna} = '{alteracao}' WHERE cod_prod = {cod_prod}")
    connection.commit()
    print('\n--->>> Produto alterado com sucesso! <<<---')
def apagar_produto():

    # Pede ao usuario o codigo do produto...
    cod_prod = int(input('Código do produto: '))

    # Valida se o codigo não está cadastrado...
    cursor.execute(f'SELECT * FROM ESTOQUE WHERE COD_PROD = {cod_prod}')
    estoque = cursor.fetchone()
    if not estoque:
        print('\n--->>> Código inválido! <<<---')
        return

    # Mostra o produto que o usuario escolheu excluir...
    cod_prod, nome_prod, desc_cripto, cp, cf, cv, iv, ml = estoque
    desc_prod = hill_criptografia(desc_cripto, chave_descripto)
    calculo_print_tabela(cod_prod, nome_prod, desc_prod, cp, cf, cv, iv, ml)

    # Pede a confirmação para exclusão...
    confirmacao = str(input('Confirmar a exclusão do produto <s/n>: ')).lower()
    if confirmacao != 's':
        print('\n--->>> Nenhum produto excluído! <<<---')
        return
    #
    cursor.execute(f'DELETE FROM ESTOQUE WHERE COD_PROD = {cod_prod}')
    connection.commit()
    print('\n--->>> Produto excluído com sucesso! <<<---')
def mostrar_estoque():

    # Valida se existe algum produto cadastrado...
    cursor.execute('SELECT * FROM ESTOQUE ORDER BY COD_PROD ASC')
    estoque = cursor.fetchall()
    if not estoque:
        print('\n--->>> Nenhum produto cadastrado! <<<---')
        return

    # Mostra o estoque completo de produtos...
    print('\n--->>> Estoque completo de produtos! <<<---')
    for item in estoque:
        cod_prod, nome_prod, desc_cripto, cp, cf, cv, iv, ml = item
        desc_prod = hill_criptografia(desc_cripto, chave_descripto)
        calculo_print_tabela(cod_prod, nome_prod, desc_prod, cp, cf, cv, iv, ml)

# Print do menu principal...
def print_menu():
    print('''
===================================================
¦        SISTEMA DE CONTROLE DE ESTOQUE!          ¦
===================================================
¦ [1].Cadastrar Produto                           ¦
¦ [2].Alterar Produto                             ¦
¦ [3].Apagar Produto                              ¦
¦ [4].Mostrar Estoque                             ¦
¦ [0].Sair                                        ¦
===================================================''')

#----------------------------------------------------------------------------------------

# Pede ao usuario qual operação deseja realizar...
print_menu()
menu = int(input('Opção: '))
os.system('cls')

# Laço de repetição para a interação do sistema...
while menu != 0:
    if menu == 1:   # Cadastrar produto
        cadastrar_produto()
    elif menu == 2: # Alterar produto
        alterar_produto()
    elif menu == 3: # Apagar produto
        apagar_produto()
    elif menu == 4: # Mostrar produto
        mostrar_estoque()
    else:
        print('\n--->>> Opção invalida! <<<---')

    # Pede novamente ao usuario qual operação deseja realizar...
    print_menu()
    menu = int(input('Opção: '))
    os.system('cls')

# Finalizando o uso do sistema...
print('\n--->>> Obrigada por utilizar o sistema :) <<<---')
cursor.close()
connection.close()