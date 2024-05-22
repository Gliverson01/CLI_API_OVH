import typer
import csv
import ovh
from dynaconf import Dynaconf
from ovh.exceptions import ResourceNotFoundError, APIError
from rich.console import Console

# Carregar as configurações do arquivo settings.yml
try:
    settings = Dynaconf(settings_files=['/root/vars/settings.yml'])
except Exception as e:
    raise FileNotFoundError("Erro ao carregar o arquivo de configuração: settings.yml") from e

# Criando uma instância do aplicativo Typer
app = typer.Typer()

# Criando uma instância do console rich
console = Console()

def connect_to_ovh():
    """
    Estabelece a conexão com a API da OVH e retorna um cliente OVH.
    """
    try:
        return ovh.Client(
            endpoint=settings.ovh.endpoint,
            application_key=settings.ovh.application_key,
            application_secret=settings.ovh.application_secret,
            consumer_key=settings.ovh.consumer_key
        )
    except Exception as e:
        console.print(f"[red]Erro ao conectar com a API da OVH: {e}[/red]")
        raise

def reboot_vps(vps_name: str):
    """
    Reinicia uma VPS específica.
    """
    try:
        client = connect_to_ovh()

        with console.status("[bold green]Reiniciando VPS...") as status:
            client.post(f"/vps/{vps_name}/reboot")
            console.print(f"[green]A reinicialização da VPS '{vps_name}' foi iniciada com sucesso![/green]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao reiniciar a VPS '{vps_name}': {e}[/red]")

def name_vps(vps_name: str):
    """
    Obtém o nome, a provedora e o IP da VPS específica.
    """
    try:
        client = connect_to_ovh()

        with console.status("[bold green]Obtendo informações da VPS...") as status:
            ips = client.get(f"/vps/{vps_name}/ips")
            result = client.get(f"/vps/{vps_name}")

            console.print(f"[green]Nome da VPS '{vps_name}': {result.get('displayName')}")
            console.print(f"[green]IP(s): {', '.join(ips)}[/green]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao obter informações da VPS '{vps_name}': {e}[/red]")

def list_vps():
    """
    Lista todas as VPS disponíveis.
    """
    try:
        client = connect_to_ovh()

        with console.status("[bold green]Listando todas as VPS disponíveis...[/bold green]") as status:
            vps_list = client.get("/vps")
            console.print(f"[green]VPS disponíveis: {', '.join(vps_list)}[/green]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao listar as VPS: {e}[/red]")

def count_vps():
    """
    Conta o número total de VPS disponíveis.
    """
    try:
        client = connect_to_ovh()

        with console.status("[bold green]Contando o número total de VPS disponíveis...[/bold green]") as status:
            vps_list = client.get("/vps")
            total_vps = len(vps_list)
            console.print(f"[green]Total de VPS disponíveis: {total_vps}[/green]")
    except (ResourceNotFoundError, APIError) as e:
        console.print(f"[red]Erro ao contar o número de VPS: {e}[/red]")

def get_all_ips():
    """
    Obtém todos os IPs das VPS disponíveis e escreve em um arquivo CSV.
    """
    try:
        client = connect_to_ovh()

        with console.status("[bold green]Obtendo IPs das VPS e escrevendo em arquivo CSV...") as status:
            with open('vps_ips.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Nome da VPS', 'IPs'])

                vps_list = client.get("/vps")

                for vps_name in vps_list:
                    try:
                        ips = client.get(f"/vps/{vps_name}/ips")
                        writer.writerow([vps_name, ', '.join(ips)])
                    except APIError as e:
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
        command = typer.prompt("Digite o comando (ex: reboot <VPS>, name <VPS>, list, count, ips)")
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
            elif command_parts[0] == "ips":
                get_all_ips()
            else:
                console.print("[red]Comando inválido. Use 'reboot <VPS>', 'name <VPS>', 'list', 'count' ou 'ips'[/red]")
        else:
            console.print("[red]Comando inválido. Use 'reboot <VPS>', 'name <VPS>', 'list', 'count' ou 'ips'[/red]")

if __name__ == "__main__":
    app()
