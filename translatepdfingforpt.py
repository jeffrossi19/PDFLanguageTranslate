import os

from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
from googletrans import Translator


def extract_text_from_pdf(pdf_path):
    """Extrai texto de cada página do PDF."""
    reader = PdfReader(pdf_path)
    pages_text = [page.extract_text() for page in reader.pages]
    return pages_text


def translate_text(text, target_language="pt"):
    """Traduz texto para o idioma desejado."""
    translator = Translator()
    return translator.translate(text, dest=target_language).text


def save_translated_text(translations, output_path):
    """Salva o texto traduzido em um arquivo PDF."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for i, text in enumerate(translations):
        pdf.set_font('Arial', size=12)
        pdf.multi_cell(0, 10, f"--- Página {i + 1} ---\n{text}\n\n")

    pdf.output(output_path)


def split_pdf(pdf_path, max_pages=10):
    """Divide um PDF em arquivos menores com um máximo de `max_pages` páginas cada."""
    input_pdf = PdfReader(pdf_path)
    total_pages = len(input_pdf.pages)
    output_paths = []

    for i in range(0, total_pages, max_pages):
        output_pdf = PdfWriter()
        for j in range(i, min(i + max_pages, total_pages)):
            output_pdf.add_page(input_pdf.pages[j])
        output_path = pdf_path.replace('.pdf', f'_part{i//max_pages}.pdf')
        with open(output_path, 'wb') as out_file:
            output_pdf.write(out_file)
        output_paths.append(output_path)

    return output_paths


def process_pdf_part(pdf_part, output_dir):
    """Processa uma parte de PDF para tradução e salvamento."""
    pages_text = extract_text_from_pdf(pdf_part)
    translations = [translate_text(page) for page in pages_text]
    output_path = os.path.join(output_dir, os.path.basename(pdf_part).replace('.pdf', '_translated.pdf'))
    save_translated_text(translations, output_path)
    return output_path


def translate_large_pdf(pdf_path, output_dir):
    """Traduz um arquivo PDF grande dividindo em partes e traduzindo separadamente."""
    print("Dividindo o PDF...")
    pdf_parts = split_pdf(pdf_path)

    translated_files = []
    for part in pdf_parts:
        print(f"Traduzindo parte: {part}")
        translated_files.append(process_pdf_part(part, output_dir))

    print("Reunindo arquivos traduzidos...")
    final_output_path = os.path.join(output_dir, "arquivo_traduzido_final.pdf")
    with open(final_output_path, 'wb') as final_pdf:
        writer = PdfWriter()
        for translated_file in translated_files:
            reader = PdfReader(translated_file)
            for page in reader.pages:
                writer.add_page(page)
        writer.write(final_pdf)

    print(f"Arquivo traduzido completo salvo em: {final_output_path}")


# Caminho do arquivo PDF local
input_pdf = r"C:\Projetos\Tradutor\teste.pdf"

# Diretório de saída local (subpasta "documents_translated")
output_directory = r"C:\Projetos\Tradutor\documents_translated"

# Crie a pasta se ela não existir
os.makedirs(output_directory, exist_ok=True)

# Traduzir o PDF grande
translate_large_pdf(input_pdf, output_directory)