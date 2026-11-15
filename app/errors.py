class ApiError(Exception):
    """Erro previsto de uma chamada da API; vira JSON {"erro": mensagem}."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status
