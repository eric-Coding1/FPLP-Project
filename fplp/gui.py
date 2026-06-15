"""FPLP Language - Desktop GUI (tkinter)"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import sys
import io
import os
import threading

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fplp.lexer import Lexer
from fplp.parser import Parser
from fplp.compiler import compile_program
from fplp.vm import VM
from fplp.environment import Environment
from fplp.builtins import FPLPError
from fplp.block_editor import BlockEditor


def _format_value(val):
    """Format a value for display (dup from main to avoid circular import)."""
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return str(val)
    if isinstance(val, list):
        items = ', '.join(_format_value(v) for v in val)
        return '[' + items + ']'
    if isinstance(val, dict):
        items = ', '.join(f'{_format_value(k)}: {_format_value(v)}' for k, v in val.items())
        return '{' + items + '}'
    if isinstance(val, str):
        return '"' + val + '"'
    return str(val)


# Color scheme
BG_DARK = "#1e1e1e"
BG_MED = "#252526"
BG_LIGHT = "#2d2d2d"
FG = "#d4d4d4"
FG_DIM = "#888"
ACCENT = "#0d7377"
ACCENT_HOVER = "#0a8a8f"
EDITOR_FONT = ("Consolas", 11)
OUTPUT_FONT = ("Consolas", 10)


class StdoutCapture(io.StringIO):
    """Captures stdout writes and forwards them to a GUI callback."""
    def __init__(self, callback):
        super().__init__()
        self._gui_callback = callback

    def write(self, s):
        if s:
            self._gui_callback(s)
        super().write(s)


class FPLPImageArchive:
    """Stores images shown via show_image() for GUI display."""
    def __init__(self):
        self.images = []
        self._lock = threading.Lock()

    def add(self, pil_image):
        with self._lock:
            self.images.append(pil_image)
            return len(self.images) - 1

    def get(self, index):
        with self._lock:
            if 0 <= index < len(self.images):
                return self.images[index]
        return None

    def clear(self):
        with self._lock:
            self.images.clear()


# Global image archive - the graphics module can push images here
_image_archive = FPLPImageArchive()


def get_image_archive():
    return _image_archive


class FPLPGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FPLP - Fast Parallel Language Plus")
        self.root.geometry("1000x750")
        self.root.minsize(700, 500)
        self.current_file = None
        self._image_archive = get_image_archive()
        self._image_windows = []

        self._setup_styles()
        self._build_menu()
        self._build_layout()
        self._bind_shortcuts()

        # Add tag styles for output
        self.output.tag_config("stdout", foreground="#d4d4d4")
        self.output.tag_config("stderr", foreground="#f48771")
        self.output.tag_config("result", foreground="#89d185")

    def _setup_styles(self):
        self.root.configure(bg=BG_DARK)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TMenuBar", background=BG_MED, foreground=FG)

    def _build_menu(self):
        menubar = tk.Menu(self.root, bg=BG_MED, fg=FG,
                          activebackground=ACCENT, activeforeground="white")

        file_menu = tk.Menu(menubar, tearoff=0, bg=BG_MED, fg=FG,
                            activebackground=ACCENT, activeforeground="white")
        file_menu.add_command(label="New       Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open      Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save      Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As   Ctrl+Shift+S", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        run_menu = tk.Menu(menubar, tearoff=0, bg=BG_MED, fg=FG,
                           activebackground=ACCENT, activeforeground="white")
        run_menu.add_command(label="Run          F5", command=self.run_code)
        run_menu.add_command(label="Run All (current file)", command=self.run_current_file)
        menubar.add_cascade(label="Run", menu=run_menu)

        edit_menu = tk.Menu(menubar, tearoff=0, bg=BG_MED, fg=FG,
                            activebackground=ACCENT, activeforeground="white")
        edit_menu.add_command(label="Clear Output", command=self.clear_output)
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Images", command=self.clear_images)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=0, bg=BG_MED, fg=FG,
                            activebackground=ACCENT, activeforeground="white")
        help_menu.add_command(label="About FPLP", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _build_layout(self):
        # Main paned window
        self.paned = tk.PanedWindow(self.root, orient=tk.VERTICAL,
                                     bg=BG_DARK, sashrelief=tk.RAISED, sashwidth=4)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Editor area
        editor_frame = tk.Frame(self.paned, bg=BG_DARK)
        self.paned.add(editor_frame, height=400, stretch="always")

        # Toolbar
        toolbar = tk.Frame(editor_frame, bg=BG_MED, height=36)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        self.run_btn = tk.Button(
            toolbar, text="▶ Run  F5", command=self.run_code,
            bg=ACCENT, fg="white", relief=tk.FLAT,
            padx=16, pady=2, font=("Segoe UI", 10, "bold"),
            activebackground=ACCENT_HOVER, activeforeground="white",
            cursor="hand2"
        )
        self.run_btn.pack(side=tk.LEFT, padx=(8, 4), pady=4)

        self.clear_btn = tk.Button(
            toolbar, text="Clear", command=self.clear_output,
            bg=BG_LIGHT, fg=FG, relief=tk.FLAT,
            padx=12, pady=2, font=("Segoe UI", 9),
            activebackground=BG_MED, activeforeground=FG,
            cursor="hand2"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=4, pady=4)

        # --- Mode switch tabs ---
        self._mode_var = tk.StringVar(value="code")
        code_mode_btn = tk.Button(
            toolbar, text="Code", command=lambda: self._switch_mode("code"),
            bg=BG_LIGHT, fg=FG, relief=tk.FLAT,
            padx=10, pady=2, font=("Segoe UI", 9, "bold"),
            activebackground=ACCENT, activeforeground="white",
            cursor="hand2"
        )
        code_mode_btn.pack(side=tk.LEFT, padx=(20, 2), pady=4)
        self._code_mode_btn = code_mode_btn

        blocks_mode_btn = tk.Button(
            toolbar, text="Blocks", command=lambda: self._switch_mode("blocks"),
            bg=BG_LIGHT, fg=FG, relief=tk.FLAT,
            padx=10, pady=2, font=("Segoe UI", 9, "bold"),
            activebackground=ACCENT, activeforeground="white",
            cursor="hand2"
        )
        blocks_mode_btn.pack(side=tk.LEFT, padx=2, pady=4)
        self._blocks_mode_btn = blocks_mode_btn

        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            toolbar, textvariable=self.status_var,
            bg=BG_MED, fg=FG_DIM, font=("Segoe UI", 9),
            anchor=tk.E
        )
        status_label.pack(side=tk.RIGHT, padx=12, pady=4)

        # Editor container — will hold either code or block editor
        self._editor_container = tk.Frame(editor_frame, bg=BG_DARK)
        self._editor_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 0))

        # --- Code editor view ---
        self._code_view = tk.Frame(self._editor_container, bg=BG_DARK)

        # Line numbers
        self.line_numbers = tk.Text(
            self._code_view, width=5, padx=6, pady=6,
            bg=BG_MED, fg=FG_DIM, font=EDITOR_FONT,
            state=tk.DISABLED, relief=tk.FLAT, takefocus=0,
            highlightthickness=0, borderwidth=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor
        self.editor = tk.Text(
            self._code_view, wrap=tk.NONE,
            font=EDITOR_FONT,
            bg=BG_DARK, fg=FG,
            insertbackground="white",
            relief=tk.FLAT, highlightthickness=0, borderwidth=0,
            padx=8, pady=6,
            selectbackground=ACCENT, selectforeground="white",
            undo=True
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for editor
        editor_scroll = tk.Scrollbar(self._code_view, command=self.editor.yview,
                                      bg=BG_MED, troughcolor=BG_DARK)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=self._sync_scroll)

        # --- Block editor view ---
        self._block_view = tk.Frame(self._editor_container, bg="#F0F0F0")
        self._block_editor = BlockEditor(self._block_view, on_generate=self._on_blocks_generated)

        # Start with code view
        self._code_view.pack(fill=tk.BOTH, expand=True)
        self._highlight_mode("code")

        # Line numbers
        self.line_numbers = tk.Text(
            self._code_view, width=5, padx=6, pady=6,
            bg=BG_MED, fg=FG_DIM, font=EDITOR_FONT,
            state=tk.DISABLED, relief=tk.FLAT, takefocus=0,
            highlightthickness=0, borderwidth=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor
        self.editor = tk.Text(
            self._code_view, wrap=tk.NONE,
            font=EDITOR_FONT,
            bg=BG_DARK, fg=FG,
            insertbackground="white",
            relief=tk.FLAT, highlightthickness=0, borderwidth=0,
            padx=8, pady=6,
            selectbackground=ACCENT, selectforeground="white",
            undo=True
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for editor
        editor_scroll = tk.Scrollbar(self._code_view, command=self.editor.yview,
                                      bg=BG_MED, troughcolor=BG_DARK)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=self._sync_scroll)

        # Output area
        output_frame = tk.Frame(self.paned, bg=BG_DARK)
        self.paned.add(output_frame, height=200, stretch="always")

        # Output tabs
        self.output_notebook = ttk.Notebook(output_frame)
        self.output_notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Console tab
        console_frame = tk.Frame(self.output_notebook, bg=BG_DARK)
        self.output_notebook.add(console_frame, text="  Console  ")

        self.output = tk.Text(
            console_frame, wrap=tk.WORD,
            font=OUTPUT_FONT,
            bg=BG_DARK, fg=FG,
            relief=tk.FLAT, highlightthickness=0, borderwidth=0,
            padx=8, pady=6, state=tk.DISABLED
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        output_scroll = tk.Scrollbar(console_frame, command=self.output.yview,
                                      bg=BG_MED, troughcolor=BG_DARK)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output.config(yscrollcommand=output_scroll.set)

        # Images tab
        self.images_frame = tk.Frame(self.output_notebook, bg=BG_DARK)
        self.output_notebook.add(self.images_frame, text="  Images  ")

        self.images_canvas = tk.Canvas(self.images_frame, bg=BG_DARK,
                                        highlightthickness=0)
        self.images_canvas.pack(fill=tk.BOTH, expand=True)
        self.images_label = tk.Label(
            self.images_canvas, text="No images generated yet.\nRun code that uses show_image().",
            bg=BG_DARK, fg=FG_DIM, font=("Segoe UI", 11)
        )
        self.images_canvas.create_window(300, 100, window=self.images_label)

        # Insert default template
        self._insert_template()

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as_file())
        self.root.bind("<F5>", lambda e: self.run_code())
        self.root.bind("<Control-Return>", lambda e: self.run_code())
        self.editor.bind("<KeyRelease>", lambda e: self._update_line_numbers())

    def _insert_template(self):
        template = """# FPLP - Fast Parallel Language Plus
