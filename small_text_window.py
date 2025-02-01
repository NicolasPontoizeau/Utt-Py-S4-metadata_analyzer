import tkinter as tk
from tkinter import filedialog, messagebox

def load():
    # Open a file dialog to select a JSON file
    file_path = filedialog.askopenfilename(
        title="Sélectionner un fichier JSON",
        filetypes=[("Fichiers JSON", "*.json")]
    )
    if not file_path:
        return  # User canceled the dialog

    try:
        # Clear the current content of the Text widget
        results_text.config(state="normal")  # Enable editing
        results_text.delete("1.0", tk.END)  # Clear all content

        # Open and read the file
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()  # Read the entire file content
            results_text.insert(tk.END, content)  # Insert content into the Text widget

        # Disable editing in the Text widget after loading the file
        results_text.config(state="disabled")

        # Print the file path to the console
        print(f"Fichier .json sélectionné : {file_path} chargé")

    except Exception as e:
        # Show an error message if something goes wrong
        messagebox.showerror("Erreur", f"Impossible de lire le fichier JSON : {e}")

# Create the main application window
window = tk.Tk()
window.title("JSON File Viewer")

# Create a Text widget to display the file content
results_text = tk.Text(window, wrap="word", state="disabled")
results_text.pack(expand=True, fill="both")

# Create a button to trigger the file loading
load_button = tk.Button(window, text="Charger un fichier JSON", command=load)
load_button.pack(pady=10)

# Start the Tkinter event loop
window.mainloop()