import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image  # Importante: Instale com 'pip install Pillow'
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import base64  # Para codificar imagens para a API da OpenAI

OPENAI_API_KEY = "sua-chave-aqui"

# Importar a biblioteca OpenAI (pip install openai)
try:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    messagebox.showerror("Erro",
                         "A biblioteca 'openai' não está instalada. Por favor, instale com 'pip install openai'.")
    client = None
except Exception as e:
    messagebox.showerror("Erro na OpenAI",
                         f"Não foi possível inicializar a API da OpenAI: {e}\nVerifique sua OPENAI_API_KEY.")
    client = None

"""
Classificador de Insetos para Vigilância em Saúde Pública com IA e GUI

Objetivo didático:
- Coletar respostas (Sim/Não) sobre características morfológicas e hábitos de insetos.
- Aplicar regras de decisão para classificar o inseto quanto ao risco de transmissão de doenças.
- Exibir resultado + resumo das respostas, deixando o algoritmo transparente.
- Adicionar opção de classificação por imagem usando IA (OpenAI GPT-4o) como um entomologista.
"""


# =========================
# 1) MODELO DE DADOS
# =========================
@dataclass(frozen=True)
class Question:
    """
    Estrutura IMUTÁVEL (frozen=True) para organizar as perguntas do quiz.

    Campos:
    - text: pergunta exibida ao usuário
    - key: chave usada para salvar a resposta no dicionário `answers`
    - image: caminho da imagem ilustrativa
    """
    text: str
    key: str
    image: str


# =========================
# 2) MOTOR (LÓGICA)
# =========================
class InsectClassifierEngine:
    """
    Motor de classificação (lógica do algoritmo) para insetos.
    """

    RESULT_UNKNOWN = "Não foi possível classificar o risco."
    RESULT_HIGH_RISK = "VETOR DE DOENÇA (ALTO RISCO) 🚨"
    RESULT_LOW_RISK = "INSETO COMUM (BAIXO RISCO) ✅"
    RESULT_BENEFICIAL = "ESPÉCIE BENÉFICA 🌼"

    def classify(self, answers: Dict[str, str]) -> str:
        """
        Recebe um dicionário com respostas 'sim'/'nao' e aplica regras para classificar o risco do inseto.

        Regras de classificação (simplificadas para fins didáticos):
        - ALTO RISCO (Vetor):
            - Aedes aegypti: tem asas + tamanho pequeno + patas listradas + voa de dia + água parada
            - Anopheles: tem asas + tamanho pequeno + asas com manchas + voa à noite + água limpa
            - Barbeiro: sem asas (adulto pode ter) + corpo achatado + hábitos noturnos + frestas de parede
        - BENEFÍCIO:
            - Abelha: tem asas + corpo peludo + pólen nas patas + voa de dia + flores
        - BAIXO RISCO: Se não se encaixa nos anteriores, é considerado de baixo risco.
        """
        ans = answers
        result_text = self.RESULT_UNKNOWN

        # --- Lógica para Aedes aegypti (Dengue, Zika, Chikungunya) ---
        if ans.get("tem_asas") == "sim" and ans.get("tamanho_pequeno") == "sim":
            if ans.get("patas_listradas") == "sim" and ans.get("voa_dia") == "sim":
                if ans.get("ambiente_agua_parada") == "sim":
                    result_text = self.RESULT_HIGH_RISK  # Aedes aegypti

        # --- Lógica para Anopheles (Malária) ---
        if result_text == self.RESULT_UNKNOWN:  # Se ainda não classificou
            if ans.get("tem_asas") == "sim" and ans.get("tamanho_pequeno") == "sim":
                if ans.get("asas_manchas") == "sim" and ans.get("voa_noite") == "sim":
                    if ans.get("ambiente_agua_limpa") == "sim":
                        result_text = self.RESULT_HIGH_RISK  # Anopheles

        # --- Lógica para Barbeiro (Doença de Chagas) ---
        if result_text == self.RESULT_UNKNOWN:  # Se ainda não classificou
            if ans.get("corpo_achatado") == "sim" and ans.get("habitos_noturnos") == "sim":
                if ans.get("ambiente_frestas_parede") == "sim":
                    result_text = self.RESULT_HIGH_RISK  # Barbeiro

        # --- Lógica para Abelhas (Benéficas) ---
        if result_text == self.RESULT_UNKNOWN:  # Se ainda não classificou
            if ans.get("tem_asas") == "sim" and ans.get("corpo_peludo") == "sim":
                if ans.get("polen_patas") == "sim" and ans.get("voa_dia") == "sim":
                    if ans.get("ambiente_flores") == "sim":
                        result_text = self.RESULT_BENEFICIAL  # Abelha

        # --- Lógica para Inseto Comum (Baixo Risco) ---
        if result_text == self.RESULT_UNKNOWN:  # Se ainda não classificou e não é vetor nem benéfico
            # Se tem asas e não é nenhum dos vetores ou benéficos específicos
            if ans.get("tem_asas") == "sim" or ans.get("tamanho_pequeno") == "sim":
                result_text = self.RESULT_LOW_RISK
            # Se não tem asas, mas não é barbeiro
            elif ans.get("tem_asas") == "nao" and ans.get("corpo_achatado") == "nao":
                result_text = self.RESULT_LOW_RISK
            # Se não tem nenhuma característica marcante
            else:
                result_text = self.RESULT_UNKNOWN

        return result_text


