import typer
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

# Função para obter o nome da VPS
def name_vps(vps_name: str):
    """
    Obtém o nome da VPS específica.
    """
    try:
        # Estabelecer a conexão com a OVH
        client = connect_to_ovh()

        with console.status("[bold green]Obtendo nome da VPS...[/bold green]") as status:
            # Realiza a operação de "get" na VPS específica
            result = client.get(f"/vps/{vps_name}")

            # Exibe apenas o displayName da VPS
            console.print(f"[green]Nome da VPS '{vps_name}': {result.get('displayName')}[/green]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao obter o nome da VPS: {e}[/red]")

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

# Definindo os comandos da CLI
@app.command()
def start():
    """
    Inicia a aplicação para monitorar e executar comandos em servidores VPS.
    """
    console.print("[bold cyan]Aplicação iniciada...[/bold cyan]")

    # Loop infinito para aguardar novos comandos
    while True:
        # Aguarda um novo comando da linha de comando
        command = typer.prompt("Digite o comando (ex: reboot <VPS>, name <VPS>, list, count)")
        
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
            else:
                console.print("[red]Comando inválido. Use 'reboot <VPS>', 'name <VPS>', 'list' ou 'count'[/red]")
        else:
            console.print("[red]Comando inválido. Use 'reboot <VPS>', 'name <VPS>', 'list', 'count' ou 'setPassword <VPS> <new_password>'[/red]")

# Executando a CLI
if __name__ == "__main__":
    app()
