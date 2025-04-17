import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from src.call_llm import get_image_generate, get_loss
from src.loss import get_loss
import os

class ImagePromptGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 文生图匹配游戏 🎯")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f4f7")
        
        # Set application icon
        try:
            self.root.iconphoto(True, tk.PhotoImage(file="assets/icon.png"))
        except:
            pass
        
        # Configure styles
        self.configure_styles()
        
        # Create frame for the title
        title_frame = tk.Frame(root, bg="#f0f4f7")
        title_frame.pack(pady=15)
        
        # Main title
        main_title = tk.Label(title_frame, text="图像提示词匹配游戏", font=("Helvetica", 22, "bold"), 
                              bg="#f0f4f7", fg="#2c3e50")
        main_title.pack()
        
        # Subtitle
        subtitle = tk.Label(title_frame, text="尝试创建与目标图像最相似的提示词", 
                           font=("Helvetica", 12), bg="#f0f4f7", fg="#7f8c8d")
        subtitle.pack(pady=5)
        
        # Create control panel frame
        control_frame = tk.Frame(root, bg="#e1e8ed", relief=tk.GROOVE, bd=1)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Prompt frame
        prompt_frame = tk.Frame(control_frame, bg="#e1e8ed", pady=10, padx=15)
        prompt_frame.pack(fill=tk.X)
        
        prompt_label = tk.Label(prompt_frame, text="提示词：", font=("Helvetica", 12, "bold"), bg="#e1e8ed")
        prompt_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.prompt_entry = tk.Entry(prompt_frame, width=60, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.prompt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        
        # Button frame
        button_frame = tk.Frame(control_frame, bg="#e1e8ed", pady=10, padx=15)
        button_frame.pack(fill=tk.X)
        
        self.load_button = ttk.Button(button_frame, text="加载目标图片", command=self.load_image, style="Accent.TButton", width=15)
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.generate_button = ttk.Button(button_frame, text="生成图片", command=self.generate_image, style="Generate.TButton", width=15)
        self.generate_button.pack(side=tk.LEFT)
        
        # History counter and score
        score_frame = tk.Frame(button_frame, bg="#e1e8ed")
        score_frame.pack(side=tk.RIGHT)
        
        self.attempts_label = tk.Label(score_frame, text="尝试次数: 0", font=("Arial", 11), bg="#e1e8ed")
        self.attempts_label.pack(side=tk.RIGHT, padx=10)
        
        self.best_loss_label = tk.Label(score_frame, text="最佳 Loss: --", font=("Arial", 11), bg="#e1e8ed", fg="#16a085")
        self.best_loss_label.pack(side=tk.RIGHT, padx=10)
        self.best_prompt_label = tk.Label(score_frame, text="最佳提示词: --", font=("Arial", 11), bg="#e1e8ed", fg="#16a085")
        self.best_prompt_label.pack(side=tk.RIGHT, padx=10)
        # Current loss display with styling
        self.loss_frame = tk.Frame(root, bg="#f0f4f7", padx=20, pady=5)
        self.loss_frame.pack(fill=tk.X)
        
        self.loss_label = tk.Label(self.loss_frame, text="当前 Loss: --", font=("Arial", 14, "bold"), 
                                 bg="#f0f4f7", fg="#e74c3c")
        self.loss_label.pack(side=tk.LEFT)
        
        self.loss_indicator = tk.Canvas(self.loss_frame, width=20, height=20, bg="#f0f4f7", highlightthickness=0)
        self.loss_indicator.pack(side=tk.LEFT, padx=(10, 0))
        self.draw_loss_indicator("gray")
        
        # Images frame
        self.image_frame = tk.Frame(root, bg="#f0f4f7")
        self.image_frame.pack(pady=15, expand=True)
        
        # Target image section
        target_section = tk.Frame(self.image_frame, bg="#f0f4f7")
        target_section.grid(row=0, column=0, padx=20)
        
        self.target_label = tk.Label(target_section, text="目标图片", font=("Arial", 12, "bold"), bg="#f0f4f7")
        self.target_label.pack(pady=(0, 5))
        
        self.target_canvas = tk.Label(target_section, bg="#ffffff", relief=tk.RIDGE, bd=2, width=400, height=400)
        self.target_canvas.pack()
        
        # Generated image section
        generated_section = tk.Frame(self.image_frame, bg="#f0f4f7")
        generated_section.grid(row=0, column=1, padx=20)
        
        self.generated_label = tk.Label(generated_section, text="生成图片", font=("Arial", 12, "bold"), bg="#f0f4f7")
        self.generated_label.pack(pady=(0, 5))
        
        self.generated_canvas = tk.Label(generated_section, bg="#ffffff", relief=tk.RIDGE, bd=2, width=400, height=400)
        self.generated_canvas.pack()
        
        # Status bar
        self.status_bar = tk.Label(root, text="准备就绪，请加载目标图片", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Variables to track game state
        self.target_image = None
        self.generated_image = None
        self.best_loss = float('inf')
        self.attempts = 0
        
        # Add keyboard shortcut
        self.root.bind('<Return>', lambda event: self.generate_image())

    def configure_styles(self):
        """Configure custom styles for ttk widgets"""
        style = ttk.Style()
        
        # Button styles
        style.configure("Accent.TButton", 
                       font=("Arial", 10, "bold"),
                       background="#4CAF50",
                       foreground="white")
        
        style.configure("Generate.TButton", 
                       font=("Arial", 10, "bold"),
                       background="#2196F3",
                       foreground="white")
        
        style.map("Accent.TButton",
                 background=[('active', '#3d8b40'), ('pressed', '#2e6830')],
                 foreground=[('active', 'black'), ('pressed', 'black')])
        
        style.map("Generate.TButton",
                 background=[('active', '#0b7dda'), ('pressed', '#0a5a9c')],
                 foreground=[('active', 'black'), ('pressed', 'black')])

    def load_image(self):
        """Load a target image from file system"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if not file_path:
            return
            
        try:
            self.target_image = Image.open(file_path)
            self.display_image(self.target_image, self.target_canvas)
            self.display_image(Image.open('./black.png'), self.generated_canvas)
            # Reset game state
            self.loss_label.config(text="当前 Loss: --")
            self.generated_canvas.config(image='')
            self.status_bar.config(text=f"已加载图片: {os.path.basename(file_path)}")
            self.best_loss = float('inf')
            self.attempts = 0
            self.attempts_label.config(text=f"尝试次数: {self.attempts}")
            self.best_loss_label.config(text=f"最佳 Loss: --")
            self.draw_loss_indicator("gray")
        except Exception as e:
            self.status_bar.config(text=f"错误: {str(e)}")

    def generate_image(self):
        """Generate an image based on the prompt"""
        prompt = self.prompt_entry.get().strip()
        if not self.target_image:
            self.status_bar.config(text="错误: 请先加载目标图片")
            return
        self.status_bar.config(text=f"正在生成图片，请稍候...")
        self.root.update()
        try:
            # Call the image generation API
            if prompt=='':
                self.generated_image = Image.open('./black.png')
            else:
                self.generated_image = get_image_generate(prompt)
            self.display_image(self.generated_image, self.generated_canvas)
            
            # Calculate loss
            loss = get_loss(self.target_image, self.generated_image)
            # Update attempt counter
            self.attempts += 1
            self.attempts_label.config(text=f"尝试次数: {self.attempts}")
            
            # Update loss display
            self.loss_label.config(text=f"当前 Loss: {loss:.4f}")
            
            # Update best loss if applicable
            if loss < self.best_loss:
                self.best_loss = loss
                self.best_loss_label.config(text=f"最佳 Loss: {loss:.4f}")
                self.best_prompt_label.config(text=f"最佳提示词: {prompt}")
                self.generated_image.save(f"best_image_{self.attempts}.png")
                self.status_bar.config(text=f"已保存最佳图片: best_image_{self.attempts}.png")
                with open(f"best_prompt_{self.attempts}.txt", "w") as f:
                    f.write(prompt)
                color = self.get_loss_color(loss)
                self.draw_loss_indicator(color)
                
                if loss < 0.3:
                    self.status_bar.config(text=f"太棒了！你找到了一个非常接近的匹配 (Loss: {loss:.4f})")
                else:
                    self.status_bar.config(text=f"已生成图片 (Loss: {loss:.4f})")
            else:
                self.status_bar.config(text=f"已生成图片 (Loss: {loss:.4f}, 非最佳)")
                self.draw_loss_indicator("orange")
        except Exception as e:
            self.status_bar.config(text=f"生成错误: {str(e)}")

    def display_image(self, pil_image, canvas_label):
        """Display an image on the specified canvas"""
        # Resize the image to fit the canvas while maintaining aspect ratio
        width, height = pil_image.size
        max_size = 400
        
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
            
        resized = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a new blank image with the canvas size
        display_img = Image.new("RGB", (max_size, max_size), color="white")
        
        # Paste the resized image in the center
        x_offset = (max_size - new_width) // 2
        y_offset = (max_size - new_height) // 2
        display_img.paste(resized, (x_offset, y_offset))
        
        # Convert to Tkinter PhotoImage and display
        tk_image = ImageTk.PhotoImage(display_img)
        canvas_label.img = tk_image
        canvas_label.config(image=tk_image)

    def get_loss_color(self, loss):
        """Return a color based on the loss value"""
        if loss < 0.2:
            return "#27ae60"  # Green (very good)
        elif loss < 0.3:
            return "#2ecc71"  # Light green (good)
        elif loss < 0.4:
            return "#f39c12"  # Orange (moderate)
        elif loss < 0.5:
            return "#e67e22"  # Dark orange (poor)
        else:
            return "#e74c3c"  # Red (bad)

    def draw_loss_indicator(self, color):
        """Draw a colored circle indicator for the loss value"""
        self.loss_indicator.delete("all")
        self.loss_indicator.create_oval(2, 2, 18, 18, fill=color, outline="")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImagePromptGame(root)
    root.mainloop()