import json
import typer
import ovh
from dynaconf import Dynaconf
from ovh.exceptions import ResourceNotFoundError, APIError

# Carregar as configurações do arquivo settings.yml
settings = Dynaconf(settings_files=['/root/vars/settings.yml'])

# Criando uma instância do aplicativo Typer
app = typer.Typer()

# Função para reiniciar uma VPS específica
def reboot_vps(vps_name: str):
    """
    Reinicia uma VPS específica.
    """
    try:
        # Instantiate an OVH Client.
        client = ovh.Client(
            endpoint=settings.ovh.endpoint,
            application_key=settings.ovh.application_key,
            application_secret=settings.ovh.application_secret,
            consumer_key=settings.ovh.consumer_key
        )

        # Realiza a operação de reinicialização da VPS específica
        result = client.post(f"/vps/{vps_name}/reboot")

        # Exibe o resultado da operação
        typer.echo(json.dumps(result, indent=4))

        # Verifica se a operação foi concluída com sucesso
        if result.get("state") == "todo":
            typer.echo("A reinicialização da VPS foi iniciada com sucesso!")
        else:
            typer.echo("A reinicialização da VPS falhou. Verifique o status da VPS.")
    except ResourceNotFoundError as e:
        typer.echo(f"Erro: {e}")
    except APIError as e:
        typer.echo(f"Erro ao reiniciar a VPS: {e}")

# Função para obter o nome da VPS
def name_vps(vps_name: str):
    """
    Obtém o nome da VPS específica.
    """
    try:
        # Instantiate an OVH Client.
        client = ovh.Client(
            endpoint=settings.ovh.endpoint,
            application_key=settings.ovh.application_key,
            application_secret=settings.ovh.application_secret,
            consumer_key=settings.ovh.consumer_key
        )

        # Realiza a operação de "get" na VPS específica
        result = client.get(f"/vps/{vps_name}")

        # Exibe apenas o displayName da VPS
        typer.echo(f"DisplayName: {result.get('displayName')}")
    except ResourceNotFoundError as e:
        typer.echo(f"Erro: {e}")
    except APIError as e:
        typer.echo(f"Erro ao obter o nome da VPS: {e}")

# Definindo a função principal da CLI
@app.command()
def start():
    """
    Inicia a aplicação para monitorar e executar comandos em servidores VPS.
    """
    typer.echo("Aplicação iniciada...")

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
                typer.echo("Comando inválido. Use 'reboot <VPS>' ou 'name <VPS>'")
        else:
            typer.echo("Comando inválido. Use 'reboot <VPS>' ou 'name <VPS>'")

# Executando a CLI
if __name__ == "__main__":
    app()
