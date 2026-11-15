from . import requirements, rules


def catalog(snap):
    """Itens do guarda-roupa com o requisito, o progresso e se já foram liberados."""
    return [{"id": item["id"], "nome": item["nome"], "slot": item["slot"],
             **requirements.status(item["requisito"], snap)}
            for item in rules.load()["itens"]]
