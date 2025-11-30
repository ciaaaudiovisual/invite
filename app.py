import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont
import io

# ==============================================================================
# ⚙️ ÁREA DE CONFIGURAÇÃO
# ==============================================================================

ARQUIVO_TEMPLATE = "template.png"       
ARQUIVO_FONTE = "fonte_assinatura.otf"  # <--- Atualizado para .otf

# --- CONFIGURAÇÃO DA FOTO (ASPECTO 3:4) ---
# O template tem 720px de altura. Para manter 3:4, a largura deve ser 540px.
# (540 / 720 = 0.75, que é igual a 3/4)
FOTO_POS_X = 0        # Encostado na esquerda
FOTO_POS_Y = 0        # Encostado no topo
FOTO_LARGURA = 540    # Largura calculada para proporção 3:4
FOTO_ALTURA = 720     # Altura total do template

# --- CONFIGURAÇÃO DO NOME ---
NOME_POS_X = 870      # Centro horizontal
NOME_POS_Y = 645      # Altura da linha
TAMANHO_FONTE = 50    # Tamanho menor
COR_TEXTO = "white"

# ==============================================================================
# 🛠️ LÓGICA
# ==============================================================================

def carregar_recursos():
    # Carregar Template
    try:
        template = Image.open(ARQUIVO_TEMPLATE).convert("RGBA")
    except FileNotFoundError:
        st.error(f"❌ ERRO: O arquivo '{ARQUIVO_TEMPLATE}' não está no repositório.")
        return None, None

    # Carregar Fonte
    try:
        font = ImageFont.truetype(ARQUIVO_FONTE, TAMANHO_FONTE)
    except:
        # Tenta carregar a fonte padrão do sistema se a personalizada falhar
        font = ImageFont.load_default()
        st.warning(f"⚠️ A fonte '{ARQUIVO_FONTE}' não foi encontrada. Usando padrão.")
    
    return template, font

def processar_arte(foto_cortada, nome_usuario, template, fonte):
    # 1. Redimensionar para o tamanho exato (3:4)
    # Como o corte já foi feito na proporção certa, isso NÃO distorce a imagem.
    foto_final = foto_cortada.resize((FOTO_LARGURA, FOTO_ALTURA), Image.LANCZOS)
    foto_final = foto_final.convert("RGBA")
    
    # 2. Criar Canvas Transparente
    canvas = Image.new("RGBA", template.size)
    
    # 3. Colar Foto (Camada de Fundo)
    canvas.paste(foto_final, (FOTO_POS_X, FOTO_POS_Y))
    
    # 4. Colar Template (Camada da Frente)
    canvas.paste(template, (0, 0), mask=template)
    
    # 5. Escrever Nome
    # O código escreve EXATAMENTE o que está na variável nome_usuario
    draw = ImageDraw.Draw(canvas)
    draw.text((NOME_POS_X, NOME_POS_Y), nome_usuario, font=fonte, fill=COR_TEXTO, anchor="mm")
    
    return canvas

# ==============================================================================
# 📱 INTERFACE
# ==============================================================================

st.set_page_config(page_title="Gerador de Convite", page_icon="⚓", layout="wide")

st.title("⚓ Gerador de Convite")
st.markdown("---")

col_esq, col_dir = st.columns([1, 1.5])

with col_esq:
    st.subheader("1. Dados do Formando")
    # O input de texto captura exatamente o que é digitado (Ex: "João da Silva")
    nome_input = st.text_input("Nome Completo", placeholder="Digite aqui (Maiúsculas/Minúsculas)")
    
    arquivo_foto = st.file_uploader("Carregar Foto", type=['jpg', 'png', 'jpeg'])
    
    imagem_cortada_obj = None
    
    if arquivo_foto:
        st.info("📐 Ajuste o corte (Proporção Retrato 3:4)")
        img_original = Image.open(arquivo_foto)
        
        # Ferramenta de corte com Aspect Ratio travado em 3:4
        imagem_cortada_obj = st_cropper(
            img_original,
            realtime_update=True,
            box_color='#0000FF',
            aspect_ratio=(3, 4), # Trava a proporção Vertical
            should_resize_image=True
        )

with col_dir:
    st.subheader("2. Visualização")
    placeholder = st.empty()
    
    # Só gera se tiver todos os dados
    if arquivo_foto and nome_input and imagem_cortada_obj:
        tmpl, fnt = carregar_recursos()
        
        if tmpl:
            # Gera a imagem
            img_pronta = processar_arte(imagem_cortada_obj, nome_input, tmpl, fnt)
            img_rgb = img_pronta.convert("RGB")
            
            # Mostra na tela
            placeholder.image(img_rgb, caption=f"Convite de {nome_input}", use_container_width=True)
            
            # Botões de Download
            col_b1, col_b2 = st.columns(2)
            
            pdf_buffer = io.BytesIO()
            img_rgb.save(pdf_buffer, format="PDF", resolution=300.0)
            
            png_buffer = io.BytesIO()
            img_rgb.save(png_buffer, format="PNG")
            
            col_b1.download_button("📄 PDF (Impressão)", pdf_buffer.getvalue(), f"Convite_{nome_input}.pdf", "application/pdf", use_container_width=True)
            col_b2.download_button("📲 Imagem (WhatsApp)", png_buffer.getvalue(), f"Convite_{nome_input}.png", "image/png", use_container_width=True)

    elif not arquivo_foto:
        placeholder.info("👈 Envie sua foto para começar.")
