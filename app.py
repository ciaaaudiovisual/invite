import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont
import io

# ==========================================
# ⚙️ CONFIGURAÇÕES (AJUSTE AQUI)
# ==========================================

# Nomes dos arquivos que você vai subir no GitHub
ARQUIVO_TEMPLATE = "template.png"       # Deve ter o fundo transparente (PNG)
ARQUIVO_FONTE = "fonte_assinatura.ttf"  # Opcional. Se não tiver, o sistema usa uma padrão.

# Configuração da ÁREA DA FOTO (Em pixels, baseado no seu template)
# Você deve medir isso no Photoshop/Paint para ficar perfeito
POSICAO_X = 50          # Distância da esquerda até o começo da foto
POSICAO_Y = 120         # Distância do topo até o começo da foto
LARGURA_FOTO = 400      # Largura do buraco
ALTURA_FOTO = 500       # Altura do buraco
ASPECT_RATIO = (LARGURA_FOTO, ALTURA_FOTO) # Trava a proporção do corte

# Posição do Texto (Nome)
POSICAO_NOME_X = 1200   # Centro horizontal de onde o nome fica
POSICAO_NOME_Y = 900    # Altura vertical do nome
TAMANHO_FONTE = 80      # Tamanho da letra

# ==========================================
# 🛠️ FUNÇÕES DE PROCESSAMENTO
# ==========================================

def carregar_template():
    """Tenta carregar a imagem de fundo. Retorna None se falhar."""
    try:
        return Image.open(ARQUIVO_TEMPLATE).convert("RGBA")
    except FileNotFoundError:
        return None

def criar_convite(foto_usuario, nome_militar):
    """Monta a arte final: Foto + Template + Nome"""
    
    # 1. Carregar Template
    template = carregar_template()
    if not template:
        st.error(f"Erro Crítico: O arquivo '{ARQUIVO_TEMPLATE}' não foi encontrado no repositório.")
        return None

    # 2. Redimensionar a foto cortada para o tamanho exato do buraco
    foto_redimensionada = foto_usuario.resize((LARGURA_FOTO, ALTURA_FOTO))
    foto_redimensionada = foto_redimensionada.convert("RGBA")

    # 3. Criar o Canvas (Tela base transparente)
    convite_final = Image.new("RGBA", template.size)

    # 4. A Mágica do "Sanduíche":
    # Primeiro colamos a foto do militar (no fundo)
    convite_final.paste(foto_redimensionada, (POSICAO_X, POSICAO_Y))
    
    # Depois colamos o template por cima (ele tem o buraco transparente)
    convite_final.paste(template, (0, 0), mask=template)

    # 5. Escrever o Nome
    draw = ImageDraw.Draw(convite_final)
    
    # Tenta carregar a fonte personalizada, senão usa a padrão do sistema
    try:
        font = ImageFont.truetype(ARQUIVO_FONTE, TAMANHO_FONTE)
    except:
        font = ImageFont.load_default()
        st.warning("Aviso: Fonte personalizada não encontrada. Usando fonte padrão.")

    # Escreve o texto centralizado na âncora "mm" (middle-middle)
    draw.text((POSICAO_NOME_X, POSICAO_NOME_Y), nome_militar, font=font, fill="white", anchor="mm")

    return convite_final

# ==========================================
# 📱 INTERFACE DO USUÁRIO (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Gerador de Convite Naval", page_icon="⚓", layout="centered")

st.title("⚓ Convite de Formatura")
st.markdown("Crie seu convite personalizado oficial para a solenidade.")
st.markdown("---")

# Container de Entrada de Dados
col_input, col_crop = st.columns([1, 1.5])

with col_input:
    st.subheader("1. Seus Dados")
    nome_input = st.text_input("Nome de Guerra / Completo", placeholder="Ex: MN Silva")
    arquivo_upload = st.file_uploader("Envie sua foto (Farda)", type=['jpg', 'png', 'jpeg'])

imagem_cortada = None

# Só mostra a ferramenta de corte se tiver foto carregada
if arquivo_upload:
    with col_crop:
        st.subheader("2. Ajuste a Foto")
        st.info("Arraste os cantos da caixa azul para enquadrar seu rosto.")
        
        img_original = Image.open(arquivo_upload)
        
        # Componente de Corte (St_Cropper)
        imagem_cortada = st_cropper(
            img_original,
            realtime_update=True,
            box_color='#0000FF', # Cor da linha azul
            aspect_ratio=ASPECT_RATIO, # Trava a proporção
            should_resize_image=True # Melhora performance em fotos pesadas
        )

st.markdown("---")

# Botão de Gerar (Só ativa se tiver nome e foto)
if nome_input and imagem_cortada:
    if st.button("✨ Gerar Meu Convite", type="primary", use_container_width=True):
        
        with st.spinner("Processando arte em alta resolução..."):
            
            # Chama a função de montagem
            resultado_rgba = criar_convite(imagem_cortada, nome_input)
            
            if resultado_rgba:
                # Converter para RGB (necessário para salvar PDF e JPG corretamente)
                resultado_rgb = resultado_rgba.convert("RGB")
                
                # --- EXIBIÇÃO ---
                st.subheader("3. Resultado Final")
                st.image(resultado_rgb, caption=f"Convite de {nome_input}", use_container_width=True)
                
                # --- ÁREA DE DOWNLOAD ---
                st.success("Convite gerado! Escolha o formato abaixo:")
                
                col_d1, col_d2 = st.columns(2)
                
                # Preparar Buffer PDF
                buffer_pdf = io.BytesIO()
                resultado_rgb.save(buffer_pdf, format="PDF", resolution=300.0)
                
                # Preparar Buffer PNG (Imagem)
                buffer_png = io.BytesIO()
                resultado_rgb.save(buffer_png, format="PNG")
                
                with col_d1:
                    st.download_button(
                        label="📄 Baixar em PDF\n(Para Imprimir)",
                        data=buffer_pdf.getvalue(),
                        file_name=f"Convite_{nome_input}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                with col_d2:
                    st.download_button(
                        label="📲 Baixar Imagem\n(Para WhatsApp)",
                        data=buffer_png.getvalue(),
                        file_name=f"Convite_{nome_input}.png",
                        mime="image/png",
                        use_container_width=True
                    )

elif arquivo_upload and not nome_input:
    st.warning("⚠️ Por favor, digite seu nome acima.")
