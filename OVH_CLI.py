import typer
import csv
import ovh
from dynaconf import Dynaconf
from ovh.exceptions import ResourceNotFoundError, APIError
from rich.console import Console

# Carregar as configurações do arquivo settings.yml
settings = Dynaconf(settings_files=['/root/vars/settings.yml'])

# Criando uma instância do aplicativo Typer
app = typer.Typer()

# Criando uma instância do console rich
console = Console()

# Função para estabelecer a conexão com a OVH
def connect_to_ovh():
    """
    Estabelece a conexão com a API da OVH e retorna um cliente OVH.
    """
    return ovh.Client(
        endpoint=settings.ovh.endpoint,
        application_key=settings.ovh.application_key,
        application_secret=settings.ovh.application_secret,
        consumer_key=settings.ovh.consumer_key
    )

# Função para reiniciar uma VPS específica
def reboot_vps(vps_name: str):
    """
    Reinicia uma VPS específica.
    """
    try:
        # Estabelecer a conexão com a OVH
        client = connect_to_ovh()

        with console.status("[bold green]Reiniciando VPS...") as status:
            # Realiza a operação de reinicialização da VPS específica
            result = client.post(f"/vps/{vps_name}/reboot")

            # Exibe o resultado da operação
            console.print("[green]A reinicialização da VPS foi iniciada com sucesso![/green]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao reiniciar a VPS: {e}[/red]")

# Função para obter o nome, a provedora e o IP da VPS
def name_vps(vps_name: str):
    """
    Obtém o nome, a provedora e o IP da VPS específica.
    """
    try:
        # Estabelecer a conexão com a OVH
        client = connect_to_ovh()

        with console.status("[bold green]Obtendo informações da VPS...") as status:
            # Realiza a operação de "get" na VPS específica para obter os IPs
            ips = client.get(f"/vps/{vps_name}/ips")

            # Realiza a operação de "get" na VPS específica para obter o displayName
            result = client.get(f"/vps/{vps_name}")

            # Exibe o displayName, a provedora e os IPs da VPS
            console.print(f"[green]Nome da VPS '{vps_name}': {result.get('displayName')}")
            console.print(f"[green]IP {', '.join(ips)}")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao obter informações da VPS: {e}[/red]")

# Função para listar todas as VPS disponíveis
def list_vps():
    """
    Lista todas as VPS disponíveis.
    """
    try:
        # Estabelecer a conexão com a OVH
        client = connect_to_ovh()

        with console.status("[bold green]Listando todas as VPS disponíveis...[/bold green]") as status:
            # Realiza a operação de "get" para listar todas as VPS
            vps_list = client.get("/vps")

            # Exibe a lista de VPS
            console.print(f"[green]VPS disponíveis: {', '.join(vps_list)}[/green]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao listar as VPS: {e}[/red]")

# Função para contar o número total de VPS disponíveis
def count_vps():
    """
    Conta o número total de VPS disponíveis.
    """
    try:
        # Estabelecer a conexão com a OVH
        client = connect_to_ovh()

        with console.status("[bold green]Contando o número total de VPS disponíveis...[/bold green]") as status:
            # Realiza a operação de "get" para listar todas as VPS
            vps_list = client.get("/vps")

            # Conta o número de VPS na lista
            total_vps = len(vps_list)

            # Exibe o total de VPS
            console.print(f"[green]Total de VPS disponíveis: {total_vps}[/green]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao contar o número de VPS: {e}[/red]")

def get_all_ips():
    """
    Obtém todos os IPs das VPS disponíveis e escreve em um arquivo CSV.
    """
    try:
        # Estabelecer a conexão com a OVH
        client = connect_to_ovh()

        with console.status("[bold green]Obtendo IPs das VPS e escrevendo em arquivo CSV...") as status:
            # Abre o arquivo CSV em modo de escrita
            with open('vps_ips.csv', mode='w', newline='') as file:
                writer = csv.writer(file)

                # Escreve os cabeçalhos das colunas no arquivo CSV
                writer.writerow(['Nome da VPS', 'IPs'])

                # Realiza a operação de "get" para listar todas as VPS
                vps_list = client.get("/vps")

                for vps_name in vps_list:
                    try:
                        # Realiza a operação de "get" na VPS específica para obter os IPs
                        ips = client.get(f"/vps/{vps_name}/ips")

                        # Escreve uma linha no arquivo CSV com o nome da VPS e seus IPs
                        writer.writerow([vps_name, ', '.join(ips)])
                    except APIError as e:
                        # Ignora as VPS expiradas
                        if "This service is expired" in str(e):
                            console.print(f"[yellow]VPS '{vps_name}' está expirada e será ignorada.[/yellow]")
                        else:
                            console.print(f"[red]Erro ao obter os IPs da VPS '{vps_name}': {e}[/red]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao obter os IPs das VPS: {e}[/red]")

@app.command()
def start():
    """
    Inicia a aplicação para monitorar e executar comandos em servidores VPS.
    """
    console.print("[bold cyan]Aplicação iniciada...[/bold cyan]")

    # Loop infinito para aguardar novos comandos
    while True:
        # Aguarda um novo comando da linha de comando
        command = typer.prompt("Digite o comando (ex: reboot <VPS>, name <VPS>, list, count, ips)")

        # Processa o comando
        command_parts = command.split()
        if len(command_parts) >= 2:
            if command_parts[0] == "reboot":
                reboot_vps(command_parts[1])
            elif command_parts[0] == "name":
                name_vps(command_parts[1])
            else:
                console.print("[red]Comando inválido. Use 'reboot <VPS>' ou 'name <VPS>'[/red]")
        elif len(command_parts) == 1:
            if command_parts[0] == "list":
                list_vps()
            elif command_parts[0] == "count":
                count_vps()
            elif command_parts[0] == "ips":  # Adicionando a opção "ips"
                get_all_ips()  # Chama a função para obter todos os IPs das VPS
            else:
                console.print("[red]Comando inválido. Use 'reboot <VPS>', 'name <VPS>', 'list', 'count' ou 'ips'[/red]")
        else:
            console.print("[red]Comando inválido. Use 'reboot <VPS>', 'name <VPS>', 'list', 'count' ou 'ips'[/red]")

# Executando a CLI
if __name__ == "__main__":
    app()
