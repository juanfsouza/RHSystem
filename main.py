from selenium.webdriver.chrome.options import Options
import time
import customtkinter as ctk
import sqlite3
import os
import re
from grpc import services
import pdfplumber
from selenium.webdriver.common.by import By
from datetime import datetime
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC


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

def update_candidato(id, nome, numero, email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE candidatos 
    SET nome = ?, numero = ?, email = ? 
    WHERE id = ?
    """, (nome, numero, email, id))
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

        self.update_button = ctk.CTkButton(self.action_frame, text="Atualizar Selecionados", command=self.update_selected)
        self.update_button.pack(side="left", padx=10)

        self.delete_button = ctk.CTkButton(self.action_frame, text="Deletar Selecionados", command=self.delete_selected)
        self.delete_button.pack(side="left", padx=10)

        # Novo botão para extração de PDFs
        self.extract_button = ctk.CTkButton(self.action_frame, text="Extrair de PDFs", command=self.extract_from_pdfs)
        self.extract_button.pack(side="left", padx=10)

        # Botão de agendamento
        self.schedule_button = ctk.CTkButton(self.action_frame, text="Agendar", command=self.schedule_appointments)
        self.schedule_button.pack(side="left", padx=10)

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
        self.add_window = ctk.CTkToplevel(self)
        self.add_window.title("Adicionar Candidato")
        self.add_window.geometry("400x300")

        # Campos do formulário
        ctk.CTkLabel(self.add_window, text="Nome").pack(pady=0)
        nome_entry = ctk.CTkEntry(self.add_window)
        nome_entry.pack(pady=5)

        ctk.CTkLabel(self.add_window, text="Número de Telefone").pack(pady=0)
        numero_entry = ctk.CTkEntry(self.add_window)
        numero_entry.pack(pady=5)

        ctk.CTkLabel(self.add_window, text="Email").pack(pady=0)
        email_entry = ctk.CTkEntry(self.add_window)
        email_entry.pack(pady=5)

        def validate_and_add():
            nome = nome_entry.get()
            numero = numero_entry.get()
            email = email_entry.get()

            if nome and numero and email:
                if re.match(r"\(?\d{2}\)?\s*\d{4,5}-?\d{4}", numero) and re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", email):
                    add_candidato(nome, numero, email)
                    self.load_table()
                    self.add_window.destroy()
                else:
                    # Exibir mensagem de erro (se necessário)
                    print("Dados inválidos")
            else:
                print("Preencha todos os campos")

        add_button = ctk.CTkButton(self.add_window, text="Adicionar", command=validate_and_add)
        add_button.pack(pady=10)


    def save_new_candidato(self, nome_entry, numero_entry, email_entry):
        nome = nome_entry.get()
        numero = numero_entry.get()
        email = email_entry.get()
        add_candidato(nome, numero, email)
        self.load_table()
        self.add_window.destroy()

    def save_candidato(self, nome_entry, numero_entry, email_entry):
        """Salva o candidato no banco de dados."""
        nome = nome_entry.get()
        numero = numero_entry.get()
        email = email_entry.get()
        add_candidato(nome, numero, email)
        self.add_window.destroy()
        self.load_table()

    def delete_selected(self):
        """Deleta os candidatos selecionados."""
        selected_ids = [id for checkbox, id in self.checkboxes if checkbox.get() == 1]
        if selected_ids:
            delete_candidatos(selected_ids)
            self.load_table()  # Recarrega a tabela

    def update_selected(self):
        """Mostra o formulário de atualização de candidatos selecionados."""
        # Filtra os candidatos selecionados
        selected_ids = [id for checkbox, id in self.checkboxes if checkbox.get()]

        if not selected_ids:
            # Nenhum candidato selecionado
            ctk.CTkMessagebox(title="Erro", message="Selecione ao menos um candidato para atualizar.")
            return

        if len(selected_ids) > 1:
            # Apenas permite a atualização de um candidato de cada vez
            ctk.CTkMessagebox(title="Erro", message="Selecione apenas um candidato para atualizar.")
            return

        # Obter os dados do candidato selecionado
        id_candidato = selected_ids[0]
        candidato = next(c for c in fetch_candidatos() if c[0] == id_candidato)

        # Exibir janela para editar
        self.update_window = ctk.CTkToplevel(self)
        self.update_window.title("Atualizar Candidato")
        self.update_window.geometry("400x300")

        # Nome
        ctk.CTkLabel(self.update_window, text="Nome").pack(pady=0)
        nome_entry = ctk.CTkEntry(self.update_window)
        nome_entry.insert(0, candidato[1])
        nome_entry.pack(pady=5)

        # Número
        ctk.CTkLabel(self.update_window, text="Número").pack(pady=0)
        numero_entry = ctk.CTkEntry(self.update_window)
        numero_entry.insert(0, candidato[2])
        numero_entry.pack(pady=5)

        # E-mail
        ctk.CTkLabel(self.update_window, text="E-mail").pack(pady=0)
        email_entry = ctk.CTkEntry(self.update_window)
        email_entry.insert(0, candidato[3])
        email_entry.pack(pady=5)

        # Botão de salvar
        save_button = ctk.CTkButton(self.update_window, text="Salvar", command=lambda: self.save_update(id_candidato, nome_entry, numero_entry, email_entry))
        save_button.pack(pady=10)
    
    def save_update(self, id_candidato, nome_entry, numero_entry, email_entry):
        """Salva as atualizações no banco de dados."""
        nome = nome_entry.get()
        numero = numero_entry.get()
        email = email_entry.get()

        # Validação simples
        if not nome or not numero or not email:
            ctk.CTkMessagebox(title="Erro", message="Todos os campos devem ser preenchidos.")
            return

        # Atualiza o candidato no banco de dados
        update_candidato(id_candidato, nome, numero, email)

        # Fecha a janela de atualização
        self.update_window.destroy()

        # Atualiza a tabela na interface
        self.load_table()

        ctk.CTkMessagebox(title="Sucesso", message="Candidato atualizado com sucesso.")

    def extract_from_pdfs(self):
        folder_path = "caminho/para/pasta/dos/pdfs"
        extracted_data = process_pdfs(folder_path)
        
        for data in extracted_data:
            add_candidato(data["nome"], data["numero"], data["email"])

        self.load_table()  # Recarrega a tabela após a inserção


    def schedule_appointments(self):
        """Exibe os campos de agendamento para cada candidato selecionado."""
        # Filtra os candidatos selecionados
        selected_ids = [id for checkbox, id in self.checkboxes if checkbox.get()]
        
        if not selected_ids:
            ctk.CTkMessagebox(title="Erro", message="Selecione ao menos um candidato para agendar.")
            return

        # Campo para tempo de agendamento
        time_slot_entry = ctk.CTkEntry(self, placeholder_text="Tempo de Agendamento (minutos)")
        time_slot_entry.pack(pady=5)
        
        # Campo para data e hora
        date_time_entry = ctk.CTkEntry(self, placeholder_text="Data e Hora (DD/MM/YYYY HH:MM)")
        date_time_entry.pack(pady=5)

        # Botão de confirmação
        confirm_button = ctk.CTkButton(self, text="Confirmar Agendamento", command=lambda: self.confirm_schedule(selected_ids, time_slot_entry, date_time_entry))
        confirm_button.pack(pady=10)

    def confirm_schedule(self, selected_ids, time_slot_entry, date_time_entry):
        """Confirma o agendamento e envia a mensagem via WhatsApp."""
        # Recuperar dados inseridos
        time_slot = int(time_slot_entry.get())
        date_time_str = date_time_entry.get()
        
        try:
            # Parse da data e hora
            schedule_datetime = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data e hora inválido.")
            return
        
        # Enviar mensagens via WhatsApp com Selenium
        self.send_whatsapp_messages(selected_ids, time_slot, schedule_datetime)
    
    def send_whatsapp_messages(self, selected_ids, time_slot, schedule_datetime):
        """Envia mensagens via WhatsApp usando Selenium."""
        chrome_opt = uc.ChromeOptions()
                        
        options = uc.ChromeOptions()

        # Inicializar o navegador Chrome
        driver = uc.Chrome(options=chrome_opt)

        # Acessar WhatsApp Web
        driver.get("https://web.whatsapp.com/")

        print("Por favor, escaneie o QR Code se necessário.")
        time.sleep(15)  # Espera para escanear o QR Code

        for candidato_id in selected_ids:
            candidato = next(c for c in fetch_candidatos() if c[0] == candidato_id)
            nome = candidato[1]
            numero = candidato[2]

            # Criar a mensagem com data e tempo de agendamento
            message = f"Olá {nome}, seu agendamento está confirmado para {schedule_datetime.strftime('%d/%m/%Y às %H:%M')}. O tempo de atendimento é de {time_slot} minutos."

            # URL para enviar a mensagem no WhatsApp
            driver.get(f"https://web.whatsapp.com/send?phone=+55{numero}&text={message}")

            time.sleep(5)  # Espera o carregamento da página

            # Encontrar o botão de envio e clicar
            send_button = driver.find_element(By.XPATH, '//button[@data-testid="compose-btn-send"]')
            send_button.click()

            time.sleep(2)  # Espera para garantir que a mensagem seja enviada

        driver.quit()  # Fecha o navegador

        ctk.CTkMessagebox(title="Sucesso", message="Mensagens enviadas com sucesso!")

if __name__ == "__main__":
    setup_database()
    app = RHApp()
    app.mainloop()
