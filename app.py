import gradio as gr
from datetime import datetime
from dateutil import parser
import pytz
import uuid
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from astro_calc import compute_chart

RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)


def create_pdf(data):
    name = f"astro_{uuid.uuid4().hex[:8]}.pdf"
    path = os.path.join(RESULT_DIR, name)

    c = canvas.Canvas(path, pagesize=A4)
    y = 800

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Astrological Report")
    y -= 40

    c.setFont("Helvetica", 11)

    c.drawString(50, y, f"Ascendant: {round(data['ascendant'], 2)}°")
    y -= 20
    c.drawString(50, y, f"Moon Sign: {data['moon_sign']}")
    y -= 20
    c.drawString(50, y, f"Manglik: {data['manglik']['text']}")
    y -= 20
    c.drawString(50, y, f"Current Dasha: {data['dasha']['current']}")
    y -= 20

    c.drawString(50, y, "Planet Positions:")
    y -= 20

    for p, v in data["longitudes"].items():
        c.drawString(60, y, f"{p}: {round(v, 2)}°")
        y -= 18

    c.save()
    return path


def analyze(dob, tob, tz_name, lat, lon):
    try:
        dt = parser.parse(f"{dob} {tob}")
        tz = pytz.timezone(tz_name)
        dt = tz.localize(dt)
    except Exception as e:
        return f"Invalid date/time: {e}", None

    try:
        chart = compute_chart(dt, float(lat), float(lon))
        pdf_path = create_pdf(chart)
        return "Analysis completed.", pdf_path
    except Exception as e:
        return f"Processing error: {e}", None


iface = gr.Interface(
    fn=analyze,
    inputs=[
        gr.Textbox(label="Date of Birth (YYYY-MM-DD)"),
        gr.Textbox(label="Time of Birth (HH:MM)"),
        gr.Textbox(label="Timezone (e.g., Asia/Kolkata)"),
        gr.Number(label="Latitude"),
        gr.Number(label="Longitude"),
    ],
    outputs=[gr.Textbox(label="Status"), gr.File(label="Download Report")],
    title="Astro Bot",
)

if __name__ == "__main__":
    iface.launch()
