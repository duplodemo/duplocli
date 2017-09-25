import click
import lambdaa
import connection
import apigateway

@click.group()
@click.version_option()
def cli():
    pass #Entry Point

cli.add_command(lambdaa.lambdaa)
cli.add_command(connection.connection)
cli.add_command(apigateway.apigateway)

