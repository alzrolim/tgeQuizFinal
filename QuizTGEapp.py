"""
Quiz TGE APP 2025 - Versão Refatorada com Janelas Melhoradas
Sistema de quiz com interface gráfica usando Tkinter e SQLite
"""

import sqlite3
import random
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


# --------------------- Constantes e Configurações ---------------------
class Config:
    """Configurações globais da aplicação"""
    WINDOW_WIDTH_RATIO = 0.7
    WINDOW_HEIGHT_RATIO = 0.7
    BACKGROUND_COLOR = "#1e1e1e"
    TEXT_COLOR = "#ffffff"
    SECONDARY_TEXT_COLOR = "#cccccc"
    BUTTON_COLOR = "#333333"
    SUCCESS_COLOR = "#4CAF50"
    ERROR_COLOR = "#f44336"
    
    # Proporções de questões
    SPECIFIC_QUESTIONS_RATIO = 0.6
    
    # Percentuais de desempenho
    EXCELLENT_THRESHOLD = 70
    GOOD_THRESHOLD = 50


class DatabasePath:
    """Caminhos dos bancos de dados"""
    SPECIFIC_QUESTIONS = 'questoesEspecificas.db'
    GENERAL_QUESTIONS = 'questoesGerais.db'


# --------------------- Modelos de Dados ---------------------
@dataclass
class Question:
    """Representa uma questão do quiz"""
    id: int
    numero: int
    enunciado: str
    alternativa_a: str
    alternativa_b: str
    alternativa_c: str
    alternativa_d: str
    fonte: str
    gabarito: str
    
    def get_alternatives(self) -> dict:
        """Retorna um dicionário com as alternativas"""
        return {
            'a': self.alternativa_a,
            'b': self.alternativa_b,
            'c': self.alternativa_c,
            'd': self.alternativa_d
        }


class PerformanceLevel(Enum):
    """Níveis de desempenho do usuário"""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"


# --------------------- Gerenciador de Dados ---------------------
class DatabaseManager:
    """Gerencia operações com banco de dados"""
    
    @staticmethod
    def load_questions(database_path: str) -> List[Question]:
        """Carrega questões do banco de dados"""
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, numero, enunciado, alternativa_a, alternativa_b, 
                       alternativa_c, alternativa_d, fonte, gabarito 
                FROM questoes
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            return [Question(*row) for row in rows]
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco", f"Erro ao carregar questões: {e}")
            return []


