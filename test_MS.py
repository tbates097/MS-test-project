"""
Minimal test script to demonstrate Aerotech DLL loading and usage.
This script attempts to load and use the minimum required Aerotech functionality.
"""
from pythonnet import load
load("coreclr")
import os
import sys
import json

# Import System for Type.GetType
import System
from System.Collections.Generic import List
from System import String

import clr

def update_configured_options(
    specs_dict,
    stage_type=None,
    axis=None,
    json_filename="test drive temp.json",
    output_filename="test drive working.json"
):
    """
    Update the ConfiguredOptions section under MechanicalProducts in the given JSON file,
    and write the result to a new file to avoid overwriting the template.
    """
    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, json_filename)
    output_path = os.path.join(base_dir, output_filename)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Update MechanicalProducts[0]
    mech_products = data.get("MechanicalProducts")
    if not mech_products or not isinstance(mech_products, list) or len(mech_products) == 0:
        raise KeyError("MechanicalProducts group not found or is empty in JSON.")
    mech_product = mech_products[0]

    # Update ConfiguredOptions
    if "ConfiguredOptions" not in mech_product or not isinstance(mech_product["ConfiguredOptions"], dict):
        mech_product["ConfiguredOptions"] = {}
    mech_product["ConfiguredOptions"].update(specs_dict)

    # Optionally update Name and DisplayName
    if stage_type is not None:
        mech_product["Name"] = stage_type
        mech_product["DisplayName"] = stage_type

    # Update InterconnectedAxes[0]
    interconnected_axes = data.get("InterconnectedAxes")
    if interconnected_axes and isinstance(interconnected_axes, list) and len(interconnected_axes) > 0:
        inter_axis = interconnected_axes[0]
        if axis is not None:
            inter_axis["Name"] = axis
        if stage_type is not None and "MechanicalAxis" in inter_axis:
            inter_axis["MechanicalAxis"]["DisplayName"] = stage_type

    # Save back to a new file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"ConfiguredOptions updated in {output_path}")

