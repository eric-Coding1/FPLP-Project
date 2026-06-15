"""FPLP Language - Scratch-like Block Editor (Canvas-based)"""

import tkinter as tk
from tkinter import messagebox

# --- Color palette (Scratch-inspired) ---
CAT_COLORS = {
    "Motion":    ("#4C97FF", "#3C7ED6"),   # blue
    "Control":   ("#FFAB19", "#D98A0E"),   # yellow/orange
    "Variables": ("#FF8C1A", "#D9750F"),   # orange
    "Operators": ("#59C059", "#3DA13D"),   # green
    "Functions": ("#FF6680", "#D94D66"),   # red
    "Data":      ("#FF8C1A", "#D9750F"),   # orange
    "Sensing":   ("#5CB1D6", "#3F94B8"),   # light blue
    "IO":        ("#A36AE2", "#8551C7"),   # purple
    "Graphics":  ("#9966FF", "#7D4DD9"),   # violet
    "Libs":      ("#CF63CF", "#B04AB0"),   # magenta
}

BLOCK_COLORS = {
    "Variables": ("#FF8C1A", "#D9750F", "#FFF0D0"),
    "Control":   ("#FFAB19", "#D98A0E", "#FFF5D0"),
    "Functions": ("#FF6680", "#D94D66", "#FFD0D8"),
    "Operators": ("#59C059", "#3DA13D", "#D8F0D8"),
    "Data":      ("#FF8C1A", "#D9750F", "#FFF0D0"),
    "IO":        ("#A36AE2", "#8551C7", "#E8D8F8"),
    "Graphics":  ("#9966FF", "#7D4DD9", "#E8D8FF"),
    "Libs":      ("#CF63CF", "#B04AB0", "#F0D8F0"),
    "String":    ("#5CB1D6", "#3F94B8", "#D0EAF4"),
    "Math":      ("#59C059", "#3DA13D", "#D8F0D8"),
}


# ======================================================================
# Block model
# ======================================================================

class BlockNode:
    """A single block in the workspace tree."""
    def __init__(self, label, snippet, category, block_type="statement"):
        self.label = label
        self.snippet = snippet      # FPLP code template
        self.category = category
        self.block_type = block_type  # "statement", "expression", "value", "boolean"
        self.next_block = None      # chain below (statement blocks)
        self.body_block = None      # C-shape body (if, loop, fn)
        self.arg_blocks = []        # argument slots (for expressions)
        self.x = 100
        self.y = 100
        self.width = 160
        self.height = 36
        self.canvas_id = None       # tkinter canvas item group id
        self.text_ids = []          # text sub-items

    def __repr__(self):
        return f"Block({self.label})"


# ======================================================================
# Block definitions for the palette
# ======================================================================

