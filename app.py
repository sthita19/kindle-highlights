import os
import random
import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import io

# Load environment variables directly
SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
SENDER_PASSWORD = st.secrets["SENDER_PASSWORD"]

def read_clippings(file_content, encoding="utf-8"):
    try:
        file_content.seek(0)
        content = file_content.read()
        clippings = content.decode(encoding).split("==========\n")
        return clippings
    except Exception as e:
        st.error(f"Error reading file content: {e}")
        return []

def separate_clipping(clipping):
    parts = clipping.strip().split("\n")
    if len(parts) < 3:
        return None
    
    book_details = parts[0].strip()
    highlight_text = ""
    for part in reversed(parts):
        if part.strip() and part.strip() != "==========":
            highlight_text = part.strip()
            break
    
    return f"<b>{book_details}</b><br/><br/><i>\"{highlight_text}\"</i><br/><br/>"

def select_random_clippings(clippings, num_clippings=5):
    selected_clippings = []
    clippings_count = len(clippings)
    if clippings_count == 0:
        return selected_clippings
    for _ in range(min(num_clippings, clippings_count)):
        random_index = random.randint(0, clippings_count - 1)
        formatted_clipping = separate_clipping(clippings[random_index])
        if formatted_clipping:
            selected_clippings.append(formatted_clipping)
    return selected_clippings

def send_email(receiver_email, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "Your Kindle Highlights"
        
        msg.attach(MIMEText(message, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        st.success(f"Email successfully sent to {receiver_email}.")
    except Exception as e:
        st.error(f"Error sending email: {e}")
    finally:
        try:
            server.quit()
        except:
            pass

# Streamlit application
st.title("Kindle Highlights Emailer")

file = st.file_uploader("Upload your file", type=["txt"])
email = st.text_input("Recipient Email", value=RECEIVER_EMAIL)
num_highlights = st.number_input("Number of Highlights", min_value=1, value=5)
send_time = st.time_input("Send Time")

if st.button("Schedule Email"):
    if file and email and num_highlights > 0 and send_time:
        file_content = io.BytesIO(file.read())
        clippings = read_clippings(file_content)
        selected_clippings = select_random_clippings(clippings, num_highlights)
        if selected_clippings:
            message = "<br/>".join(selected_clippings)
            send_email(email, message)
        else:
            st.warning("No valid clippings found.")
    else:
        st.error("Please fill in all fields.")
