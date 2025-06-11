#!/usr/bin/env python3

import click
from repository import Repository

repository = None
@click.group()
def cli():
    global repository
    repository = Repository()
    pass

@click.command()
def init():
    global repository
    repository.wit_init()

@click.command()
@click.argument('file_name',type=click.Path())
def add(file_name):
    global repository
    repository.wit_add_file(file_name)

@click.command()
@click.argument('message',type=click.STRING)
def commit(message):
    global repository
    repository.wit_commit(message)

@click.command()
def log():
    repository.wit_log()

@click.command()
def status():
    repository.wit_status()

@click.command()
@click.argument('id',type=click.STRING)
def checkout(id):
    global repository
    repository.wit_checkout(id)


@click.command()
def push():
    global repository
    repository.wit_push()

cli.add_command(init)
cli.add_command(add)
cli.add_command(commit)
cli.add_command(log)
cli.add_command(status)
cli.add_command(checkout)

cli.add_command(push)


if __name__ == '__main__':
    cli()

