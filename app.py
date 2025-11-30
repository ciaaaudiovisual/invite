import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont
import io
import os

# ==============================================================================
# ⚙️ ÁREA DE CONFIGURAÇÃO (AJUSTADA PARA 720p E FONTE ABRAMO)
# ==============================================================================

# 1. ARQUIVOS
# ATENÇÃO: O nome do arquivo da fonte aqui deve ser IGUAL ao que está no GitHub
ARQUIVO_TEMPLATE = "template.png"       
ARQUIVO_FONTE = "fonte_assinatura_otf"  # <--- Verifique se o arquivo chama Abramo.ttf ou Abramo.otf

# 2. POSIÇÃO DA FOTO (CONFIGURADO PARA PREENCHER A LATERAL ESQUERDA)
# Baseado na resolução 1280x720
FOTO_POS_X = 0        # Começa no canto esquerdo absoluto
FOTO_POS_Y = 0        # Começa no topo absoluto
FOTO_LARGURA = 640    # Largura (metade da tela para garantir que cobre o fade)
FOTO_ALTURA = 720     # Altura total do template (720p)

# 3. POSIÇÃO DO NOME (Baseado no seu pedido anterior)
NOME_POS_X = 870      
NOME_POS_Y = 645      
TAMANHO_FONTE = 90    # Aumentei um pouco para a fonte Abramo ficar legível
COR_TEXTO = "white"   

# ==============================================================================
# 🛠️ LÓGICA DO SISTEMA
# ==============================================================================

def carregar_recursos():
    # Carregar Template
    try:
        template = Image.open(ARQUIVO_TEMPLATE).convert("RGBA")
    except FileNotFoundError:
        st.error(f"❌ ERRO: Não encontrei o arquivo '{ARQUIVO_TEMPLATE}'.")
        return None, None

    # Carregar Fonte (Lógica mais robusta)
    font = None
    try:
        font = ImageFont.truetype(ARQUIVO_FONTE, TAMANHO_FONTE)
    except OSError:
        # Tenta procurar com .otf se .ttf falhar, ou vice-versa
        try:
            alternativa = ARQUIVO_FONTE.replace(".ttf", ".otf")
            font = ImageFont.truetype(alternativa, TAMANHO_FONTE)
        except:
            st.warning(f"⚠️ A fonte '{ARQUIVO_FONTE}' não foi carregada. Usando padrão.")
            font = ImageFont.load_default()
    
    return template, font

def processar_arte_final(foto_cortada, nome_usuario, template, fonte):
    # 1. Redimensionar foto para a lateral completa (usando LANCZOS para qualidade)
    foto_final = foto_cortada.resize((FOTO_LARGURA, FOTO_ALTURA), Image.LANCZOS)
    foto_final = foto_final.convert("RGBA")
    
    # 2. Criar Canvas
    canvas = Image.new("RGBA", template.size)
    
    # 3. Colar Foto (Fundo)
    canvas.paste(foto_final, (FOTO_POS_X, FOTO_POS_Y))
    
    # 4. Colar Template (Frente)
    # Importante: A parte branca do seu PNG deve ser TRANSPARENTE para a foto aparecer
    canvas.paste(template, (0, 0), mask=template)
    
    # 5. Escrever Nome
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
    st.subheader("1. Seus Dados")
    nome_input = st.text_input("Nome Completo", placeholder="Ex: Cb Fulano")
    arquivo_foto = st.file_uploader("Sua Foto", type=['jpg', 'png', 'jpeg'])
    
    imagem_cortada_obj = None
    
    if arquivo_foto:
        st.info("Ajuste o corte (A foto ocupará toda a lateral esquerda):")
        img_original = Image.open(arquivo_foto)
        
        # Ferramenta de corte travada na proporção da lateral esquerda
        imagem_cortada_obj = st_cropper(
            img_original,
            realtime_update=True,
            box_color='#0000FF',
            aspect_ratio=(FOTO_LARGURA, FOTO_ALTURA),
            should_resize_image=True
        )

with col_dir:
    st.subheader("2. Resultado")
    placeholder = st.empty()
    
    if arquivo_foto and nome_input and imagem_cortada_obj:
        tmpl, fnt = carregar_recursos()
        
        if tmpl:
            img_pronta = processar_arte_final(imagem_cortada_obj, nome_input, tmpl, fnt)
            img_rgb = img_pronta.convert("RGB")
            
            placeholder.image(img_rgb, caption=f"Convite de {nome_input}", use_container_width=True)
            
            col_b1, col_b2 = st.columns(2)
            
            # PDF Buffer
            pdf_buffer = io.BytesIO()
            img_rgb.save(pdf_buffer, format="PDF", resolution=300.0)
            
            # PNG Buffer
            png_buffer = io.BytesIO()
            img_rgb.save(png_buffer, format="PNG")
            
            col_b1.download_button("📄 Baixar PDF", pdf_buffer.getvalue(), f"Convite_{nome_input}.pdf", "application/pdf", use_container_width=True)
            col_b2.download_button("📲 Baixar Imagem", png_buffer.getvalue(), f"Convite_{nome_input}.png", "image/png", use_container_width=True)

    elif not arquivo_foto:
        placeholder.info("👈 Envie sua foto primeiro.")
