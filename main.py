from tkinter import *
import subprocess
import os
import shutil
from tkinter import filedialog
import xml.etree.ElementTree as ET

# Function to parse the original XML and get field names and types
def parse_xml_fields(config_file):
    fields = []
    try:
        # Parse the original configuration XML
        tree = ET.parse(config_file)
        root = tree.getroot()

        # Find all 'field' elements under 'recipe'
        recipe = root.find("recipe")
        if recipe is not None:
            for field in recipe.findall("field"):
                name = field.get("name")
                type_ = field.get("type")
                fields.append((name, type_))
        else:
            print("Error: 'recipe' element not found in XML.")
    
    except Exception as e:
        print(f"Error parsing XML: {e}")
    
    return fields

# Function to create a new XML with selected fields and their types
def create_new_xml(selected_fields, config_file, output_filename="selected_fields_config.xml"):
    try:
        # Parse the original configuration XML to get the field types
        fields_and_types = parse_xml_fields(config_file)
        
        # Create the root element for the new XML
        root = ET.Element("rtde_config")
        recipe = ET.SubElement(root, "recipe", key="out")

        # Add selected fields to the XML with their types
        for selected_field in selected_fields:
            # Find the type of the selected field
            field_type = next((field_type for field_name, field_type in fields_and_types if field_name == selected_field), None)
            if field_type:
                ET.SubElement(recipe, "field", name=selected_field, type=field_type)
            else:
                print(f"Warning: Field '{selected_field}' not found in the original XML.")
        
        # Write the tree to a new XML file
        tree = ET.ElementTree(root)
        tree.write(output_filename)
        
        return output_filename
    except Exception as e:
        print(f"Error creating XML: {e}")
        return None


# Function to run record.py with command-line arguments
def run_record_script():
    try:
        # Collect arguments from the input fields
        host = host_entry.get() or "192.168.56.101"
        port = port_entry.get() or 30004
        samples = samples_entry.get() or 0
        frequency = frequency_entry.get() or 125
        output_file = output_entry.get() or "robot_data.csv"
       

        # Determine which config file to use
        config_file = "record_configuration.xml" 

        # Collect selected fields from the listbox
        selected_fields = [field_listbox.get(i) for i in field_listbox.curselection()]

        # Create new XML file with selected fields (pass both selected_fields and config_file)
        new_config_file = create_new_xml(selected_fields, config_file)  # <-- Fix here
        
        if new_config_file is None:
            return  # If the new config file creation failed, stop further execution

        # Build the command with arguments
        command = [
            "python", "record.py", 
            "--host", host, 
            "--port", str(port), 
            "--samples", str(samples), 
            "--frequency", str(frequency), 
            "--config", config_file,  # Use the new XML file
            "--output", output_file
            
        ]

        # Filter out empty strings from the command list
        command = [arg for arg in command if arg]

        # Run the command and capture output
        result = subprocess.run(command, capture_output=True, text=True)

        # Display the captured output in a label
        output_text.set(result.stdout)  # Display standard output
        error_text.set(result.stderr)   # Display standard error if any

        # Check if the file was created by record.py
        if os.path.exists(output_file):
            download_button.config(state=NORMAL)  # Enable the download button if file exists
        else:
            download_button.config(state=DISABLED)  # Disable the download button if file doesn't exist

    except Exception as e:
        output_text.set(f"Error: {e}")  # If there is an error running the script

# Function to download the .csv file
def download_file():
    try:
        # Ask user to select the location to save the file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            # Move the generated .csv file to the chosen location
            shutil.copy("robot_data.csv", file_path)
            output_text.set(f"File saved to {file_path}")
        else:
            output_text.set("Download cancelled.")

    except Exception as e:
        output_text.set(f"Error: {e}")

# Function to load fields from the selected config file and populate the listbox
def load_fields():
    # Clear the current listbox content
    field_listbox.delete(0, END)

    # Get the selected config file (default or custom)
    config_file = "record_configuration.xml" 
    
    # Parse the XML and get the available fields
    fields = parse_xml_fields(config_file)

    # Populate the listbox with field names
    for field in fields:
        field_listbox.insert(END, field)

# Setting up the GUI
root = Tk()
root.title("Run record.py")
#root.iconbitmap("image/logo.png")
root.geometry("800x800")

# Frame for Parameter Input Fields
input_frame = Frame(root)
input_frame.pack(padx=10, pady=10)

# Host
host_label = Label(input_frame, text="Host:")
host_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
host_entry = Entry(input_frame)
host_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

# Port
port_label = Label(input_frame, text="Port:")
port_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")
port_entry = Entry(input_frame)
port_entry.grid(row=0, column=3, padx=10, pady=5, sticky="w")

# Samples
samples_label = Label(input_frame, text="Number of Samples:")
samples_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
samples_entry = Entry(input_frame)
samples_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Frequency
frequency_label = Label(input_frame, text="Frequency (Hz):")
frequency_label.grid(row=1, column=2, padx=10, pady=5, sticky="e")
frequency_entry = Entry(input_frame)
frequency_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

# Output File
output_label = Label(input_frame, text="Output File:")
output_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
output_entry = Entry(input_frame)
output_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Frame for Config and Load Fields
config_frame = Frame(root)
config_frame.pack(padx=10, pady=10)

# Load fields button
load_fields_button = Button(config_frame, text="Choose data", command=load_fields)
load_fields_button.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# Listbox for Fields (multi-selection)
field_listbox = Listbox(config_frame, selectmode=MULTIPLE, width=40, height=10)
field_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=5)


# Run Script Button
button_run = Button(root, text="Run record.py", command=run_record_script)
button_run.pack(padx=10, pady=10)

# Output Display
output_text = StringVar()
output_label = Label(root, textvariable=output_text)
output_label.pack(padx=10, pady=10)

# Error Display
error_text = StringVar()
error_label = Label(root, textvariable=error_text, fg="red")
error_label.pack(padx=10, pady=5)

# Download Button (Initially disabled)
download_button = Button(root, text="Download CSV", command=download_file, state=DISABLED)
download_button.pack(padx=10, pady=10)

# Quit Button
button_quit = Button(root, text="Exit Program", command=root.quit)
button_quit.pack(padx=10, pady=10)

root.mainloop()