class QuestionManager:
    """Gerencia a seleção e preparação das questões"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def prepare_questions(self, total_questions: int) -> List[Question]:
        """Prepara questões misturadas de ambos os bancos"""
        specific_questions = self.db_manager.load_questions(DatabasePath.SPECIFIC_QUESTIONS)
        general_questions = self.db_manager.load_questions(DatabasePath.GENERAL_QUESTIONS)
        
        random.shuffle(specific_questions)
        random.shuffle(general_questions)
        
        num_specific = int(total_questions * Config.SPECIFIC_QUESTIONS_RATIO)
        num_general = total_questions - num_specific
        
        selected_questions = (
            specific_questions[:num_specific] + 
            general_questions[:num_general]
        )
        
        random.shuffle(selected_questions)
        return selected_questions


# --------------------- Janela Personalizada de Resultado ---------------------
class CustomResultDialog:
    """Janela personalizada para mostrar resultado de cada questão"""
    
    def __init__(self, parent, is_correct: bool, correct_answer: str = None, user_answer: str = None):
        self.parent = parent
        self.is_correct = is_correct
        self.correct_answer = correct_answer
        self.user_answer = user_answer
        self.result = None
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Cria a janela de diálogo personalizada"""
        # Criar janela
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Resultado da Questão")
        self.dialog.configure(bg=Config.BACKGROUND_COLOR)
        
        # Configurar tamanho e posição
        dialog_width, dialog_height = 500, 400
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        pos_x = parent_x + (parent_width - dialog_width) // 2
        pos_y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")
        self.dialog.resizable(False, False)
        
        # Tornar modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Configurar cor de fundo baseada no resultado
        bg_color = Config.SUCCESS_COLOR if self.is_correct else Config.ERROR_COLOR
        
        # Frame principal com borda colorida
        main_frame = tk.Frame(
            self.dialog,
            bg=bg_color,
            padx=3,
            pady=3
        )
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame interno
        inner_frame = tk.Frame(
            main_frame,
            bg=Config.BACKGROUND_COLOR,
            padx=20,
            pady=15
        )
        inner_frame.pack(fill='both', expand=True)
        
        # Ícone e título
        self._create_header(inner_frame)
        
        # Mensagem principal
        self._create_message(inner_frame)
        
        # Botão de continuar
        self._create_button(inner_frame)
        
        # Configurar eventos
        self.dialog.bind('<Return>', lambda e: self._continue())
        self.dialog.bind('<Escape>', lambda e: self._continue())
        self.dialog.focus_set()
    
    def _create_header(self, parent):
        """Cria o cabeçalho com ícone e título"""
        header_frame = tk.Frame(parent, bg=Config.BACKGROUND_COLOR)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Ícone grande usando caracteres Unicode
        if self.is_correct:
            icon = "✅"
            title = "CORRETO!"
            color = Config.SUCCESS_COLOR
        else:
            icon = "❌"
            title = "INCORRETO!"
            color = Config.ERROR_COLOR
        
        # Ícone
        icon_label = tk.Label(
            header_frame,
            text=icon,
            font=("Arial", 36),
            bg=Config.BACKGROUND_COLOR,
            fg=color
        )
        icon_label.pack(pady=(0, 5))
        
        # Título
        title_label = tk.Label(
            header_frame,
            text=title,
            font=("Arial", 16, "bold"),
            bg=Config.BACKGROUND_COLOR,
            fg=color
        )
        title_label.pack()
    
    def _create_message(self, parent):
        """Cria a mensagem de resultado"""
        message_frame = tk.Frame(parent, bg=Config.BACKGROUND_COLOR)
        message_frame.pack(fill='x', pady=(0, 15))
        
        if self.is_correct:
            message = "Parabéns! Você acertou esta questão!"
            message_color = Config.SUCCESS_COLOR
        else:
            message = f"Resposta incorreta.\n\nSua resposta: {self.user_answer.upper()}\nResposta correta: {self.correct_answer.upper()}"
            message_color = Config.ERROR_COLOR
        
        message_label = tk.Label(
            message_frame,
            text=message,
            font=("Arial", 11),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_COLOR,
            justify="center"
        )
        message_label.pack()
        
        # Linha decorativa
        line_frame = tk.Frame(
            message_frame,
            height=2,
            bg=message_color
        )
        line_frame.pack(fill='x', pady=(10, 0))
    
    def _create_button(self, parent):
        """Cria o botão de continuar"""
        button_frame = tk.Frame(parent, bg=Config.BACKGROUND_COLOR)
        button_frame.pack(fill='x')
        
        # Usar "Continuar" para ambos os casos
        button_text = "Continuar"
        
        continue_button = tk.Button(
            button_frame,
            text=button_text,
            font=("Arial", 12, "bold"),
            bg=Config.SUCCESS_COLOR if self.is_correct else Config.ERROR_COLOR,
            fg=Config.TEXT_COLOR,
            width=20,
            height=2,
            command=self._continue,
            cursor="hand2"
        )
        continue_button.pack(pady=10)
        
        # Efeito hover
        def on_enter(e):
            continue_button.config(bg="#45a049" if self.is_correct else "#da190b")
        
        def on_leave(e):
            continue_button.config(bg=Config.SUCCESS_COLOR if self.is_correct else Config.ERROR_COLOR)
        
        continue_button.bind("<Enter>", on_enter)
        continue_button.bind("<Leave>", on_leave)
    
    def _continue(self):
        """Fecha a janela e continua o quiz"""
        self.dialog.destroy()
    
    def show(self):
        """Mostra a janela e aguarda o usuário"""
        self.dialog.wait_window()


