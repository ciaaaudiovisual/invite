import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont
import io

# ==============================================================================
# ⚙️ ÁREA DE CONFIGURAÇÃO (AJUSTE AQUI OS DADOS DO SEU TEMPLATE)
# ==============================================================================

# 1. ARQUIVOS (Devem estar na mesma pasta ou raiz do GitHub)
ARQUIVO_TEMPLATE = "template.png"       # O PNG com fundo transparente
ARQUIVO_FONTE = "fonte_assinatura.ttf"  # A fonte cursiva (opcional)

# 2. POSIÇÃO DA FOTO (Onde fica o buraco transparente?)
# Meça isso no Paint/Photoshop (pixels a partir do canto superior esquerdo)
FOTO_POS_X = 50       # Distância da esquerda até o início da foto
FOTO_POS_Y = 120      # Distância do topo até o início da foto
FOTO_LARGURA = 400    # Largura exata do buraco
FOTO_ALTURA = 500     # Altura exata do buraco

# 3. POSIÇÃO DO NOME (Onde o texto será escrito?)
NOME_POS_X = 1200     # Posição horizontal (Centro do texto)
NOME_POS_Y = 900      # Posição vertical (Altura da linha)
TAMANHO_FONTE = 80    # Tamanho da letra
COR_TEXTO = "white"   # Cor do nome (pode ser hex: "#FF0000" ou nome: "black")

# ==============================================================================
# 🛠️ LÓGICA DO SISTEMA (NÃO PRECISA MEXER ABAIXO)
# ==============================================================================

def carregar_recursos():
    """Carrega o template e a fonte com segurança."""
    # Tenta carregar Template
    try:
        template = Image.open(ARQUIVO_TEMPLATE).convert("RGBA")
    except FileNotFoundError:
        st.error(f"❌ ERRO: O arquivo '{ARQUIVO_TEMPLATE}' não foi encontrado.")
        return None, None

    # Tenta carregar Fonte
    try:
        font = ImageFont.truetype(ARQUIVO_FONTE, TAMANHO_FONTE)
    except:
        font = ImageFont.load_default() # Usa padrão se não achar a personalizada
    
    return template, font

def processar_arte_final(foto_cortada, nome_usuario, template, fonte):
    """Monta o sanduíche: Foto + Template + Nome."""
    
    # 1. Ajustar tamanho da foto para caber no buraco
    # Usa LANCZOS para garantir alta qualidade na redução/ampliação
    foto_final = foto_cortada.resize((FOTO_LARGURA, FOTO_ALTURA), Image.LANCZOS)
    foto_final = foto_final.convert("RGBA")
    
    # 2. Criar a base (Canvas)
    canvas = Image.new("RGBA", template.size)
    
    # 3. Colar a Foto (Camada de Baixo)
    canvas.paste(foto_final, (FOTO_POS_X, FOTO_POS_Y))
    
    # 4. Colar o Template (Camada de Cima - com transparência)
    canvas.paste(template, (0, 0), mask=template)
    
    # 5. Escrever o Nome
    draw = ImageDraw.Draw(canvas)
    
    # anchor="mm" centraliza o texto exatamente nas coordenadas X,Y informadas
    draw.text((NOME_POS_X, NOME_POS_Y), nome_usuario, font=fonte, fill=COR_TEXTO, anchor="mm")
    
    return canvas

# ==============================================================================
# 📱 INTERFACE DO USUÁRIO (STREAMLIT)
# ==============================================================================

st.set_page_config(page_title="Gerador de Convite", page_icon="⚓", layout="wide")

st.title("⚓ Gerador de Convite - Visualização Real-Time")
st.markdown("Preencha seus dados à esquerda e veja o resultado instantâneo à direita.")
st.markdown("---")

# Layout de duas colunas: Controles (Esq) e Prévia (Dir)
col_esq, col_dir = st.columns([1, 1.5])

with col_esq:
    st.subheader("1. Seus Dados")
    nome_input = st.text_input("Nome Completo / Guerra", placeholder="Ex: MN Silva")
    arquivo_foto = st.file_uploader("Sua Foto (Farda)", type=['jpg', 'png', 'jpeg'])
    
    imagem_cortada_obj = None
    
    if arquivo_foto:
        st.info("📐 Ajuste a caixa azul para enquadrar seu rosto:")
        img_original = Image.open(arquivo_foto)
        
        # Ferramenta de Corte Interativa
        imagem_cortada_obj = st_cropper(
            img_original,
            realtime_update=True,     # Atualiza enquanto arrasta
            box_color='#0000FF',      # Cor da borda (Azul)
            aspect_ratio=(FOTO_LARGURA, FOTO_ALTURA), # Trava a proporção
            should_resize_image=True  # Otimiza performance
        )

with col_dir:
    st.subheader("2. Resultado Final")
    placeholder = st.empty() # Espaço reservado para a imagem
    
    # Lógica de atualização em Tempo Real
    if arquivo_foto and nome_input and imagem_cortada_obj:
        
        # Carrega recursos e gera imagem
        tmpl, fnt = carregar_recursos()
        if tmpl:
            img_pronta_rgba = processar_arte_final(imagem_cortada_obj, nome_input, tmpl, fnt)
            
            # Converte para RGB (padrão de visualização e PDF)
            img_pronta_rgb = img_pronta_rgba.convert("RGB")
            
            # Mostra na tela
            placeholder.image(img_pronta_rgb, caption=f"Convite de {nome_input}", use_container_width=True)
            
            st.success("✅ Arte pronta! Escolha o formato abaixo:")
            
            # --- BOTÕES DE DOWNLOAD ---
            b1, b2 = st.columns(2)
            
            # Preparar PDF
            pdf_buffer = io.BytesIO()
            img_pronta_rgb.save(pdf_buffer, format="PDF", resolution=300.0)
            
            # Preparar PNG (Imagem)
            png_buffer = io.BytesIO()
            img_pronta_rgb.save(png_buffer, format="PNG")
            
            with b1:
                st.download_button(
                    label="📄 Baixar PDF (Impressão)",
                    data=pdf_buffer.getvalue(),
                    file_name=f"Convite_{nome_input}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with b2:
                st.download_button(
                    label="📲 Baixar Imagem (WhatsApp)",
                    data=png_buffer.getvalue(),
                    file_name=f"Convite_{nome_input}.png",
                    mime="image/png",
                    use_container_width=True
                )
    
    elif not arquivo_foto:
        placeholder.info("👈 Comece enviando sua foto na coluna da esquerda.")
    elif not nome_input:
        placeholder.warning("👈 Digite seu nome para ver a prévia.")
