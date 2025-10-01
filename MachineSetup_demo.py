import os
import sys
import tkinter as tk
from tkinter import filedialog

sys.dont_write_bytecode = True

#sys.path.append(r"K:\10. Released Software\Shared Python Programs\production-2.1")
sys.path.append(r"C:\Users\tbates\Python\shared-python-programs\Generate MCD")
from GenerateMCD import AerotechController

# --- Configuration ---
# These paths are derived from the required directory structure.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#AEROTECH_DLL_PATH = os.path.join(BASE_DIR, "extern", "Automation1")

def main_menu():
    """Prints the main menu options."""
    print("\n" + "="*50)
    print("      Aerotech MCD Generation Demo")
    print("="*50)
    print("1. WF1: Create a CALCULATED MCD from JSON specs")
    print("2. WF2: Create a NON-CALCULATED MCD from JSON specs")
    print("3. WF3: Convert an existing MCD file to a JSON file")
    print("4. WF4: CALCULATE parameters from an existing MCD file")
    print("5. Exit")
    print("-"*50)
    return input("Select an option (1-5): ")

def run_workflow_1(controller):
    """WF1: Creates a new, calculated MCD file from a predefined dictionary."""
    print("\n--- Running Workflow 1: JSON Specs -> Calculated MCD ---")
    stage_type = 'PRO165LM'
    axis = 'Z'
    specs_dict = {
        'Travel': '-0100',
        'Feedback': '-E1',
        'Cable Management': '-CMS2'
    }
    print(f"Using example Stage: {stage_type} ({axis}-axis)")
    print(f"With specs: {specs_dict}")
    
    _, _, output_path = controller.calculate_parameters(
        specs_dict=specs_dict, 
        stage_type=stage_type, 
        axis=axis
    )
    print(f"\n✅ Success! Calculated MCD file saved to: {output_path}")
    return output_path

def run_workflow_2(controller):
    """WF2: Creates a new, non-calculated MCD file from a predefined dictionary."""
    print("\n--- Running Workflow 2: JSON Specs -> Non-Calculated MCD ---")
    stage_type = 'PRO165'
    axis = 'X'
    specs_dict = {
        'Direct Linear Feedback': 'SL', 
        'Travel': '-100', 
        'Tabletop': '-TT1'
    }
    print(f"Using example Stage: {stage_type} ({axis}-axis)")
    print(f"With specs: {specs_dict}")

    _, output_path, _ = controller.convert_to_mcd(
        specs_dict=specs_dict, 
        stage_type=stage_type, 
        axis=axis, 
        workflow='wf2'
    )

    print(f"\n✅ Success! Non-calculated MCD file saved to: {output_path}")
    return output_path

def run_workflow_3(controller, created_mcd_path):
    """WF3: Converts an existing MCD file to a JSON file."""
    print("\n--- Running Workflow 3: MCD -> JSON ---")
    if not created_mcd_path or not os.path.exists(created_mcd_path):
        print("\n⚠️ No MCD file has been created yet. Please run Workflow 1 or 2 first.")
        return

    print(f"Using the MCD file generated previously: {created_mcd_path}")
    output_json_path = os.path.join(BASE_DIR, f"{os.path.basename(created_mcd_path).split('.')[0]}_converted.json")
    
    controller.convert_to_json(created_mcd_path, output_json_path)
    print(f"\n✅ Success! MCD converted to JSON at: {output_json_path}")

def run_workflow_4(controller):
    """WF4: Asks the user for an MCD file and calculates its parameters."""
    print("\n--- Running Workflow 4: Existing MCD -> Calculated MCD ---")
    
    # Hide the root Tkinter window
    root = tk.Tk()
    root.withdraw()
    
    mcd_file_path = os.path.join(BASE_DIR, "PRO165LM XY-No Load.mcd")
    
    if not mcd_file_path:
        print("No file selected. Returning to menu.")
        return

    print(f"Selected file: {mcd_file_path}")

    # Read the file into a .NET object
    read_from_file = controller.MachineControllerDefinition.GetMethod("ReadFromFile")
    original_mcd_obj = read_from_file.Invoke(None, [mcd_file_path])

    if original_mcd_obj:
        print("Successfully read MCD file into memory.")
        # Calculate parameters from the object
        _, output_path, _ = controller.calculate_from_current_mcd(original_mcd_obj)
        print(f"\n✅ Success! New calculated MCD file saved to: {output_path}")
    else:
        print("\n❌ Failed to read the MCD file.")

if __name__ == "__main__":
    try:
        # 1. Create the controller object
        controller = AerotechController(
        )
        # 2. Explicitly initialize the controller (loads DLLs)
        controller.initialize()

    except (FileNotFoundError, TypeError, RuntimeError, KeyError, Exception) as e:
        print(f"\n❌ CRITICAL ERROR during initialization: {e}")
        print("Please ensure all required files and folders are in the correct locations.")
        sys.exit(1)

    # Variable to store the path of a newly created MCD for WF3
    last_created_mcd = None

    while True:
        choice = main_menu()
        try:
            if choice == '1':
                last_created_mcd = run_workflow_1(controller)
            elif choice == '2':
                last_created_mcd = run_workflow_2(controller)
            elif choice == '3':
                run_workflow_3(controller, last_created_mcd)
            elif choice == '4':
                run_workflow_4(controller)
            elif choice == '5':
                print("Exiting demo.")
                break
            else:
                print("Invalid option. Please try again.")
        except Exception as e:
            print(f"\n❌ An error occurred during the workflow: {e}")
            if hasattr(e, 'InnerException') and e.InnerException:
                print(f"  Inner .NET Exception: {e.InnerException}")
        
        input("\nPress Enter to return to the menu...")