PALETTE_BLOCKS = [
    ("Control", [
        BlockNode("if else",       'if __cond__ {\n    \n} else {\n    \n}', "Control"),
        BlockNode("if",            'if __cond__ {\n    \n}', "Control"),
        BlockNode("for loop",      'for __var__ in __iter__ {\n    \n}', "Control"),
        BlockNode("while loop",    'loop __cond__ {\n    \n}', "Control"),
    ]),
    ("Variables", [
        BlockNode("let x = v",     'let __name__ = __value__', "Variables"),
        BlockNode("set x = v",     '__name__ = __value__', "Variables"),
        BlockNode("change x",      '__name__ = __name__ + 1', "Variables"),
    ]),
    ("Functions", [
        BlockNode("define fn",     'fn __name__(__params__) {\n    \n}', "Functions"),
        BlockNode("fn arrow",      'fn __name__(__params__) => __expr__', "Functions"),
        BlockNode("return",        'return __value__', "Functions"),
        BlockNode("call fn",       '__name__(__args__)', "Functions"),
    ]),
    ("Operators", [
        BlockNode("+",             '__a__ + __b__', "Operators", "expression"),
        BlockNode("-",             '__a__ - __b__', "Operators", "expression"),
        BlockNode("*",             '__a__ * __b__', "Operators", "expression"),
        BlockNode("/",             '__a__ / __b__', "Operators", "expression"),
        BlockNode("and",           '__a__ and __b__', "Operators", "boolean"),
        BlockNode("or",            '__a__ or __b__', "Operators", "boolean"),
        BlockNode("not",           'not __x__', "Operators", "boolean"),
        BlockNode("< = >",         '__a__ < __b__', "Operators", "boolean"),
    ]),
    ("Math", [
        BlockNode("sqrt",          'sqrt(__x__)', "Math", "expression"),
        BlockNode("abs",           'abs(__x__)', "Math", "expression"),
        BlockNode("pow",           'pow(__x__, __y__)', "Math", "expression"),
        BlockNode("min / max",     'max(__a__, __b__)', "Math", "expression"),
        BlockNode("round",         'round(__x__)', "Math", "expression"),
        BlockNode("random",        'rand(__min__, __max__)', "Math", "expression"),
    ]),
    ("String", [
        BlockNode("join",          'join(__arr__, __sep__)', "String", "expression"),
        BlockNode("split",         'split(__s__, __sep__)', "String", "expression"),
        BlockNode("upper",          'upper(__s__)', "String", "expression"),
        BlockNode("lower",          'lower(__s__)', "String", "expression"),
        BlockNode("len",            'len(__s__)', "String", "expression"),
        BlockNode("contains",       'contains(__s__, __sub__)', "String", "boolean"),
        BlockNode("replace",        'str_replace(__s__, __old__, __new__)', "String", "expression"),
    ]),
    ("Data", [
        BlockNode("array",          '[__items__]', "Data", "expression"),
        BlockNode("push",           'push(__arr__, __val__)', "Data"),
        BlockNode("pop",            'pop(__arr__)', "Data", "expression"),
        BlockNode("keys",           'keys(__map__)', "Data", "expression"),
        BlockNode("values",         'values(__map__)', "Data", "expression"),
        BlockNode("len",            'len(__obj__)', "Data", "expression"),
    ]),
    ("IO", [
        BlockNode("print",          'print(__value__)', "IO"),
        BlockNode("input",          'input(__prompt__)', "IO"),
        BlockNode("read file",      'read_file(__path__)', "IO"),
        BlockNode("write file",     'write_file(__path__, __content__)', "IO"),
    ]),
    ("Graphics", [
        BlockNode("create img",    'create_image(__w__, __h__, "__color__")', "Graphics", "expression"),
        BlockNode("draw rect",     'draw_rect(__img__, __x__, __y__, __w__, __h__, "__color__")', "Graphics"),
        BlockNode("draw circle",   'draw_circle(__img__, __cx__, __cy__, __r__, "__color__")', "Graphics"),
        BlockNode("draw text",     'draw_text(__img__, __x__, __y__, "__text__", __size__)', "Graphics"),
        BlockNode("save image",    'save_image(__img__, "__path__")', "Graphics"),
        BlockNode("show image",    'show_image(__img__)', "Graphics"),
    ]),
    ("Libs", [
        BlockNode("json.parse",    'json.parse(__str__)', "Libs", "expression"),
        BlockNode("json.stringify",'json.stringify(__val__, __indent__)', "Libs", "expression"),
        BlockNode("math.sqrt",     'math.sqrt(__x__)', "Libs", "expression"),
        BlockNode("os.cwd",        'os.cwd()', "Libs", "expression"),
        BlockNode("os.listdir",    'os.listdir(__path__)', "Libs", "expression"),
        BlockNode("time.now",      'time.now()', "Libs", "expression"),
    ]),
]


# ======================================================================
# Block Workspace (canvas-based)
# ======================================================================