# Press F5 to run

fn greet(name) => "Hello, " + name

print(greet("FPLP"))
print("2 + 3 * 4 =", 2 + 3 * 4)

let nums = [1, 2, 3, 4, 5]
let total = 0
for n in nums {
    total = total + n
}
print("sum =", total)
"""
        self.editor.insert("1.0", template)
        self._update_line_numbers()

    def _sync_scroll(self, *args):
        self.editor.yview_moveto(args[0])
        self._update_line_numbers()

    def _update_line_numbers(self):
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        line_count = self.editor.index("end-1c").split(".")[0]
        numbers = "\n".join(str(i) for i in range(1, int(line_count) + 1))
        self.line_numbers.insert("1.0", numbers)
        self.line_numbers.config(state=tk.DISABLED)
        # Sync scroll
        self.line_numbers.yview_moveto(self.editor.yview()[0])

    # --- File operations ---

    def new_file(self):
        if self._confirm_discard():
            self.editor.delete("1.0", tk.END)
            self.current_file = None
            self.root.title("FPLP - Untitled")
            self._update_line_numbers()

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open FPLP file",
            filetypes=[("FPLP files", "*.fplp"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)
            self.current_file = path
            self.root.title(f"FPLP - {os.path.basename(path)}")
            self._update_line_numbers()
            self.status_var.set(f"Opened: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_file(self):
        if self.current_file:
            self._write_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        path = filedialog.asksaveasfilename(
            title="Save FPLP file",
            defaultextension=".fplp",
            filetypes=[("FPLP files", "*.fplp"), ("All files", "*.*")]
        )
        if path:
            self._write_file(path)
            self.current_file = path
            self.root.title(f"FPLP - {os.path.basename(path)}")

    def _write_file(self, path):
        try:
            content = self.editor.get("1.0", tk.END).rstrip("\n")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_var.set(f"Saved: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    def _confirm_discard(self):
        # Simple check - always allow for now
        return True

    # --- Run ---

    def run_code(self):
        self.clear_output()
        self.clear_images()
        self.status_var.set("Running...")
        self.run_btn.config(state=tk.DISABLED, text="⏳ Running")

        source = self.editor.get("1.0", tk.END).strip()
        if not source:
            self._reset_run_btn()
            return

        thread = threading.Thread(target=self._execute, args=(source,))
        thread.daemon = True
        thread.start()

    def run_current_file(self):
        if self.current_file:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", f.read())
            self.run_code()
        else:
            self.run_code()

    def _execute(self, source):
        try:
            # Set up stdout capture
            output_lines = []

            def on_stdout(text):
                output_lines.append(text)
                self.root.after(0, self._append_output, text)

            captured = StdoutCapture(on_stdout)
            old_stdout = sys.stdout
            sys.stdout = captured

            # Reset image archive
            self._image_archive.clear()

            # Parse + compile + execute
            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()

            try:
                code = compile_program(program)
            except Exception as e:
                self.root.after(0, self._append_output,
                                f"Compile error: {e}\n", True)
                sys.stdout = old_stdout
                self.root.after(0, self._reset_run_btn)
                return

            env = Environment()
            vm = VM()
            result = vm.run_code(code, env)

            sys.stdout = old_stdout

            if result is not None:
                formatted = _format_value(result)
                self.root.after(0, self._append_result, f"=> {formatted}")

            # Check for images
            if self._image_archive.images:
                self.root.after(0, self._display_images)

            self.root.after(0, lambda: self.status_var.set("Done ✓"))

        except SyntaxError as e:
            sys.stdout = old_stdout if 'old_stdout' in dir() else sys.__stdout__
            self.root.after(0, self._append_output, f"Syntax error: {e}\n", True)
        except Exception as e:
            sys.stdout = old_stdout if 'old_stdout' in dir() else sys.__stdout__
            self.root.after(0, self._append_output, f"Error: {e}\n", True)
        finally:
            if 'old_stdout' in dir():
                sys.stdout = old_stdout
            self.root.after(0, self._reset_run_btn)

    def _append_output(self, text, is_error=False):
        self.output.config(state=tk.NORMAL)
        tag = "stderr" if is_error else "stdout"
        self.output.insert(tk.END, text, tag)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def _append_result(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", "result")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def clear_output(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)

    def clear_images(self):
        self._image_archive.clear()
        self.images_canvas.delete("all")
        self.images_label = tk.Label(
            self.images_canvas, text="No images.",
            bg=BG_DARK, fg=FG_DIM, font=("Segoe UI", 11)
        )
        self.images_canvas.create_window(300, 100, window=self.images_label)

    def _reset_run_btn(self):
        self.run_btn.config(state=tk.NORMAL, text="▶ Run  F5")

    def _display_images(self):
        """Show images from the archive in the images tab."""
        self.images_canvas.delete("all")
        archive = self._image_archive
        x_offset = 10

        for i in range(len(archive.images)):
            pil_img = archive.get(i)
            if pil_img is None:
                continue

            # Resize for display (max 300px wide)
            img = pil_img.copy()
            max_w = 300
            if img.width > max_w:
                ratio = max_w / img.width
                new_size = (max_w, int(img.height * ratio))
                img = img.resize(new_size, 1)

            # Convert PIL to PhotoImage
            import io as _io
            buf = _io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)

            photo = tk.PhotoImage(data=buf.read())
            # Keep reference
            if not hasattr(self, '_tk_images'):
                self._tk_images = []
            self._tk_images.append(photo)

            self.images_canvas.create_image(
                x_offset, 10, anchor=tk.NW, image=photo
            )
            self.images_canvas.create_text(
                x_offset + img.width // 2, img.height + 15,
                text=f"Image {i + 1} ({pil_img.width}x{pil_img.height})",
                fill=FG_DIM, font=("Segoe UI", 9)
            )
            x_offset += img.width + 20

        self.images_canvas.config(scrollregion=self.images_canvas.bbox("all"))
        self.output_notebook.select(self.images_frame)

    def show_about(self):
        messagebox.showinfo(
            "About FPLP",
            "FPLP v1.0\n\n"
            "Fast Parallel Language Plus\n\n"
            "A lightweight scripting language with\n"
            "bytecode compiler + stack VM.\n\n"
            "Built in Python with ❤️"
        )

    # ---- Mode switching ----

    def _switch_mode(self, mode):
        """Switch between Code view and Blocks view."""
        if mode == self._mode_var.get():
            return
        self._mode_var.set(mode)

        if mode == "code":
            # Generate code from blocks and show code view
            code = self._block_editor.workspace.generate_code()
            if code.strip():
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", code.strip())
            self._block_view.pack_forget()
            self._code_view.pack(fill=tk.BOTH, expand=True)
            self.status_var.set("Code mode")
        else:
            # Show blocks view, sync blocks from code
            self._code_view.pack_forget()
            self._block_view.pack(fill=tk.BOTH, expand=True)
            # Convert current code to blocks
            source = self.editor.get("1.0", tk.END).strip()
            if source:
                self._block_editor.workspace.blocks.clear()
                self._block_editor.workspace.add_blocks_from_code(source)
                self._block_editor.workspace._rerender_all()
            self.status_var.set("Blocks mode — click blocks from the left palette to add them")

        self._highlight_mode(mode)

    def _highlight_mode(self, mode):
        """Highlight the active mode button."""
        if mode == "code":
            self._code_mode_btn.config(bg=ACCENT, fg="white")
            self._blocks_mode_btn.config(bg=BG_LIGHT, fg=FG)
        else:
            self._blocks_mode_btn.config(bg=ACCENT, fg="white")
            self._code_mode_btn.config(bg=BG_LIGHT, fg=FG)

    def _on_blocks_generated(self, code):
        """Called when blocks generate code. Switches to code view."""
        if code.strip():
            self._switch_mode("code")
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", code.strip())
            self.status_var.set("Blocks → Code generated")

    def run(self):
        self.root.mainloop()


def launch_gui():
    """Launch the FPLP GUI application."""
    gui = FPLPGUI()
    gui.run()
