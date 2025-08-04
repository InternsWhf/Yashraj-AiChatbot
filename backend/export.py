from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os
import io
from typing import Dict, List, Any, Optional
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import tempfile

class PDFExporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for WHF branding"""
        # WHF Header Style
        self.whf_header_style = ParagraphStyle(
            'WHFHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#ff6600'),  # WHF Orange
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        # WHF Subheader Style
        self.whf_subheader_style = ParagraphStyle(
            'WHFSubheader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            alignment=TA_LEFT,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # WHF Body Style
        self.whf_body_style = ParagraphStyle(
            'WHFBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            fontName='Helvetica'
        )
        
        # WHF Footer Style
        self.whf_footer_style = ParagraphStyle(
            'WHFFooter',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=0,
            fontName='Helvetica'
        )
    
    def create_whf_header(self, doc, title: str):
        """Create WHF branded header"""
        elements = []
        
        # WHF Logo placeholder (you can add actual logo)
        logo_text = "🏭 WESTERN HEAT & FORGE"
        logo_para = Paragraph(logo_text, self.whf_header_style)
        elements.append(logo_para)
        
        # Title
        title_para = Paragraph(title, self.whf_subheader_style)
        elements.append(title_para)
        
        # Date and time
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        date_para = Paragraph(f"Generated on: {current_time}", self.whf_footer_style)
        elements.append(date_para)
        
        elements.append(Spacer(1, 20))
        return elements
    
    def create_question_section(self, question: str):
        """Create question section"""
        elements = []
        
        # Question header
        question_header = Paragraph("Question:", self.whf_subheader_style)
        elements.append(question_header)
        
        # Question text
        question_text = Paragraph(question, self.whf_body_style)
        elements.append(question_text)
        
        elements.append(Spacer(1, 15))
        return elements
    
    def create_answer_section(self, answer: str):
        """Create answer section"""
        elements = []
        
        # Answer header
        answer_header = Paragraph("Answer:", self.whf_subheader_style)
        elements.append(answer_header)
        
        # Answer text
        answer_text = Paragraph(answer, self.whf_body_style)
        elements.append(answer_text)
        
        elements.append(Spacer(1, 15))
        return elements
    
    def create_source_files_section(self, source_files: List[str]):
        """Create source files section"""
        elements = []
        
        if source_files:
            # Source files header
            sources_header = Paragraph("Source Files:", self.whf_subheader_style)
            elements.append(sources_header)
            
            # Create table for source files
            data = [["#", "File Name"]]
            for i, file_name in enumerate(source_files, 1):
                data.append([str(i), file_name])
            
            table = Table(data, colWidths=[0.5*inch, 5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6600')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 15))
        
        return elements
    
    def create_metadata_section(self, metadata: Dict[str, Any]):
        """Create metadata section"""
        elements = []
        
        if metadata:
            # Metadata header
            metadata_header = Paragraph("Additional Information:", self.whf_subheader_style)
            elements.append(metadata_header)
            
            # Create table for metadata
            data = [["Field", "Value"]]
            for key, value in metadata.items():
                data.append([key.title(), str(value)])
            
            table = Table(data, colWidths=[2*inch, 3.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 15))
        
        return elements
    
    def create_whf_footer(self):
        """Create WHF branded footer"""
        elements = []
        
        elements.append(Spacer(1, 20))
        
        # Footer line
        footer_line = "─" * 50
        footer_para = Paragraph(footer_line, self.whf_footer_style)
        elements.append(footer_para)
        
        # WHF contact info
        contact_info = """
        Western Heat & Forge | AI-Powered Document Assistant<br/>
        For technical support, contact: support@whf.com<br/>
        This document was generated by Forgia AI Assistant
        """
        contact_para = Paragraph(contact_info, self.whf_footer_style)
        elements.append(contact_para)
        
        return elements
    
    def generate_pdf(self, question: str, answer: str, source_files: List[str] = None, 
                    metadata: Dict[str, Any] = None, title: str = "WHF AI Assistant Response"):
        """Generate a complete PDF document"""
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        # Build PDF content
        story = []
        
        # Add header
        story.extend(self.create_whf_header(doc, title))
        
        # Add question section
        story.extend(self.create_question_section(question))
        
        # Add answer section
        story.extend(self.create_answer_section(answer))
        
        # Add source files section
        if source_files:
            story.extend(self.create_source_files_section(source_files))
        
        # Add metadata section
        if metadata:
            story.extend(self.create_metadata_section(metadata))
        
        # Add footer
        story.extend(self.create_whf_footer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def save_pdf(self, pdf_content: bytes, filename: str = None):
        """Save PDF to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"whf_response_{timestamp}.pdf"
        
        with open(filename, 'wb') as f:
            f.write(pdf_content)
        
        return filename

class EmailExporter:
    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "forgia@whf.com")
        self.from_name = os.getenv("FROM_NAME", "Forgia AI Assistant")
    
    def send_pdf_email(self, to_email: str, subject: str, pdf_content: bytes, 
                      pdf_filename: str, message: str = None):
        """Send PDF via email using SendGrid"""
        
        if not self.sendgrid_api_key:
            raise Exception("SendGrid API key not configured")
        
        try:
            # Create email message
            mail = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=message or f"""
                <h2>WHF AI Assistant Response</h2>
                <p>Please find attached the response to your question from Forgia AI Assistant.</p>
                <p>Best regards,<br/>Forgia AI Assistant<br/>Western Heat & Forge</p>
                """
            )
            
            # Attach PDF
            encoded_pdf = base64.b64encode(pdf_content).decode()
            attachedFile = Attachment(
                FileContent(encoded_pdf),
                FileName(pdf_filename),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            mail.attachment = attachedFile
            
            # Send email
            sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
            response = sg.send(mail)
            
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send email"
            }

# Initialize exporters
pdf_exporter = PDFExporter()
email_exporter = EmailExporter() 