class BlockWorkspace:
    """A Scratch-like canvas workspace with draggable blocks."""

    def __init__(self, parent, on_generate=None):
        self.parent = parent
        self.on_generate = on_generate
        self.blocks = []            # top-level block chain
        self.dragging = None        # (BlockNode, offset_x, offset_y)
        self._block_count = 0
        self._selected = None

        # Canvas
        self.canvas = tk.Canvas(
            parent, bg="#F0F0F0", highlightthickness=0,
            width=600, height=400
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)

        # Context menu
        self._context_menu = tk.Menu(self.canvas, tearoff=0, bg="#333", fg="white",
                                      activebackground="#555")
        self._context_menu.add_command(label="Delete block", command=self._delete_selected)
        self._context_menu.add_command(label="Duplicate", command=self._duplicate_selected)

    # ---- Add block from palette ----

    def add_block(self, block_node, x=None, y=None):
        """Add a block to the workspace canvas."""
        if x is None:
            x = 50 + (self._block_count * 20) % 300
        if y is None:
            y = 50 + (self._block_count * 50) % 400

        block_node.x = x
        block_node.y = y
        self.blocks.append(block_node)
        self._block_count += 1
        self._render_block(block_node)
        return block_node

    def add_blocks_from_code(self, code):
        """Parse simple blocks from code (future: parse AST)."""
        # For now, just add a generic block
        lines = [l for l in code.strip().split('\n') if l.strip()]
        for line in lines[:20]:  # limit to 20 blocks
            label = line.strip()[:40]
            if label:
                b = BlockNode(label, line.strip(), "Control")
                self.add_block(b)

    # ---- Rendering ----

    def _render_block(self, block):
        """Draw a block on the canvas."""
        c = self.canvas
        bg_color, border_color, _ = BLOCK_COLORS.get(
            block.category, ("#ccc", "#999", "#eee")
        )

        x, y = block.x, block.y
        w = max(block.width, len(block.label) * 7 + 40)
        h = block.height
        r = 6  # corner radius

        # Top notch (C-shape connector at top)
        # Bottom plug
        # Rounded rect body

        # Body
        coords = [x+r, y, x+w-r, y,
                  x+w, y, x+w, y+r,
                  x+w, y+h-r, x+w, y+h,
                  x+w-r, y+h, x+r, y+h,
                  x, y+h, x, y+h-r,
                  x, y+r, x, y]

        # Left color stripe
        stripe = c.create_rectangle(x+2, y+2, x+6, y+h-2,
                                     fill=border_color, outline="",
                                     tags=("block", f"block_{id(block)}"))

        # Main body
        body = c.create_rectangle(x+6, y+2, x+w-2, y+h-2,
                                   fill=bg_color, outline=border_color,
                                   width=1, tags=("block", f"block_{id(block)}"))

        # Label text
        text = c.create_text(x + w//2, y + h//2,
                              text=block.label, anchor=tk.CENTER,
                              fill="#222", font=("Arial", 9, "bold"),
                              tags=("block", f"block_{id(block)}"))

        # Category badge
        badge = c.create_text(x + w - 8, y + h//2,
                               text="›", anchor=tk.E,
                               fill=border_color, font=("Arial", 12, "bold"),
                               tags=("block", f"block_{id(block)}"))

        block.canvas_id = body
        block.text_ids = [stripe, text, badge]

        # Store reference
        c.block_node = block

    def _rerender_all(self):
        """Clear and redraw all blocks."""
        self.canvas.delete("block")
        for b in self.blocks:
            self._render_block(b)

    # ---- Mouse interactions ----

    def _get_block_at(self, x, y):
        """Find the top-level block at canvas coordinates."""
        for b in reversed(self.blocks):
            bx, by = b.x, b.y
            bw = b.width
            bh = b.height
            # Check chain length
            w = bw
            h = bh
            # Extend height for chained blocks
            cur = b
            while cur.next_block:
                cur = cur.next_block
                h += cur.height + 2

            if bx <= x <= bx + w + 100 and by <= y <= by + h:
                return b
        return None

    def _on_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        block = self._get_block_at(x, y)
        if block:
            self._selected = block
            self.dragging = (block, x - block.x, y - block.y)
            # Raise to top
            self.canvas.tag_raise(f"block_{id(block)}")

    def _on_drag(self, event):
        if self.dragging:
            block, ox, oy = self.dragging
            x = self.canvas.canvasx(event.x) - ox
            y = self.canvas.canvasy(event.y) - oy
            block.x = max(10, x)
            block.y = max(10, y)
            self._rerender_all()

    def _on_release(self, event):
        if self.dragging:
            block, _, _ = self.dragging
            self._snap_block(block)
            self.dragging = None

    def _snap_block(self, block):
        """Snap a block into the chain if it's close to another block."""
        snap_dist = 30
        for other in self.blocks:
            if other is block:
                continue
            # Check if block is near the bottom of other
            other_bottom = other.y + other.height
            # Find the last in the chain
            last = other
            while last.next_block:
                last = last.next_block
                other_bottom = last.y + last.height

            if (abs(block.y - other_bottom) < snap_dist and
                    abs(block.x - other.x) < snap_dist):
                # Snap: insert block after 'last'
                block.x = last.x
                block.y = last.y + last.height + 2
                # Update chain
                block.next_block = last.next_block
                last.next_block = block
                break

    def _on_right_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        block = self._get_block_at(x, y)
        if block:
            self._selected = block
            self._context_menu.tk_popup(event.x_root, event.y_root)

    def _delete_selected(self):
        if self._selected and self._selected in self.blocks:
            self.blocks.remove(self._selected)
            self._selected = None
            self._rerender_all()

    def _duplicate_selected(self):
        if self._selected:
            import copy
            new = copy.copy(self._selected)
            new.x += 20
            new.y += 20
            new.next_block = None
            self.blocks.append(new)
            self._rerender_all()

    # ---- Code generation ----

    def generate_code(self):
        """Walk the block chain and generate FPLP code."""
        lines = []
        for block in self.blocks:
            self._block_to_code(block, lines, 0)
        return '\n'.join(lines)

    def _block_to_code(self, block, lines, indent):
        """Recursively generate code from a block."""
        snippet = block.snippet
        # Replace placeholders
        code = snippet

        # Handle C-shaped blocks (if, loop, fn)
        if block.body_block:
            lines.append('    ' * indent + code.split('{')[0] + '{')
            self._block_to_code(block.body_block, lines, indent + 1)
            lines.append('    ' * indent + '}')
        else:
            lines.append('    ' * indent + code)

        # Process next block in chain
        if block.next_block:
            self._block_to_code(block.next_block, lines, indent)


