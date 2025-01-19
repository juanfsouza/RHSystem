# WhatsApp Automation with Scheduled Messages

This project automates the process of sending scheduled WhatsApp messages to multiple candidates using Selenium and Python. The script includes functionality to increment the scheduled time for each candidate dynamically and ensures sequential delivery of personalized messages.

Features

Automated WhatsApp Messaging:

Sends personalized messages to candidates through WhatsApp Web.

Waits for the user to scan the QR code to log into WhatsApp Web.

Dynamic Scheduling:

Adjusts the scheduled time for each candidate based on a configurable time slot.

Ensures each candidate receives a message with a unique time.

Error Handling:

Handles scenarios where the send button is not found or other issues arise during message delivery.



![Screenshot_1](https://github.com/user-attachments/assets/6d9ea71b-4a1d-4ed2-9d79-96774b63c837)
![Screenshot_2](https://github.com/user-attachments/assets/f9e870fe-69c8-4220-823a-165e492877a3)
![Screenshot_3](https://github.com/user-attachments/assets/8fb44cca-7686-4b59-bdf2-7d1a5280ef37)

Prerequisites

Python 3.9 or later

Google Chrome and Chromedriver compatible with your Chrome version

Required Python packages (install via pip):

pip install selenium undetected-chromedriver customtkinter

How It Works

Message Format

Each message is dynamically generated with the candidate's name and their scheduled appointment time. For example:

Message Template:

Olá {nome}, seu agendamento está confirmado para {data} às {hora}.

Example Messages:

Candidate 1: "Olá João, seu agendamento está confirmado para 15/01/2025 às 11:00."

Candidate 2: "Olá Maria, seu agendamento está confirmado para 15/01/2025 às 11:30."

Scheduling Logic

The initial date and time are provided by the user.

The time for each subsequent candidate is incremented by a configurable time slot (e.g., 30 minutes).

Code Highlights

Sending Messages Loop

for candidato_id in selected_ids:
    # Retrieve candidate information
    candidato = next(c for c in fetch_candidatos() if c[0] == candidato_id)
    nome = candidato[1]
    numero = candidato[2]

    # Generate message with adjusted schedule time
    message = f"Olá {nome}, seu agendamento está confirmado para {schedule_datetime.strftime('%d/%m/%Y às %H:%M')}.">

    # Open WhatsApp Web with the pre-filled message
    driver.get(f"https://web.whatsapp.com/send?phone=+55{numero}&text={message}")

    time.sleep(10)  # Wait for the page to load

    try:
        # Locate and click the send button
        send_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-icon='send']"))
        )
        send_button.click()
        print(f"Mensagem enviada para {nome} no número {numero}: {message}")
    except Exception as e:
        print(f"Erro ao enviar mensagem para {nome} no número {numero}: {e}")

    # Increment the schedule time for the next candidate
    schedule_datetime += timedelta(minutes=time_slot)

Setup Instructions

Clone the Repository

git clone https://github.com/juanfsouza/RHSystem.git
cd RHSystem

Install Dependencies

pip install -r requirements.txt

Run the Script

python main.py

Follow the Instructions

Scan the QR code displayed in the browser to log into WhatsApp Web.

Enter the initial schedule time and time slot when prompted.

Select candidates and confirm scheduling.

Limitations

Requires WhatsApp Web to remain open during the entire process.

Depends on the user scanning the QR code for authentication.

Contributing for me
