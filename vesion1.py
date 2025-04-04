import flet as ft
import re

def tratar_dados(e, origem_field, dados_tratados):
    dados_tratados.value = ''
    dados_tratados.update()
    
    textos = origem_field.value.split('\r\n')  # Divide o texto em um alista de string, com base nas quebras de linhas

    bancos = [
        "Bradesco", "Brasil", "Itaú", "Itau", "CEF", "Nubank", "Santander", "Basa", 
        "Banco do Brasil", "Banco Safra", "Caixa Econômica", "Banrisul", "Banestes", 
        "Banco Original", "BTG", "XP Investimentos", "Neon", "C6 Bank", "XP", "C6",
        "Caixa Economica", 'PIX', 'Sicredi', r'C6 \(336\)'
    ] #Lista de bancos
    
    bancos_regex = "|".join(bancos) #Cria um expressão com todo os bancos, separados por "|"

    padrao = re.compile(
        rf"(?P<banco>{bancos_regex})\s*(?:\(\d+\))?\s*" #Captura o nome do banco usando a lista bancos_regex
        r"(?P<nome>[A-Za-zÀ-ÖØ-öø-ÿ\s\.\-]+?)\s+PIX\s+" #Captura o nome da pessoa, descartando a palavra PIX
        r"(?:CPF\s*(?P<cpf>[\d\.\-]+)|" 
        r"Email\s*(?P<email>[\w.\-]+@[\w.\-]+)|"
        r"Fone\s*(?P<fone>\+?[\d\s()\-]+))?\s+"
        r"(?:AG\s*(?P<agencia>[\d\-A-Za-z]+))?\s*"
        r"(?:C[\/\s]?(?:C|POUP|C/C|CC|CPOUP)\s*(?P<conta>[\w.\-]+))?\s*"
        r"R\$\s*(?P<valor>\d{1,3}(?:[\.,]\d{3})*[\.,]\d{2})",
        flags=re.IGNORECASE
    )

    def extrair_dados(texto):
        matches = padrao.finditer(texto) #Converte os grupos nomeados em um dicioná
        resultados = []  
        total_valor = 0  
        total_contas = 0  

        for match in matches:
            dados = match.groupdict()
            banco = dados['banco'] or 'Não informada'
            chave_pix = dados['cpf'] if dados['cpf'] else (dados['email'] if dados['email'] else dados['fone'] or 'Não informado')
            agencia = dados['agencia'] or 'Não informada'
            conta = dados['conta'] or 'Não informada'
            
            try:
                valor_corrigido = dados['valor']
                if re.search(r'\d{1,3}\.(\d{3}\.)*\d{2}', valor_corrigido):
                    valor_corrigido = re.sub(r'(\d)\.(\d{3})\.', r'\1\2.', valor_corrigido)
                valor = float(valor_corrigido.replace(',', '.'))
                valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                total_valor += valor
            except ValueError:
                valor_formatado = dados['valor']  

            resultado = {
                "Banco": banco,
                "Nome": dados['nome'].replace('PIX' or 'pix', '').strip(),
                "Chave Pix": chave_pix,
                "Agência": agencia,
                "Conta": conta,
                "Valor (R$)": valor_formatado
            }
            resultados.append(resultado)
            total_contas += 1

        valor_total_formatado = f"R$ {total_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return resultados, valor_total_formatado, total_contas  

    def testar_extracao(textos):
        resultados = []
        dados_tratados.value = ""
        total_valor = 0.0
        total_contas = 0

        for texto in textos:
            res, valor_total, contas = extrair_dados(texto)
            resultados.extend(res)

            # Garantindo que valor_total seja sempre um número antes de somar
            try:
                valor_total = float(str(valor_total).replace('R$ ', '').replace('.', '').replace(',', '.'))
            except ValueError:
                valor_total = 0.0  # Se houver erro, evitar quebra do código

            total_valor += valor_total
            total_contas += contas

        for res in resultados:
            dados_formatados = "\n".join([f"{key}: {value}" for key, value in res.items()])
            dados_tratados.value += f"{dados_formatados}\n{'-'*40}\n"

        # Formatar corretamente o valor total antes de exibir
        valor_total_formatado = f"R$ {total_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        dados_tratados.value += f"\nContas Pix: {total_contas}\n"
        dados_tratados.update()
        
    testar_extracao(textos)
    
