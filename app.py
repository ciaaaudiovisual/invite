import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont
import io

# ==============================================================================
# ⚙️ CONFIGURAÇÕES (AJUSTE FINO)
# ==============================================================================

ARQUIVO_TEMPLATE = "template.png"       
ARQUIVO_FONTE = "fonte_assinatura.otf"  # Certifique-se que o nome é exato

# --- CONFIGURAÇÃO DA FOTO ---
# Para não distorcer, a área de corte TERÁ a mesma proporção que estes valores.
FOTO_POS_X = 0        # Encostado na esquerda
FOTO_POS_Y = 0        # Encostado no topo
FOTO_LARGURA = 600    # Largura da área da foto (ajustei para não invadir o texto)
FOTO_ALTURA = 720     # Altura total (720p)

# --- CONFIGURAÇÃO DO NOME ---
NOME_POS_X = 870      # Centro horizontal da área do texto
NOME_POS_Y = 645      # Altura da linha do texto
TAMANHO_FONTE = 50    # REDUZIDO (Era 90)
COR_TEXTO = "white"

# ==============================================================================
# 🛠️ LÓGICA
# ==============================================================================

def carregar_recursos():
    try:
        template = Image.open(ARQUIVO_TEMPLATE).convert("RGBA")
    except FileNotFoundError:
        st.error(f"❌ ERRO: Arquivo '{ARQUIVO_TEMPLATE}' não encontrado.")
        return None, None

    try:
        font = ImageFont.truetype(ARQUIVO_FONTE, TAMANHO_FONTE)
    except:
        font = ImageFont.load_default()
        st.warning("⚠️ Fonte personalizada não encontrada. Usando padrão.")
    
    return template, font

def processar_arte(foto_cortada, nome_usuario, template, fonte):
    # 1. Redimensionar
    # Como travamos o aspect_ratio no corte, este resize NÃO vai distorcer a imagem
    foto_final = foto_cortada.resize((FOTO_LARGURA, FOTO_ALTURA), Image.LANCZOS)
    foto_final = foto_final.convert("RGBA")
    
    # 2. Criar Canvas
    canvas = Image.new("RGBA", template.size)
    
    # 3. Colar Foto (Na esquerda)
    canvas.paste(foto_final, (FOTO_POS_X, FOTO_POS_Y))
    
    # 4. Colar Template (Por cima)
    canvas.paste(template, (0, 0), mask=template)
    
    # 5. Escrever Nome (Respeitando maiúsculas/minúsculas do input)
    draw = ImageDraw.Draw(canvas)
    
    # anchor="mm" centraliza no ponto X,Y
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
    st.subheader("1. Dados")
    # O valor padrão está em Title Case (Maiúsculas só no início) para testar a fonte
    nome_input = st.text_input("Nome Completo", placeholder="Ex: Jhonatas Albuquerque")
    
    arquivo_foto = st.file_uploader("Sua Foto", type=['jpg', 'png', 'jpeg'])
    
    imagem_cortada_obj = None
    
    if arquivo_foto:
        st.info("Ajuste o retângulo azul. A proporção é fixa para não distorcer.")
        img_original = Image.open(arquivo_foto)
        
        # --- O SEGREDO PARA NÃO DISTORCER ESTÁ AQUI ---
        imagem_cortada_obj = st_cropper(
            img_original,
            realtime_update=True,
            box_color='#0000FF',
            aspect_ratio=(FOTO_LARGURA, FOTO_ALTURA), # Trava o formato da caixa
            should_resize_image=True
        )

with col_dir:
    st.subheader("2. Resultado")
    placeholder = st.empty()
    
    if arquivo_foto and nome_input and imagem_cortada_obj:
        tmpl, fnt = carregar_recursos()
        
        if tmpl:
            # Passamos o nome_input direto (sem .upper())
            img_pronta = processar_arte(imagem_cortada_obj, nome_input, tmpl, fnt)
            img_rgb = img_pronta.convert("RGB")
            
            placeholder.image(img_rgb, caption=f"Convite de {nome_input}", use_container_width=True)
            
            col_b1, col_b2 = st.columns(2)
            
            # Buffers
            pdf_buffer = io.BytesIO()
            img_rgb.save(pdf_buffer, format="PDF", resolution=300.0)
            
            png_buffer = io.BytesIO()
            img_rgb.save(png_buffer, format="PNG")
            
            col_b1.download_button("📄 Baixar PDF", pdf_buffer.getvalue(), f"Convite_{nome_input}.pdf", "application/pdf", use_container_width=True)
            col_b2.download_button("📲 Baixar Imagem", png_buffer.getvalue(), f"Convite_{nome_input}.png", "image/png", use_container_width=True)

    elif not arquivo_foto:
        placeholder.info("👈 Envie sua foto.")
