#!/usr/bin/env python3
"""
GOAT Scribe - Gradio Web UI

Launch: python app.py
Access: http://localhost:7860 (or Brev public URL)
"""

import os
import gradio as gr
from goatnote_scribe import GOATScribe

# Initialize scribe
scribe = GOATScribe()

def generate_note(clinical_text: str, patient_id: str = "anon-001"):
    """Generate ED note with guardrails"""
    try:
        result = scribe(clinical_text, patient_id=patient_id)
        
        # Format output
        note = result['note']
        phi_removed = result['phi_removed']
        guardrail_safe = result['guardrail_safe']
        guardrail_report = result.get('guardrail_report', '')
        
        # Build status message
        status = []
        status.append(f"✅ Generated {len(note)} characters")
        status.append(f"🔒 Removed {phi_removed} PHI entities")
        
        if guardrail_safe:
            status.append("✅ All safety checks passed")
        else:
            status.append(f"⚠️ Guardrail violations detected:")
            status.append(guardrail_report)
        
        status_msg = "\n".join(status)
        
        return note, status_msg
        
    except Exception as e:
        return "", f"❌ Error: {str(e)}"

# Build UI
with gr.Blocks(title="GOAT Scribe - Emergency Medicine") as demo:
    gr.Markdown("""
    # 🏥 GOAT Scribe: Emergency Medicine Documentation
    
    **H100-optimized HIPAA-compliant scribe with safety guardrails**
    
    Powered by NVIDIA Nemotron Nano 9B v2 | Built for ED teams
    """)
    
    with gr.Row():
        with gr.Column():
            clinical_input = gr.Textbox(
                label="Clinical Encounter",
                placeholder="35M presents with chest pain, 2h duration, radiating to left arm...\n\nVitals: BP 130/85, HR 95, RR 18, SpO2 98% RA\n\nPMH: HTN, hyperlipidemia\nMeds: Lisinopril 10mg daily, atorvastatin 40mg daily",
                lines=10
            )
            patient_id = gr.Textbox(
                label="Patient ID (optional)",
                value="anon-001",
                lines=1
            )
            generate_btn = gr.Button("Generate ED Note", variant="primary")
        
        with gr.Column():
            note_output = gr.Textbox(
                label="Generated ED Note",
                lines=15
            )
            status_output = gr.Textbox(
                label="Status & Guardrails",
                lines=8
            )
    
    # Examples
    gr.Examples(
        examples=[
            ["35M with chest pain, 2h duration, radiating to left arm, diaphoretic. Denies SOB, N/V. PMH: HTN, hyperlipidemia. Vitals: BP 145/90, HR 98, RR 16, SpO2 99% RA."],
            ["68F with acute stroke symptoms - right-sided weakness, facial droop, onset 45 minutes ago. Last known well time 1430. BP 185/100, HR 88, RR 18, SpO2 97% RA. NIHSS 12."],
            ["22M s/p MVC, ejected from vehicle, unrestrained. GCS 12 (E3V4M5). C-spine immobilized. BP 90/60, HR 125, RR 28. Visible chest wall deformity, decreased breath sounds left side."],
        ],
        inputs=clinical_input,
        label="Example Cases"
    )
    
    # Connect events
    generate_btn.click(
        fn=generate_note,
        inputs=[clinical_input, patient_id],
        outputs=[note_output, status_output]
    )
    
    gr.Markdown("""
    ---
    
    ### Safety Features
    
    ✅ **Vital Signs Validation**: HR, BP, RR, Temp, SpO2, GCS  
    ✅ **Medication Limits**: 11 common ED medications  
    ✅ **Protocol Warnings**: ACLS, ATLS, sepsis, stroke, STEMI  
    ✅ **HIPAA Compliance**: 18-identifier PHI detection
    
    **Repository**: https://github.com/GOATnote-Inc/scribegoat  
    **Contact**: b@thegoatnote.com
    """)

if __name__ == "__main__":
    # Launch with public sharing on Brev
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Brev handles public URLs
    )

