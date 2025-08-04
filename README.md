# AI-Direito

Sistema de processamento e consulta de livros jurídicos usando OCR e embeddings.

## Estrutura

```
.
├── data/              # PDFs e textos processados
├── src/
│   ├── pdf_processor.py  # Processamento de PDFs (OCR e extração)
│   ├── vector_store.py   # Interface com Qdrant
│   ├── chat.py          # Interface de chat com GPT
│   └── config.py        # Configurações
│
├── main.py              # Script principal
├── requirements.txt     # Dependências
└── .env                # Variáveis de ambiente
```

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure o `.env`:
```
OPENAI_API_KEY=sua_chave_aqui
QDRANT_HOST=seu_host
QDRANT_API_KEY=sua_chave
```

3. Coloque os PDFs na pasta `data/`
   - O sistema detecta automaticamente se um PDF precisa de OCR
   - Os textos processados são salvos como `.txt` na mesma pasta

## Uso

```bash
# Processa PDFs e armazena no Qdrant
python main.py

# Interface de chat
python src/chat.py
``` 