# =========================
# 3) GUI (INTERFACE) - TELAS
# =========================

class StartScreen(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.pack(fill="both", expand=True)

        self.label_title = ctk.CTkLabel(
            self,
            text="Vigilância Entomológica - Sentinela",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        self.label_title.pack(pady=50)

        self.btn_quiz = ctk.CTkButton(
            self,
            text="1 - Classificação Manual (Quiz)",
            command=self.app.show_quiz_screen,
            font=ctk.CTkFont(size=20, weight="bold"),
            width=300,
            height=60,
            fg_color="#007bff",
            hover_color="#0056b3",
        )
        self.btn_quiz.pack(pady=20)

        self.btn_ia = ctk.CTkButton(
            self,
            text="2 - Classificação por IA (Foto)",
            command=self.app.show_ia_screen,
            font=ctk.CTkFont(size=20, weight="bold"),
            width=300,
            height=60,
            fg_color="#28a745",
            hover_color="#218838",
        )
        self.btn_ia.pack(pady=20)


class QuizScreen(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.engine = InsectClassifierEngine()

        # -------------------------
        # Estado do aplicativo
        # -------------------------
        self.current_question_key: Optional[str] = None
        self.answers: Dict[str, str] = {}
        self.question_history: List[str] = []

        # -------------------------
        # Dados: perguntas e imagens
        # -------------------------
        self.all_questions: Dict[str, Question] = {
            "tem_asas": Question("O inseto possui asas?", "tem_asas", "imagens/inseto_asas.png"),
            "tamanho_pequeno": Question("O inseto é de tamanho pequeno (aprox. 0.5-1cm)?", "tamanho_pequeno",
                                        "imagens/inseto_pequeno.png"),
            "patas_listradas": Question("As patas do inseto possuem listras brancas e pretas?", "patas_listradas",
                                        "imagens/aedes_patas.png"),
            "voa_dia": Question("O inseto voa predominantemente durante o dia?", "voa_dia", "imagens/voa_dia.png"),
            "ambiente_agua_parada": Question("Foi encontrado em ambiente com água parada (vasos, pneus)?",
                                             "ambiente_agua_parada", "imagens/agua_parada.png"),
            "asas_manchas": Question("As asas do inseto possuem manchas escuras?", "asas_manchas",
                                     "imagens/anopheles_asas.png"),
            "voa_noite": Question("O inseto voa predominantemente durante a noite?", "voa_noite",
                                  "imagens/voa_noite.png"),
            "ambiente_agua_limpa": Question("Foi encontrado em ambiente com água limpa (rios, lagos)?",
                                            "ambiente_agua_limpa", "imagens/agua_limpa.png"),
            "corpo_achatado": Question("O corpo do inseto é achatado e ovalado?", "corpo_achatado",
                                       "imagens/barbeiro_corpo.png"),
            "habitos_noturnos": Question("O inseto possui hábitos noturnos (sai à noite)?", "habitos_noturnos",
                                         "imagens/habitos_noturnos.png"),
            "ambiente_frestas_parede": Question("Foi encontrado em frestas de parede, colchões ou móveis?",
                                                "ambiente_frestas_parede", "imagens/frestas_parede.png"),
            "corpo_peludo": Question("O corpo do inseto é visivelmente peludo?", "corpo_peludo",
                                     "imagens/abelha_pelos.png"),
            "polen_patas": Question("O inseto possui 'bolsas' de pólen nas patas traseiras?", "polen_patas",
                                    "imagens/abelha_polen.png"),
            "ambiente_flores": Question("Foi encontrado em ambiente com flores ou vegetação?", "ambiente_flores",
                                        "imagens/flores.png"),
        }

        # Imagens para o resultado final
        self.result_images: Dict[str, str] = {
            InsectClassifierEngine.RESULT_HIGH_RISK: "imagens/resultado_alto_risco.jpg",
            InsectClassifierEngine.RESULT_LOW_RISK: "imagens/resultado_baixo_risco.jpg",
            InsectClassifierEngine.RESULT_BENEFICIAL: "imagens/resultado_benefico.jpg",
            InsectClassifierEngine.RESULT_UNKNOWN: "imagens/resultado_desconhecido.jpg",
        }

        self.total_questions = len(self.all_questions)

        # Monta a UI
        self._build_ui()

    def _build_ui(self) -> None:
        # Card onde ficam imagem e pergunta
        self.question_card_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("white", "#333333"))
        self.question_card_frame.pack(pady=20, padx=30, fill="both", expand=True)

        # Label para imagem
        self.image_display = ctk.CTkLabel(self.question_card_frame, text="", width=450, height=250)
        self.image_display.pack(pady=15)

        # Label para texto da pergunta
        self.label_question = ctk.CTkLabel(
            self.question_card_frame,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            wraplength=450,
        )
        self.label_question.pack(pady=15)

        # Frame de botões
        self.frame_buttons = ctk.CTkFrame(self.question_card_frame, fg_color="transparent")
        self.frame_buttons.pack(pady=10)

        # Botão VOLTAR (UX)
        self.btn_voltar = ctk.CTkButton(
            self.frame_buttons,
            text="Voltar",
            command=self.go_back,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=140,
            height=45,
        )
        self.btn_voltar.pack(side=ctk.LEFT, padx=10)

        # Botão SIM
        self.btn_sim = ctk.CTkButton(
            self.frame_buttons,
            text="Sim",
            command=lambda: self.process_answer("sim"),
            fg_color="#28a745",
            hover_color="#218838",
            width=140,
            height=45,
        )
        self.btn_sim.pack(side=ctk.LEFT, padx=10)

        # Botão NÃO
        self.btn_nao = ctk.CTkButton(
            self.frame_buttons,
            text="Não",
            command=lambda: self.process_answer("nao"),
            fg_color="#dc3545",
            hover_color="#c82333",
            width=140,
            height=45,
        )
        self.btn_nao.pack(side=ctk.LEFT, padx=10)

        # Label de resultado (abaixo do card)
        self.label_result = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#007bff",
        )
        self.label_result.pack(pady=20)

        # Botão de reiniciar (aparece no final)
        self.btn_restart = ctk.CTkButton(
            self,
            text="Reiniciar Classificação",
            command=self.start_quiz,
            fg_color="gray",
        )

        # Botão para voltar ao menu principal
        self.btn_back_to_menu = ctk.CTkButton(
            self,
            text="Voltar ao Menu Principal",
            command=self.app.show_start_screen,
            fg_color="#6c757d",
            hover_color="#5a6268",
        )
        self.btn_back_to_menu.pack(pady=10)

    # =========================
    # Helpers (imagens e UI)
    # =========================
    def _load_image(self, path: str) -> Optional[ctk.CTkImage]:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize((450, 250), Image.LANCZOS)
                return ctk.CTkImage(light_image=img, dark_image=img, size=(450, 250))
            except Exception as e:
                print(f"Erro ao carregar imagem {path}: {e}")
        return None

    def _set_question_view(self, question: Question) -> None:
        self.label_question.configure(text=question.text)

        img = self._load_image(question.image)
        if img:
            self.image_display.configure(image=img, text="")
        else:
            self.image_display.configure(image=None, text="[Imagem não encontrada]")

    def _update_progress(self) -> None:
        # O progresso agora é baseado no número de perguntas no histórico
        # O total de perguntas é o número de chaves em self.all_questions
        if self.all_questions:
            self.app.progress_bar.set(len(self.question_history) / len(self.all_questions))
        else:
            self.app.progress_bar.set(0)

    def _update_back_button(self) -> None:
        self.btn_voltar.configure(state="disabled" if not self.question_history else "normal")

    # =========================
    # Fluxo do Questionário (Lógica de Decisão Dinâmica)
    # =========================
    def start_quiz(self) -> None:
        self.answers = {}
        self.question_history = []
        self.label_result.configure(text="")
        self.btn_restart.pack_forget()
        self.app.progress_bar.set(0)
        self.image_display.configure(image=None, text="")
        self.current_question_key = "tem_asas"  # Começa com a primeira pergunta de insetos
        self.show_current_question()

    def show_current_question(self) -> None:
        if self.current_question_key is None:
            self.finish_and_show_result()
            return

        question = self.all_questions[self.current_question_key]
        self.frame_buttons.pack(pady=10)
        self._update_back_button()
        self._set_question_view(question)
        self._update_progress()

    def process_answer(self, answer: str) -> None:
        if self.current_question_key:
            self.answers[self.current_question_key] = answer
            self.question_history.append(self.current_question_key)

        self.current_question_key = self._get_next_question_key()
        self.show_current_question()

    def go_back(self) -> None:
        if self.question_history:
            last_question_key = self.question_history.pop()
            if last_question_key in self.answers:
                del self.answers[last_question_key]

            if self.question_history:
                self.current_question_key = self.question_history[-1]
            else:
                self.current_question_key = "tem_asas"  # Volta para a primeira pergunta
            self.show_current_question()

    def _get_next_question_key(self) -> Optional[str]:
        ans = self.answers

        # --- Lógica de decisão para determinar a próxima pergunta (Entomologia) ---

        # Pergunta inicial: Asas?
        if ans.get("tem_asas") is None: return "tem_asas"

        # --- Caminho para Insetos com Asas ---
        if ans.get("tem_asas") == "sim":
            if ans.get("tamanho_pequeno") is None: return "tamanho_pequeno"

            if ans.get("tamanho_pequeno") == "sim":  # Potencial Aedes ou Anopheles
                if ans.get("patas_listradas") is None: return "patas_listradas"
                if ans.get("patas_listradas") == "sim":  # Potencial Aedes
                    if ans.get("voa_dia") is None: return "voa_dia"
                    if ans.get("voa_dia") == "sim":
                        if ans.get("ambiente_agua_parada") is None: return "ambiente_agua_parada"
                        if ans.get("ambiente_agua_parada") == "sim":
                            return None  # Classifica como Aedes (Alto Risco)

                # Se não tem patas listradas, verifica Anopheles
                if ans.get("asas_manchas") is None: return "asas_manchas"
                if ans.get("asas_manchas") == "sim":  # Potencial Anopheles
                    if ans.get("voa_noite") is None: return "voa_noite"
                    if ans.get("voa_noite") == "sim":
                        if ans.get("ambiente_agua_limpa") is None: return "ambiente_agua_limpa"
                        if ans.get("ambiente_agua_limpa") == "sim":
                            return None  # Classifica como Anopheles (Alto Risco)

                # Se não é Aedes nem Anopheles, mas tem asas e é pequeno, pode ser Abelha ou Comum
                if ans.get("corpo_peludo") is None: return "corpo_peludo"
                if ans.get("corpo_peludo") == "sim":  # Potencial Abelha
                    if ans.get("polen_patas") is None: return "polen_patas"
                    if ans.get("polen_patas") == "sim":
                        if ans.get("voa_dia") is None: return "voa_dia"
                        if ans.get("voa_dia") == "sim":
                            if ans.get("ambiente_flores") is None: return "ambiente_flores"
                            if ans.get("ambiente_flores") == "sim":
                                return None  # Classifica como Abelha (Benéfica)

                # Se tem asas, é pequeno, mas não é vetor nem abelha específica
                return None  # Classifica como Inseto Comum (Baixo Risco)

            elif ans.get("tamanho_pequeno") == "nao":  # Inseto com asas, mas não pequeno (ex: libélula, borboleta)
                # Pode ser um inseto comum ou benéfico, mas não um vetor clássico
                if ans.get("corpo_peludo") is None: return "corpo_peludo"
                if ans.get("corpo_peludo") == "sim":  # Potencial Abelha maior
                    if ans.get("polen_patas") is None: return "polen_patas"
                    if ans.get("polen_patas") == "sim":
                        if ans.get("voa_dia") is None: return "voa_dia"
                        if ans.get("voa_dia") == "sim":
                            if ans.get("ambiente_flores") is None: return "ambiente_flores"
                            if ans.get("ambiente_flores") == "sim":
                                return None  # Classifica como Abelha (Benéfica)
                return None  # Classifica como Inseto Comum (Baixo Risco)

        # --- Caminho para Insetos sem Asas (Potencial Barbeiro) ---
        elif ans.get("tem_asas") == "nao":
            if ans.get("corpo_achatado") is None: return "corpo_achatado"
            if ans.get("corpo_achatado") == "sim":  # Potencial Barbeiro
                if ans.get("habitos_noturnos") is None: return "habitos_noturnos"
                if ans.get("habitos_noturnos") == "sim":
                    if ans.get("ambiente_frestas_parede") is None: return "ambiente_frestas_parede"
                    if ans.get("ambiente_frestas_parede") == "sim":
                        return None  # Classifica como Barbeiro (Alto Risco)

            # Se não tem asas e não é barbeiro, pode ser uma larva ou outro inseto sem asas de baixo risco
            return None  # Classifica como Inseto Comum (Baixo Risco)

        return None  # Se chegou aqui, não há mais perguntas relevantes ou não foi possível classificar

    def finish_and_show_result(self) -> None:
        result_text = self.engine.classify(self.answers)

        self.label_question.configure(text="Classificação Concluída!")
        self.frame_buttons.pack_forget()
        self.label_result.configure(text=f"Resultado: {result_text}")
        self.btn_restart.pack(pady=20)
        self.app.progress_bar.set(1)

        final_image_path = self.result_images.get(result_text, self.result_images[self.engine.RESULT_UNKNOWN])
        final_photo = self._load_image(final_image_path)
        if final_photo:
            self.image_display.configure(image=final_photo, text="")
        else:
            self.image_display.configure(image=None, text="[Imagem de resultado não encontrada]")

        messagebox.showinfo("Classificação Concluída", f"Resultado: {result_text}")


class IAScreen(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.engine = InsectClassifierEngine()  # Usar o mesmo motor para classificação final
        self.image_path = None

        self.label_title = ctk.CTkLabel(
            self,
            text="Classificação por IA (Foto)",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.label_title.pack(pady=20)

        self.image_display = ctk.CTkLabel(self, text="", width=450, height=250, fg_color=("white", "#333333"))
        self.image_display.pack(pady=15)

        self.btn_select_image = ctk.CTkButton(
            self,
            text="Selecionar Imagem",
            command=self.select_image,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#007bff",
            hover_color="#0056b3",
        )
        self.btn_select_image.pack(pady=10)

        self.btn_classify_ia = ctk.CTkButton(
            self,
            text="Classificar com IA",
            command=self.classify_with_ia,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838",
            state="disabled"  # Desabilitado até uma imagem ser selecionada
        )
        self.btn_classify_ia.pack(pady=10)

        self.label_result = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=20),  # Reduzir um pouco a fonte para caber mais texto
            text_color="#007bff",
            wraplength=550  # Aumentar o wraplength para caber a justificativa da IA
        )
        self.label_result.pack(pady=20)

        self.btn_back_to_menu = ctk.CTkButton(
            self,
            text="Voltar ao Menu Principal",
            command=self.app.show_start_screen,
            fg_color="#6c757d",
            hover_color="#5a6268",
        )
        self.btn_back_to_menu.pack(pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecione uma imagem de inseto",
            filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.image_path = file_path
            img = self._load_image(self.image_path, size=(450, 250))
            if img:
                self.image_display.configure(image=img, text="")
                self.btn_classify_ia.configure(state="normal")
            else:
                self.image_display.configure(image=None, text="[Erro ao carregar imagem]")
                self.btn_classify_ia.configure(state="disabled")
            self.label_result.configure(text="")

    def _load_image(self, path: str, size: tuple) -> Optional[ctk.CTkImage]:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize(size, Image.LANCZOS)
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            except Exception as e:
                print(f"Erro ao carregar imagem {path}: {e}")
        return None

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def classify_with_ia(self):
        if not client:
            messagebox.showerror("Erro", "A API da OpenAI não foi inicializada. Verifique sua chave de API.")
            return
        if not self.image_path:
            messagebox.showwarning("Aviso", "Por favor, selecione uma imagem primeiro.")
            return

        self.label_result.configure(text="Analisando imagem com IA...", text_color="orange")
        self.update_idletasks()  # Atualiza a UI para mostrar a mensagem

        try:
            base64_image = self.encode_image(self.image_path)

            response = client.chat.completions.create(
                model="gpt-4o",  # Modelo mais recente com visão
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text",
                             "text": "Você é um entomologista especialista em saúde pública. Analise a imagem de um inseto. Classifique-o como 'VETOR DE DOENÇA (ALTO RISCO)', 'INSETO COMUM (BAIXO RISCO)' ou 'ESPÉCIE BENÉFICA'. Justifique sua resposta detalhadamente com base nas características morfológicas (asas, patas, corpo, coloração, tamanho) e, se possível, nos hábitos ou ambiente que a imagem sugere. Se não for possível classificar com certeza, diga 'Não foi possível classificar o risco.'"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=500,  # Aumentar para permitir justificativas mais longas
            )
            ia_response = response.choices[0].message.content
            self.label_result.configure(text=f"Classificação da IA:\n{ia_response}", text_color="#007bff")

        except Exception as e:
            messagebox.showerror("Erro na IA", f"Ocorreu um erro ao classificar a imagem com IA: {e}")
            self.label_result.configure(text="Erro na classificação por IA.", text_color="red")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vigilância Entomológica - Sentinela")
        self.geometry("700x750")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Barra de progresso global (visível em todas as telas)
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.start_screen = StartScreen(self, self)
        self.quiz_screen = QuizScreen(self, self)
        self.ia_screen = IAScreen(self, self)

        self.show_start_screen()

    def show_start_screen(self):
        self.quiz_screen.pack_forget()
        self.ia_screen.pack_forget()
        self.start_screen.pack(fill="both", expand=True)
        self.progress_bar.pack_forget()  # Esconde a barra de progresso no menu inicial

    def show_quiz_screen(self):
        self.start_screen.pack_forget()
        self.ia_screen.pack_forget()
        self.quiz_screen.pack(fill="both", expand=True)
        self.quiz_screen.start_quiz()  # Inicia o quiz ao mostrar a tela
        self.progress_bar.pack(pady=10)  # Mostra a barra de progresso no quiz

    def show_ia_screen(self):
        self.start_screen.pack_forget()
        self.quiz_screen.pack_forget()
        self.ia_screen.pack(fill="both", expand=True)
        self.ia_screen.label_result.configure(text="")  # Limpa o resultado anterior
        self.ia_screen.image_display.configure(image=None, text="Selecione uma imagem")
        self.ia_screen.btn_classify_ia.configure(state="disabled")
        self.progress_bar.pack_forget()  # Esconde a barra de progresso na tela de IA


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