# --------------------- Utilitários de Interface ---------------------
class WindowUtils:
    """Utilitários para configuração de janelas"""
    
    @staticmethod
    def configure_window(window: tk.Tk, title: str = "Quiz TGE APP 2025") -> Tuple[int, int]:
        """Configura dimensões e posição da janela"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        window_width = int(screen_width * Config.WINDOW_WIDTH_RATIO)
        window_height = int(screen_height * Config.WINDOW_HEIGHT_RATIO)
        
        pos_x = screen_width - window_width
        pos_y = int((screen_height - window_height) / 2)
        
        window.title(title)
        window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        window.configure(bg=Config.BACKGROUND_COLOR)
        
        return window_width, window_height


class PerformanceEvaluator:
    """Avalia o desempenho do usuário"""
    
    @staticmethod
    def evaluate_performance(correct_answers: int, total_questions: int) -> Tuple[float, PerformanceLevel, str]:
        """Avalia o desempenho e retorna percentual, nível e mensagem"""
        percentage = (correct_answers / total_questions) * 100
        
        if percentage >= Config.EXCELLENT_THRESHOLD:
            level = PerformanceLevel.EXCELLENT
            message = "🎉 Parabéns! Excelente desempenho!"
        elif percentage >= Config.GOOD_THRESHOLD:
            level = PerformanceLevel.GOOD
            message = "👍 Bom trabalho! Continue estudando!"
        else:
            level = PerformanceLevel.NEEDS_IMPROVEMENT
            message = "📚 Continue estudando para melhorar!"
        
        return percentage, level, message


# --------------------- Tela Inicial ---------------------
class InitialScreen:
    """Tela inicial para configuração do quiz"""
    
    def __init__(self, master: tk.Tk):
        self.master = master
        self.width, self.height = WindowUtils.configure_window(master)
        self.quantity_var = tk.IntVar(value=40)
        
        self._create_interface()
    
    def _create_interface(self):
        """Cria a interface da tela inicial"""
        main_frame = tk.Frame(self.master, bg=Config.BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill='both')
        
        center_frame = tk.Frame(main_frame, bg=Config.BACKGROUND_COLOR)
        center_frame.pack(expand=True)
        
        # Título
        title_label = tk.Label(
            center_frame,
            text="Quiz TGE APP 2025",
            font=("Arial", 18, "bold"),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_COLOR
        )
        title_label.pack(pady=30)
        
        # Instrução
        instruction_label = tk.Label(
            center_frame,
            text="Escolha a quantidade de questões:",
            font=("Arial", 14),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.SECONDARY_TEXT_COLOR
        )
        instruction_label.pack(pady=15)
        
        # Dropdown de quantidade
        options = [10, 20, 30, 40, 50]
        self.dropdown = ttk.Combobox(
            center_frame,
            textvariable=self.quantity_var,
            values=options,
            font=("Arial", 12),
            state="readonly",
            width=15
        )
        self.dropdown.pack(pady=15)
        
        # Botão iniciar
        start_button = tk.Button(
            center_frame,
            text="Iniciar Quiz",
            font=("Arial", 14, "bold"),
            bg=Config.BUTTON_COLOR,
            fg=Config.TEXT_COLOR,
            width=20,
            height=2,
            command=self._start_quiz
        )
        start_button.pack(pady=30)
    
    def _start_quiz(self):
        """Inicia o quiz com a quantidade selecionada"""
        total = self.quantity_var.get()
        if total <= 0:
            messagebox.showerror("Erro", "Escolha uma quantidade válida.")
            return
        
        self.master.destroy()
        QuizApplication(total)


# --------------------- Aplicação Principal do Quiz ---------------------
class QuizApplication:
    """Aplicação principal do quiz"""
    
    def __init__(self, total_questions: int):
        self.total_questions = total_questions
        self.current_index = 0
        self.correct_answers = 0
        self.is_quiz_active = True
        
        # Gerenciadores
        self.question_manager = QuestionManager()
        self.performance_evaluator = PerformanceEvaluator()
        
        # Preparar questões
        self.questions = self.question_manager.prepare_questions(total_questions)
        self.current_correct_answer: Optional[str] = None
        
        # Interface
        self.root = tk.Tk()
        self.width, self.height = WindowUtils.configure_window(self.root, "Quiz TGE APP 2025")
        self.root.protocol("WM_DELETE_WINDOW", self._close_quiz)
        
        self._create_interface()
        self._show_question()
        self.root.mainloop()
    
    def _create_interface(self):
        """Cria a interface do quiz"""
        main_frame = tk.Frame(self.root, bg=Config.BACKGROUND_COLOR)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Barra de progresso
        self.progress_bar = ttk.Progressbar(
            main_frame,
            length=self.width - 100,
            mode='determinate',
            maximum=len(self.questions)
        )
        self.progress_bar.pack(pady=20)
        
        # Label da pergunta
        self.question_label = tk.Label(
            main_frame,
            text="",
            wraplength=self.width - 100,
            justify="left",
            font=("Arial", 13),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_COLOR
        )
        self.question_label.pack(pady=30)
        
        # Frame para botões
        buttons_frame = tk.Frame(main_frame, bg=Config.BACKGROUND_COLOR)
        buttons_frame.pack(fill='x', pady=20)
        
        # Criar botões de alternativas
        self.alternative_buttons = {}
        for letter in ['a', 'b', 'c', 'd']:
            btn = tk.Button(
                buttons_frame,
                text="",
                font=("Arial", 12),
                bg=Config.BUTTON_COLOR,
                fg=Config.TEXT_COLOR,
                wraplength=self.width - 150,
                justify="left",
                anchor="w",
                padx=15,
                pady=8,
                command=lambda l=letter: self._answer_question(l)
            )
            btn.pack(pady=8, padx=30, fill="x")
            self.alternative_buttons[letter] = btn
    
    def _show_question(self):
        """Mostra a questão atual"""
        if not self.is_quiz_active:
            return
        
        if self.current_index >= len(self.questions):
            self._finish_quiz()
            return
        
        question = self.questions[self.current_index]
        self.current_correct_answer = question.gabarito
        
        # Atualizar texto da pergunta
        question_text = (
            f"Pergunta {self.current_index + 1} de {len(self.questions)}: "
            f"{question.enunciado}\n\nFonte: {question.fonte}"
        )
        self.question_label.config(text=question_text)
        
        # Atualizar botões com alternativas
        alternatives = question.get_alternatives()
        for letter, button in self.alternative_buttons.items():
            button.config(text=f"{letter.upper()}) {alternatives[letter]}")
        
        # Atualizar barra de progresso
        self.progress_bar['value'] = self.current_index
    
    def _answer_question(self, answer: str):
        """Processa a resposta do usuário"""
        if not self.is_quiz_active:
            return
        
        is_correct = answer == self.current_correct_answer
        
        if is_correct:
            self.correct_answers += 1
        
        # Mostrar janela personalizada de resultado
        result_dialog = CustomResultDialog(
            self.root,
            is_correct,
            self.current_correct_answer,
            answer
        )
        result_dialog.show()
        
        self._next_question()
    
    def _next_question(self):
        """Avança para a próxima questão"""
        if not self.is_quiz_active:
            return
        
        self.current_index += 1
        self._show_question()
    
    def _finish_quiz(self):
        """Finaliza o quiz e mostra resultados"""
        if not self.is_quiz_active:
            return
        
        self.is_quiz_active = False
        
        percentage, level, message = self.performance_evaluator.evaluate_performance(
            self.correct_answers, len(self.questions)
        )
        
        result_text = (
            f"Quiz Finalizado!\n\n"
            f"Você acertou {self.correct_answers} de {len(self.questions)} questões.\n"
            f"Percentual de acerto: {percentage:.1f}%\n\n{message}"
        )
        
        self._show_final_result(result_text)
    
    def _show_final_result(self, result_text: str):
        """Mostra o resultado final em uma janela modal"""
        result_window = tk.Toplevel(self.root)
        result_window.title("Resultado Final")
        result_window.configure(bg=Config.BACKGROUND_COLOR)
        
        # Configurar janela
        result_width, result_height = 400, 300
        pos_x = (self.root.winfo_screenwidth() - result_width) // 2
        pos_y = (self.root.winfo_screenheight() - result_height) // 2
        result_window.geometry(f"{result_width}x{result_height}+{pos_x}+{pos_y}")
        
        # Tornar modal
        result_window.transient(self.root)
        result_window.grab_set()
        
        # Conteúdo
        result_label = tk.Label(
            result_window,
            text=result_text,
            font=("Arial", 12),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_COLOR,
            justify="center"
        )
        result_label.pack(pady=30)
        
        # Botões
        buttons_frame = tk.Frame(result_window, bg=Config.BACKGROUND_COLOR)
        buttons_frame.pack(pady=20)
        
        retry_button = tk.Button(
            buttons_frame,
            text="Tentar Novamente",
            font=("Arial", 12, "bold"),
            bg=Config.SUCCESS_COLOR,
            fg=Config.TEXT_COLOR,
            width=15,
            height=2,
            command=lambda: self._retry_quiz(result_window)
        )
        retry_button.pack(side="left", padx=10)
        
        exit_button = tk.Button(
            buttons_frame,
            text="Sair",
            font=("Arial", 12, "bold"),
            bg=Config.ERROR_COLOR,
            fg=Config.TEXT_COLOR,
            width=15,
            height=2,
            command=lambda: self._exit_application(result_window)
        )
        exit_button.pack(side="right", padx=10)
    
    def _retry_quiz(self, result_window: tk.Toplevel):
        """Reinicia o quiz"""
        result_window.destroy()
        self._close_quiz()
        self._restart_application()
    
    def _exit_application(self, result_window: tk.Toplevel):
        """Sai da aplicação"""
        result_window.destroy()
        self._close_quiz()
    
    def _close_quiz(self):
        """Fecha o quiz"""
        self.is_quiz_active = False
        if self.root:
            self.root.destroy()
    
    def _restart_application(self):
        """Reinicia a aplicação"""
        root = tk.Tk()
        InitialScreen(root)
        root.mainloop()


# --------------------- Aplicação Principal ---------------------
class QuizApp:
    """Classe principal da aplicação"""
    
    @staticmethod
    def run():
        """Executa a aplicação"""
        root = tk.Tk()
        InitialScreen(root)
        root.mainloop()


# --------------------- Ponto de Entrada ---------------------
if __name__ == "__main__":
    QuizApp.run()