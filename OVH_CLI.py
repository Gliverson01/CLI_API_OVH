import json
import typer
import ovh
from dynaconf import Dynaconf
from ovh.exceptions import ResourceNotFoundError, APIError
from rich import print
from rich.console import Console
from rich.progress import track

# Carregar as configurações do arquivo settings.yml
settings = Dynaconf(settings_files=['/root/vars/settings.yml'])

# Criando uma instância do aplicativo Typer
app = typer.Typer()

# Criando uma instância do console rich
console = Console()

# Função para reiniciar uma VPS específica
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
            print(json.dumps(result, indent=4))

            # Verifica se a operação foi concluída com sucesso
            if result.get("state") == "todo":
                print("[green]A reinicialização da VPS foi iniciada com sucesso![/green]")
            else:
                print("[red]A reinicialização da VPS falhou. Verifique o status da VPS.[/red]")
    except ResourceNotFoundError as e:
        print(f"[red]Erro: {e}[/red]")
    except APIError as e:
        print(f"[red]Erro ao reiniciar a VPS: {e}[/red]")

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
            console.print(f"[green]DisplayName: {result.get('displayName')}[/green]")
    except ResourceNotFoundError as e:
        console.print(f"[red]Erro: {e}[/red]")
    except APIError as e:
        console.print(f"[red]Erro ao obter o nome da VPS: {e}[/red]")

# Definindo a função principal da CLI
@app.command()
def start():
    """
    Inicia a aplicação para monitorar e executar comandos em servidores VPS.
    """
    console.print("[bold cyan]Aplicação iniciada...[/bold cyan]")

    # Loop infinito para aguardar novos comandos
    while True:
        # Aguarda um novo comando da linha de comando
        command = typer.prompt("Digite o comando (ex: reboot <VPS> ou name <VPS>):")
        
        # Processa o comando
        command_parts = command.split()
        if command_parts and len(command_parts) == 2:
            if command_parts[0] == "reboot":
                reboot_vps(command_parts[1])
            elif command_parts[0] == "name":
                name_vps(command_parts[1])
            else:
                console.print("[red]Comando inválido. Use 'reboot <VPS>' ou 'name <VPS>'[/red]")
        else:
            console.print("[red]Comando inválido. Use 'reboot <VPS>' ou 'name <VPS>'[/red]")

# Executando a CLI
if __name__ == "__main__":
    app()
