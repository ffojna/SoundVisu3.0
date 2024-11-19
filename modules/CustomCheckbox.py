import tkinter as tk
from tkinter import PhotoImage

class CustomCheckbox(tk.Checkbutton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Load custom images for checked and unchecked states
        self.checked_icon = PhotoImage(file="images/onCheck.png")  # Replace with your checked image
        self.unchecked_icon = PhotoImage(file="images/offCheck.png")  # Replace with your unchecked image

        # Configure the widget
        self.config(
            image=self.unchecked_icon,  # Use the unchecked image by default
            selectimage=self.checked_icon,  # Switch to checked image when selected
            indicatoron=False,  # Hide the standard checkbox indicator
            padx=0,  # Remove horizontal padding
            pady=0,  # Remove vertical padding
            borderwidth=0,  # Remove border
            highlightthickness=0,  # Remove highlight
            relief=tk.FLAT,  # Remove relief
        )

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Custom Checkbox Example")
    label = tk.Label(root, text="Click to check/uncheck checkbox:")
    label.pack()
    custom_checkbox = CustomCheckbox(root)
    custom_checkbox.pack(padx=20, pady=20)

    root.mainloop()
