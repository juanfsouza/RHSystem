import customtkinter as ctk
import sqlite3
import os
import re
import pdfplumber

# Configuração inicial do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Banco de Dados SQLite
DB_NAME = "candidatos.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        numero TEXT,
        email TEXT
    )
    """)
    conn.commit()
    conn.close()

def fetch_candidatos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidatos")
    data = cursor.fetchall()
    conn.close()
    return data

def add_candidato(nome, numero, email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO candidatos (nome, numero, email) VALUES (?, ?, ?)", (nome, numero, email))
    conn.commit()
    conn.close()

def delete_candidatos(ids):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM candidatos WHERE id = ?", [(id,) for id in ids])
    conn.commit()
    conn.close()

def process_pdfs(folder_path):
    """
    Processa todos os PDFs em uma pasta, extraindo número (com DDD), nome e e-mail.
    """
    extracted_data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Verificando se há um nome válido
                        nome_match = re.search(r"^(.*?)(?:\n|$)", text)
                        nome = nome_match.group(1).strip() if nome_match else "Não encontrado"

                        # Verificando se o número de telefone está no formato esperado
                        numero_match = re.search(r"(?i)Telefone[:\s]*\(?\d{2}\)?\s*\d{4,5}-?\d{4}", text)
                        if numero_match:
                            numero = numero_match.group(0).replace("Telefone:", "").strip()
                            numero = re.sub(r"[^\d]", "", numero)  # Remove qualquer caractere não numérico
                        else:
                            numero = "Não encontrado"

                        # Verificando se o email é válido
                        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
                        email = email_match.group(0) if email_match else "Não encontrado"

                        if nome != "Não encontrado" and numero != "Não encontrado" and email != "Não encontrado":
                            extracted_data.append({
                                "numero": numero,
                                "nome": nome,
                                "email": email
                            })
    return extracted_data

# Interface
class RHApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de RH")
        self.geometry("800x600")

        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Tabela
        self.table = ctk.CTkScrollableFrame(self.main_frame)
        self.table.pack(pady=10, padx=10, fill="both", expand=True)
        self.load_table()

        # Botões de ação
        self.action_frame = ctk.CTkFrame(self.main_frame)
        self.action_frame.pack(pady=10, padx=10, fill="x")

        self.add_button = ctk.CTkButton(self.action_frame, text="Adicionar", command=self.show_add_form)
        self.add_button.pack(side="left", padx=10)

        self.delete_button = ctk.CTkButton(self.action_frame, text="Deletar Selecionados", command=self.delete_selected)
        self.delete_button.pack(side="left", padx=10)

        # Novo botão para extração de PDFs
        self.extract_button = ctk.CTkButton(self.action_frame, text="Extrair de PDFs", command=self.extract_from_pdfs)
        self.extract_button.pack(side="left", padx=10)

    def load_table(self):
        """Carrega os dados do banco na tabela."""
        for widget in self.table.winfo_children():
            widget.destroy()

        candidatos = fetch_candidatos()

        self.checkboxes = []  # Lista para armazenar os checkboxes

        for candidato in candidatos:
            row_frame = ctk.CTkFrame(self.table)
            row_frame.pack(fill="x", pady=5)

            checkbox = ctk.CTkCheckBox(row_frame, text="", width=30)
            checkbox.grid(row=0, column=0, padx=5)
            self.checkboxes.append((checkbox, candidato[0]))  # Adiciona o checkbox e o ID

            ctk.CTkLabel(row_frame, text=str(candidato[1])).grid(row=0, column=1, padx=5)  # Nome
            ctk.CTkLabel(row_frame, text=str(candidato[2])).grid(row=0, column=2, padx=5)  # Telefone
            ctk.CTkLabel(row_frame, text=str(candidato[3])).grid(row=0, column=3, padx=5)  # Email

    def show_add_form(self):
        """Mostra o formulário de adição de candidato."""
        self.add_window = ctk.CTkToplevel(self)
        self.add_window.title("Adicionar Candidato")
        self.add_window.geometry("400x300")

        # Nome
        ctk.CTkLabel(self.add_window, text="Nome:").pack(pady=5)
        nome_entry = ctk.CTkEntry(self.add_window)
        nome_entry.pack(pady=5)

        # Telefone
        ctk.CTkLabel(self.add_window, text="Telefone:").pack(pady=5)
        numero_entry = ctk.CTkEntry(self.add_window)
        numero_entry.pack(pady=5)

        # Email
        ctk.CTkLabel(self.add_window, text="E-mail:").pack(pady=5)
        email_entry = ctk.CTkEntry(self.add_window)
        email_entry.pack(pady=5)

        # Botão de salvar
        save_button = ctk.CTkButton(self.add_window, text="Salvar", command=lambda: self.save_new_candidato(nome_entry, numero_entry, email_entry))
        save_button.pack(pady=20)

    def save_new_candidato(self, nome_entry, numero_entry, email_entry):
        nome = nome_entry.get()
        numero = numero_entry.get()
        email = email_entry.get()
        add_candidato(nome, numero, email)
        self.load_table()
        self.add_window.destroy()

    def delete_selected(self):
        """Deleta os candidatos selecionados."""
        selected_ids = [id for checkbox, id in self.checkboxes if checkbox.get() == 1]
        if selected_ids:
            delete_candidatos(selected_ids)
            self.load_table()  # Recarrega a tabela

    def extract_from_pdfs(self):
        """Extrai dados dos PDFs na pasta."""
        extracted_data = process_pdfs("pdfs")  # Pasta 'pdfs'
        for data in extracted_data:
            add_candidato(data['nome'], data['numero'], data['email'])
        self.load_table()  # Recarrega a tabela com os dados extraídos


if __name__ == "__main__":
    setup_database()
    app = RHApp()
    app.mainloop()
