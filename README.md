# Sistema de leitura de catracas

Projeto em Python para registrar leituras de entrada/saída em **8 catracas**,
acompanhar ocupação em tempo real e visualizar histórico.

## Funcionalidades

- Interface web visual para operar as catracas.
- Registro de leitura por crachá, catraca e direção (`entrada` ou `saida`).
- 8 catracas pré-configuradas (`CATRACA-01` até `CATRACA-08`).
- Controle de ocupação em tempo real.
- Histórico completo de leituras.

## Como executar a interface visual

```bash
python3 web_app.py
```

Depois, abra no navegador:

```text
http://localhost:8000
```

## Como testar

```bash
pytest -q
```
