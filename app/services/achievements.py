from . import requirements, rules


def catalog(snap):
    """Conquistas com o progresso de cada uma. São derivadas do histórico, como o nível."""
    return [{"id": item["id"], "nome": item["nome"], "icone": item["icone"],
             **requirements.status(item["requisito"], snap)}
            for item in rules.load()["conquistas"]]