def main():
    print("Python version:", sys.version)
    print("Platform:", sys.platform)
    print("\nAttempting to load Aerotech assemblies...")

    # Add Aerotech DLL directory to PATH
    AEROTECH_DLL_PATH = os.path.join(os.path.dirname(__file__), "extern", "Automation1")
    if not os.path.exists(AEROTECH_DLL_PATH):
        print(f"ERROR: Aerotech DLL path not found: {AEROTECH_DLL_PATH}")
        return
    
    # Add ConfigurationManager path
    CONFIG_MANAGER_PATH = os.path.join(os.path.dirname(__file__), "System.Configuration.ConfigurationManager.8.0.0", "lib", "netstandard2.0")
    if not os.path.exists(CONFIG_MANAGER_PATH):
        print(f"ERROR: ConfigurationManager not found at {CONFIG_MANAGER_PATH}")
        return
    
    os.environ["PATH"] = AEROTECH_DLL_PATH + ";" + os.environ["PATH"]
    os.add_dll_directory(AEROTECH_DLL_PATH)
    
    try:
        # Load Newtonsoft.Json first
        print("\nLoading Newtonsoft.Json...")
        clr.AddReference(os.path.join(AEROTECH_DLL_PATH, "Newtonsoft.Json.dll"))
        import Newtonsoft.Json
        import Newtonsoft.Json.Linq
        print("Newtonsoft.Json loaded successfully")

        # Load ConfigurationManager
        print("\nLoading ConfigurationManager...")
        clr.AddReference(os.path.join(CONFIG_MANAGER_PATH, "System.Configuration.ConfigurationManager.dll"))
        
        # Then load the Aerotech DLLs
        print("Loading Aerotech assemblies...")
        clr.AddReference(os.path.join(AEROTECH_DLL_PATH, "Aerotech.Automation1.Applications.Core.dll"))
        print("Aerotech.Core loaded successfully")
        clr.AddReference(os.path.join(AEROTECH_DLL_PATH, "Aerotech.Automation1.Applications.Interfaces.dll"))
        print("Aerotech.Interfaces loaded successfully")
        clr.AddReference(os.path.join(AEROTECH_DLL_PATH, "Aerotech.Automation1.Applications.Shared.dll"))
        print("Aerotech.Shared loaded successfully")
        clr.AddReference(os.path.join(AEROTECH_DLL_PATH, "Aerotech.Automation1.DotNetInternal.dll"))
        print("Aerotech.DotNetInternal loaded successfully")
        clr.AddReference(os.path.join(AEROTECH_DLL_PATH, "Aerotech.Automation1.Applications.Wpf.dll"))
        print("Aerotech.Wpf loaded successfully")
        
        # Get the types using assembly-qualified names
        type_name1 = "Aerotech.Automation1.Applications.Wpf.McdFormatConverter, Aerotech.Automation1.Applications.Wpf"
        type_name2 = "Aerotech.Automation1.DotNetInternal.MachineControllerDefinition, Aerotech.Automation1.DotNetInternal"
        McdFormatConverter = System.Type.GetType(type_name1)
        MachineControllerDefinition = System.Type.GetType(type_name2)
        
        if McdFormatConverter is None or MachineControllerDefinition is None:
            print("\nFATAL: One or both types could not be found. They may not be public, or the namespace may be different.")
            return

        warnings = List[String]()

        print("Successfully loaded required types")
        
        #specs_dict = {'Direct Linear Feedback': 'SL', 'Travel': '-100', 'Tabletop': '-TT1', 'Motor': '-M1', 'Foldback': '', 'Limits': '-LI1', 'Lifting Hardware': ''}
        specs_dict = {'Travel': '-0100', 'Feedback': '-E1', 'Motor': '-M1', 'Cable Management': '-CMS2'}
        stage_type = 'PRO165LM'
        axis = 'X'
        # Update ConfiguredOptions in JSON
        print("\nUpdating ConfiguredOptions in JSON...")
        update_configured_options(specs_dict, stage_type=stage_type, axis=axis)
        print("ConfiguredOptions updated successfully")

        # Load your JSON file as a .NET JObject
        base_dir = os.path.dirname(__file__)
        json_path = os.path.join(base_dir, "test drive working.json")
        with open(json_path, "r", encoding="utf-8") as f:
            json_str = f.read()

        # Parse the JSON string into a .NET JObject
        jobject = Newtonsoft.Json.Linq.JObject.Parse(json_str)

        # Get the ConvertToMcd method
        convert_to_mcd = McdFormatConverter.GetMethod("ConvertToMcd")

        # Prepare the arguments: JObject and warnings (as out parameter)
        # In pythonnet, out/ref parameters are passed as normal arguments and will be updated in place
        args = [jobject, warnings]
        # 2. DEBUG STEP: Print the object to verify its contents
        print("--- Verifying JSON object before passing to C# ---")
        print(jobject.ToString())
        print("-------------------------------------------------")
        # Call the method
        mcd_obj = convert_to_mcd.Invoke(None, args)

        print("ConvertToMcd returned:", mcd_obj)
        print("Warnings after ConvertToMcd:")
        if warnings and warnings.Count > 0:
            for warning in warnings:
                print("-", warning)
        else:
            print("No warnings were generated.")
        
        mcd_output = 'output.mcd'
        mcd_output_path = os.path.join(base_dir, mcd_output)

        write_method = MachineControllerDefinition.GetMethod("WriteToFile")
        print(f"\nWriting MCD to file: {mcd_output_path}")
        write_method.Invoke(mcd_obj, [mcd_output_path])
        print(f"MCD written successfully to {mcd_output_path}")
        '''
        # Calculate parameters
        print("\nCalculating parameters...")
        calculate_parameters = McdFormatConverter.GetMethod("CalculateParameters")
        calculated_mcd = calculate_parameters.Invoke(None, [mcd_obj, warnings])
        
        print("\nCalculation complete!")
        print(f'Return from CalculateParameters: {calculated_mcd}')
        if warnings.Count > 0:
            print("\nWarnings during calculation:")
            for warning in warnings:
                print(f"- {warning}")
        else:
            print("No warnings generated during calculation")
        
        mcd_output = 'output.mcd'
        mcd_output_path = os.path.join(base_dir, mcd_output)

        write_method = MachineControllerDefinition.GetMethod("WriteToFile")
        print(f"\nWriting MCD to file: {mcd_output_path}")
        write_method.Invoke(mcd_obj, [mcd_output_path])
        print(f"MCD written successfully to {mcd_output_path}")
        
        # Try to read an old MCD file
        original_mcd_path = os.path.join(os.path.dirname(__file__), "PRO165LM.mcd")
        print(f"\nAttempting to read MCD file: {original_mcd_path}")
        read_from_file = MachineControllerDefinition.GetMethod("ReadFromFile")
        original_mcd = read_from_file.Invoke(None, [original_mcd_path])
        print(f'MCD File: {original_mcd}')
        print("Successfully read MCD file")
        '''
        # Try to read an new MCD file
        new_mcd_path = os.path.join(os.path.dirname(__file__), "output.mcd")
        print(f"\nAttempting to read MCD file: {new_mcd_path}")
        read_from_file = MachineControllerDefinition.GetMethod("ReadFromFile")
        new_mcd = read_from_file.Invoke(None, [new_mcd_path])
        print(f'MCD File: {new_mcd}')
        print("Successfully read MCD file")
        '''
        # Extract json from MCD
        print("\nExtracting JSON from MCD...")
        extract_json = McdFormatConverter.GetMethod("ConvertToJson")
        json = extract_json.Invoke(None, [original_mcd, warnings])
        print("JSON extraction complete!")
        # Save JSON to file
        json_path = os.path.join(os.path.dirname(__file__), "original.json")
        with open(json_path, 'w') as f:
            f.write(json.ToString())  # <-- Convert JObject to string
        print(f"JSON saved to {json_path}")
        '''
        # Extract json from MCD
        print("\nExtracting JSON from MCD...")
        extract_json = McdFormatConverter.GetMethod("ConvertToJson")
        json = extract_json.Invoke(None, [new_mcd, warnings])
        print("JSON extraction complete!")
        # Save JSON to file
        json_path = os.path.join(os.path.dirname(__file__), "new.json")
        with open(json_path, 'w') as f:
            f.write(json.ToString())  # <-- Convert JObject to string
        print(f"JSON saved to {json_path}")
        
    except Exception as e:
        print("\nERROR: An exception occurred:")
        print(str(e))
        print("\nException type:", type(e).__name__)
        if hasattr(e, 'InnerException') and e.InnerException:
            print("\nInner Exception:")
            print(str(e.InnerException))

if __name__ == "__main__":
    main()