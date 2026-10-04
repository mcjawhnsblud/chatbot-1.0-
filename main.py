import tkinter as tk
from html.parser import HTMLParser
from threading import Thread
from ai import runAI
import markdown


class MarkdownTextParser(HTMLParser):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.active_tags = []

    def _newline(self):
        content = self.widget.get("1.0", "end-1c")
        if content and not content.endswith("\n"):
            self.widget.insert("end", "\n")

    def handle_starttag(self, tag, attrs):
        if tag in {"p", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote", "li"}:
            self._newline()
        if tag == "li":
            self.widget.insert("end", "• ")
        if tag == "br":
            self.widget.insert("end", "\n")
        if tag in {"strong", "b", "em", "i", "code", "pre", "h1", "h2", "h3", "h4", "h5", "h6"} or (
            tag == "a" and dict(attrs).get("href")
        ):
            self.active_tags.append(tag)

    def handle_endtag(self, tag):
        if tag in self.active_tags:
            self.active_tags.remove(tag)
        if tag in {"p", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote", "li"}:
            self._newline()

    def handle_data(self, data):
        self.widget.insert("end", data, tuple(self.active_tags))


class ChatWindow:
    def __init__(self, title="ollama ai", geometry="500x800"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(geometry)

        self.text = tk.Text(self.root, height=5, width=30)
        self.send_button = tk.Button(self.root, text="Answer", command=self.ask_ai)
        self.output = tk.Text(
            self.root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            background="#1e1e1e",
            foreground="#ffffff",
            insertbackground="#ffffff",
            padx=12,
            pady=12,
        )
        self.output_scrollbar = tk.Scrollbar(
            self.root,
            orient=tk.VERTICAL,
            command=self.output.yview,
        )
        self.output.configure(yscrollcommand=self.output_scrollbar.set)
        self.output.tag_configure("strong", font=("TkDefaultFont", 10, "bold"))
        self.output.tag_configure("b", font=("TkDefaultFont", 10, "bold"))
        self.output.tag_configure("em", font=("TkDefaultFont", 10, "italic"))
        self.output.tag_configure("i", font=("TkDefaultFont", 10, "italic"))
        self.output.tag_configure(
            "code", background="#2d2d2d", foreground="#ffffff", font=("TkFixedFont", 10)
        )
        self.output.tag_configure(
            "pre", background="#2d2d2d", foreground="#ffffff", font=("TkFixedFont", 10)
        )
        self.output.tag_configure(
            "a", foreground="#66baff", underline=True
        )
        for heading in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.output.tag_configure(heading, font=("TkDefaultFont", 12, "bold"))

        self.text.pack(padx=30, pady=(10, 5))
        self.send_button.pack(pady=5)
        self.output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        self.output.pack(side=tk.LEFT, padx=10, pady=10, fill="both", expand=True)
        self.show_markdown("Press **Answer** to generate a response.")

    def show_markdown(self, text):
        html = markdown.markdown(text, extensions=["fenced_code", "tables"])
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        MarkdownTextParser(self.output).feed(html)
        self.output.configure(state=tk.DISABLED)

    def show_error(self, error):
        self.show_markdown(f"**Request failed:** {error}")

    def ask_ai(self):
        user_text = self.text.get("1.0", "end-1c").strip()
        if not user_text:
            return

        self.send_button.config(state=tk.DISABLED)
        self.show_markdown("_Thinking..._")

        def worker():
            try:
                answer = runAI(user_text)
                if not answer.strip():
                    answer = "_The AI returned an empty response._"
            except Exception as error:
                self.root.after(
                    0,
                    lambda error=error: self.show_error(
                        f"{type(error).__name__}: {error}"
                    ),
                )
            else:
                self.root.after(0, lambda: self.show_markdown(answer))
            finally:
                self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))

        Thread(target=worker, daemon=True).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ChatWindow()
    app.run()