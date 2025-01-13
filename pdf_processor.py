import os
import re
import pdfplumber

def process_pdfs(folder_path):
    """
    Processa todos os PDFs em uma pasta, extraindo número (com DDD), nome e e-mail.
    Retorna uma lista de dicionários com os dados extraídos.
    """
    extracted_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    print(f"Texto extraído da página {page.page_number}:\n{text}")  # Verificar o texto

                    if text:
                        # Extraindo Nome (Primeira linha do texto ou ajustando conforme necessário)
                        nome_match = re.search(r"^(.*?)(?:\n|$)", text)  # Captura o primeiro nome completo
                        nome = nome_match.group(1).strip() if nome_match else "Não encontrado"

                        # Extraindo Número completo (DDD + número)
                        numero_match = re.search(r"(?i)Telefone[:\s]*\(?\d{2}\)?\s*\d{4,5}-?\d{4}", text)
                        if numero_match:
                            numero = numero_match.group(0).replace("Telefone:", "").strip()
                            numero = re.sub(r"[^\d]", "", numero)  # Remove tudo que não for número
                        else:
                            numero = "Não encontrado"

                        # Extraindo E-mail
                        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
                        email = email_match.group(0) if email_match else "Não encontrado"

                        # Adiciona os dados extraídos
                        extracted_data.append({
                            "numero": numero,
                            "nome": nome,
                            "email": email
                        })

    return extracted_data