# Função para limpar os dados (limpa os campos de texto)
def limpar_dados(e, origem_field, dados_tratados):
    origem_field.value = ""  # Limpa o campo de origem
    dados_tratados.value = ""  # Limpa o campo de dados tratados
    origem_field.update()  # Atualiza o campo origem
    dados_tratados.update()  # Atualiza o campo de dados tratados

# Função para a interface do usuário
def main(page: ft.Page):
    global origem_field, dados_tratados

    # Função para copiar os dados tratados para a área de transferência
    def copiar_para_area_de_transferencia(e):
        page.set_clipboard(dados_tratados.value)  # Copia os dados para a área de transferência
        page.open(ft.SnackBar(ft.Text("Dados copiados com sucesso!"), duration=2000))  # Exibe uma notificação
        page.update()

    # Configuração inicial da página
    page.window.width = 800
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.LIGHT  # Tema claro
    page.padding = 30
    page.window.resizable = False  # Não permite redimensionamento
    page.title = 'Pix Organiza'  # Título da página

    # Definição dos campos de texto
    origem_field = ft.TextField(
        label="Digite os dados a serem tratados",
        width=680,
        bgcolor=ft.colors.GREY_100,
        border_radius=20,
        focused_border_color='2196F3',
        expand=True
    )

    dados_tratados = ft.TextField(
        label="Dados tratados",
        multiline=True,
        expand=True,
        bgcolor=ft.colors.GREY_100,
        border_radius=20,
        focused_border_color="#2196F3",
        disabled=False,
        read_only=True,
    )

    # Botões de ação
    btn_copiar_dados = ft.TextButton(
        text='Copiar Dados',
        icon=ft.icons.COPY,
        icon_color=ft.colors.WHITE,
        tooltip='Copiar Dados',
        width=200,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.BLUE_300,
            color=ft.colors.WHITE,
        ),
        on_click=copiar_para_area_de_transferencia  # Ação de copiar os dados
    )

    btn_limpar_dados = ft.TextButton(
        text='Limpar Dados',
        icon=ft.icons.DELETE_OUTLINE,
        icon_color=ft.colors.WHITE,
        tooltip='Limpar Dados',
        width=200,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
        ),
       on_click=lambda e: limpar_dados(e, origem_field, dados_tratados)  # Ação de limpar os dados
    )

    btn_tratar_dados = ft.TextButton(
        text='Tratar os Dados',
        icon=ft.icons.FORMAT_LIST_BULLETED,
        icon_color=ft.colors.WHITE,
        tooltip='Tratar Dados',
        width=200,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
        ),
        on_click=lambda e: tratar_dados(e, origem_field, dados_tratados)  # Ação de tratar os dados
    )
    
    # Adicionando os controles à página
    page.add(
        ft.Column(
            controls=[ 
                ft.Text("Organizador de Pix", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_600),
                ft.Divider(),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text('Dados Tratados', size=16, weight=ft.FontWeight.BOLD),
                            ft.Row([origem_field], alignment=ft.MainAxisAlignment.START),
                        ],
                        spacing=10
                    ),
                    padding=20,
                    border_radius=20,
                    bgcolor=ft.colors.GREY_50,
                    shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.GREY_400)
                ),
            ]
        ),
        ft.Column(
            controls=[
                ft.Divider(),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text('Dados das Transações', size=16, weight=ft.FontWeight.BOLD),
                            dados_tratados,  # Exibe os dados tratados
                        ],
                        spacing=10,
                        expand=True,
                    ),
                    padding=20,
                    border_radius=20,
                    bgcolor=ft.colors.GREY_50,
                    shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.GREY_400),
                    expand=True,
                ),
            ],
            expand=True,
        ),
        ft.Row([btn_tratar_dados, btn_limpar_dados, btn_copiar_dados ], alignment=ft.MainAxisAlignment.END)
    )

    page.update()

# Iniciar o app
ft.app(target=main)