# ======================================================================
# Palette Panel (left sidebar)
# ======================================================================

class BlockPalette(tk.Frame):
    """Draggable block palette similar to Scratch's block categories."""

    def __init__(self, parent, workspace):
        super().__init__(parent, bg="#E8E8E8", width=200)
        self.pack_propagate(False)
        self.workspace = workspace

        # Header
        header = tk.Label(self, text="Blocks", bg="#4C97FF", fg="white",
                          font=("Arial", 12, "bold"), padx=10, pady=6)
        header.pack(fill=tk.X)

        # Scrollable area
        canvas = tk.Canvas(self, bg="#E8E8E8", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        self.inner = tk.Frame(canvas, bg="#E8E8E8")

        self.inner.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor=tk.NW, width=190)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._expanded = None
        self._cat_frames = {}

        for cat_name, blocks in PALETTE_BLOCKS:
            bg_c, border_c, _ = BLOCK_COLORS.get(cat_name, ("#ccc", "#999", "#eee"))

            # Category button
            cat_btn = tk.Button(
                self.inner, text=f"  {cat_name}", anchor=tk.W,
                bg="#D8D8D8", fg="#333", relief=tk.FLAT,
                font=("Arial", 9, "bold"),
                activebackground="#ccc", cursor="hand2",
                command=lambda c=cat_name: self._toggle(c)
            )
            cat_btn.pack(fill=tk.X, padx=2, pady=(2, 0))

            # Block buttons container
            bf = tk.Frame(self.inner, bg="#E8E8E8")
            self._cat_frames[cat_name] = bf

            for b in blocks:
                btn = tk.Button(
                    bf, text=b.label, anchor=tk.W,
                    bg=bg_c, fg="white", relief=tk.RAISED,
                    font=("Arial", 8, "bold"), bd=1,
                    activebackground=border_c,
                    cursor="hand2",
                    command=lambda bn=b: self._add_to_workspace(bn)
                )
                btn.pack(fill=tk.X, padx=6, pady=1)

        # Start expanded
        self._toggle("Control")

    def _toggle(self, name):
        if self._expanded == name:
            self._cat_frames[name].pack_forget()
            self._expanded = None
            return
        if self._expanded and self._expanded in self._cat_frames:
            self._cat_frames[self._expanded].pack_forget()
        self._cat_frames[name].pack(fill=tk.X, padx=2, pady=(0, 4))
        self._expanded = name

    def _add_to_workspace(self, block):
        import copy
        new_block = copy.copy(block)
        new_block.next_block = None
        new_block.body_block = None
        self.workspace.add_block(new_block)


# ======================================================================
# Block Editor (combines palette + workspace)
# ======================================================================

class BlockEditor(tk.Frame):
    """Full block editing interface with palette and workspace."""

    def __init__(self, parent, on_generate=None):
        super().__init__(parent, bg="#F0F0F0")
        self.on_generate = on_generate

        # Top bar
        top = tk.Frame(self, bg="#E0E0E0", height=36)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Label(top, text="Block Editor", bg="#E0E0E0", fg="#333",
                 font=("Arial", 11, "bold"), padx=10).pack(side=tk.LEFT)

        self.gen_btn = tk.Button(
            top, text="Generate Code", bg="#4C97FF", fg="white",
            relief=tk.FLAT, padx=12, pady=2,
            font=("Arial", 9, "bold"), cursor="hand2",
            command=self._generate
        )
        self.gen_btn.pack(side=tk.RIGHT, padx=8, pady=4)

        self.clear_btn = tk.Button(
            top, text="Clear All", bg="#FF6680", fg="white",
            relief=tk.FLAT, padx=12, pady=2,
            font=("Arial", 9, "bold"), cursor="hand2",
            command=self._clear
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=4, pady=4)

        # Body: palette + workspace
        body = tk.Frame(self, bg="#F0F0F0")
        body.pack(fill=tk.BOTH, expand=True)

        # Workspace (center + right)
        ws_frame = tk.Frame(body, bg="#F0F0F0")
        ws_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.workspace = BlockWorkspace(ws_frame, on_generate=on_generate)

        # Palette (left)
        self.palette = BlockPalette(body, self.workspace)
        self.palette.pack(side=tk.LEFT, fill=tk.Y)

    def _generate(self):
        code = self.workspace.generate_code()
        if self.on_generate:
            self.on_generate(code)
        else:
            return code

    def _clear(self):
        self.workspace.blocks.clear()
        self.workspace._rerender_all()
