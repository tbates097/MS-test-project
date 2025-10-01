#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCD Payload UI - Simple interface for modifying MCD payload values
Created by: Assistant
Description: UI for selecting MCD file, connecting to controller, and modifying payloads
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import tkinter.font as tkFont
import threading
import queue
import sys
import os
from datetime import datetime
import tempfile
import zipfile
import xml.etree.ElementTree as ET
import shutil

# Import required modules
import automation1 as a1
from GenerateMCD import AerotechController

class RedirectText:
    """Redirect stdout to a text widget"""
    def __init__(self, text_widget, queue_obj):
        self.text_widget = text_widget
        self.queue = queue_obj
        
    def write(self, text):
        self.queue.put(text)
        
    def flush(self):
        pass

class MCDPayloadUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MCD Payload Modifier - v1.0")
        self.root.configure(bg='white')
        
        # Configure styles
        self.setup_styles()
        
        # Initialize variables
        self.controller = None
        self.available_axes = []
        self.mcd_path = None
        self.mcd_name = None
        self.payload_vars = {}
        
        # Add stop event for thread control
        self.stop_event = threading.Event()
        self.process_thread = None
        
        # Setup main frame
        self.setup_main_frame()
        
        # Setup content
        self.setup_content()
        
        # Setup output redirection
        self.output_queue = queue.Queue()
        self.redirect_text = RedirectText(self.output_text, self.output_queue)
        
        # Start queue monitoring
        self.monitor_output()
        
    def setup_styles(self):
        """Configure ttk styles with Aerotech brand guidelines"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Aerotech Brand Colors (from UI Guidelines)
        BRAND_BLUE_1 = '#0082BE'        # Primary Blue
        BRAND_GREY_1 = '#4B545E'        # Primary Grey
        BRAND_GREY_2 = '#DAE1E9'        # Light Grey
        BRAND_BLACK = '#231F20'         # Primary Black
        BRAND_GREY_3 = '#B5BBC3'        # Medium Grey
        BRAND_GREEN_1 = '#459A34'       # Success Green
        BRAND_RED_1 = '#DB2115'         # Error Red
        BRAND_ORANGE_1 = '#EF8B22'      # Warning Orange
        
        # Brand Fonts (with fallbacks for system compatibility)
        HEADLINE_FONT = ('Source Sans Pro', 'Arial', 'sans-serif')
        BODY_FONT = ('Source Sans Pro', 'Arial', 'sans-serif')
        
        # Configure text styles with brand fonts and white backgrounds
        style.configure('Title.TLabel', 
                       font=(HEADLINE_FONT[0], 16, 'bold'), 
                       foreground=BRAND_BLUE_1,
                       background='white')
        style.configure('Subtitle.TLabel', 
                       font=(BODY_FONT[0], 12), 
                       foreground=BRAND_GREY_1,
                       background='white')
        style.configure('Header.TLabel', 
                       font=(HEADLINE_FONT[0], 14, 'bold'), 
                       foreground=BRAND_BLUE_1,
                       background='white')
        style.configure('Success.TLabel', 
                       font=(BODY_FONT[0], 10), 
                       foreground=BRAND_GREEN_1,
                       background='white')
        style.configure('Error.TLabel', 
                       font=(BODY_FONT[0], 10), 
                       foreground=BRAND_RED_1,
                       background='white')
        style.configure('Warning.TLabel', 
                       font=(BODY_FONT[0], 10), 
                       foreground=BRAND_ORANGE_1,
                       background='white')
        
        # Configure buttons with brand colors and fonts
        style.configure('Action.TButton', 
                       font=(BODY_FONT[0], 10, 'bold'),
                       background=BRAND_BLUE_1,
                       foreground='white')
        style.map('Action.TButton',
                 background=[('active', '#1C94D2'),
                            ('pressed', BRAND_GREY_1)])
        
        style.configure('Nav.TButton', 
                       font=(BODY_FONT[0], 9),
                       background=BRAND_GREY_2,
                       foreground=BRAND_GREY_1)
        style.map('Nav.TButton',
                 background=[('active', BRAND_GREY_3),
                            ('pressed', BRAND_GREY_1)])
        
        # Configure progress bar
        style.configure('Brand.Horizontal.TProgressbar',
                       background=BRAND_BLUE_1,
                       troughcolor=BRAND_GREY_2,
                       borderwidth=0,
                       lightcolor=BRAND_BLUE_1,
                       darkcolor=BRAND_BLUE_1)
        
        # Configure other ttk elements to have white backgrounds
        style.configure('TLabelFrame', background='white')
        style.configure('TLabelFrame.Label', background='white')
        style.configure('TFrame', background='white')
        style.configure('TCheckbutton', background='white')
        style.configure('TRadiobutton', background='white')
        style.configure('TLabel', background='white')
        style.configure('TEntry', fieldbackground='white')
        
    def setup_main_frame(self):
        """Setup the main application frame with brand colors"""
        # Brand Colors
        BRAND_BLUE_1 = '#0082BE'
        BRAND_GREY_1 = '#4B545E'
        
        # Header frame with brand blue
        self.header_frame = tk.Frame(self.root, bg=BRAND_BLUE_1, height=80)
        self.header_frame.pack(fill='x', pady=(0, 10))
        self.header_frame.pack_propagate(False)
        
        # Title with white text on brand blue
        title_label = tk.Label(self.header_frame, text="MCD Payload Modifier", 
                              font=('Source Sans Pro', 18, 'bold'), fg='white', bg=BRAND_BLUE_1)
        title_label.pack(pady=20)
        
        # Main content frame
        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Control frame
        self.control_frame = tk.Frame(self.root, height=60, bg='white')
        self.control_frame.pack(fill='x', padx=20, pady=(0, 20))
        self.control_frame.pack_propagate(False)
        
    def setup_content(self):
        """Setup the main content area"""
        # MCD File Selection
        mcd_frame = tk.LabelFrame(self.content_frame, text="MCD File Selection", 
                                 font=('Source Sans Pro', 10, 'bold'),
                                 fg='#0082BE', bg='white')
        mcd_frame.pack(fill='x', pady=10, padx=20)
        
        # File selection row
        file_frame = tk.Frame(mcd_frame, bg='white')
        file_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(file_frame, text="MCD File:", style='Subtitle.TLabel').pack(side='left')
        
        self.mcd_path_var = tk.StringVar()
        self.mcd_entry = ttk.Entry(file_frame, textvariable=self.mcd_path_var, width=50, state='readonly')
        self.mcd_entry.pack(side='left', padx=(10, 10))
        
        self.browse_btn = ttk.Button(file_frame, text="Browse", style='Action.TButton',
                                    command=self.browse_mcd_file)
        self.browse_btn.pack(side='left')
        
        # Controller Connection
        conn_frame = tk.LabelFrame(self.content_frame, text="Controller Connection", 
                                  font=('Source Sans Pro', 10, 'bold'),
                                  fg='#0082BE', bg='white')
        conn_frame.pack(fill='x', pady=10, padx=20)
        
        # Connection options
        self.connection_var = tk.StringVar(value="auto")
        
        conn_options_frame = tk.Frame(conn_frame, bg='white')
        conn_options_frame.pack(fill='x', padx=10, pady=5)
        
        auto_radio = ttk.Radiobutton(conn_options_frame, text="Auto-detect connection", 
                                   variable=self.connection_var, value="auto")
        auto_radio.pack(anchor='w', pady=2)
        
        usb_radio = ttk.Radiobutton(conn_options_frame, text="Force USB connection", 
                                  variable=self.connection_var, value="usb")
        usb_radio.pack(anchor='w', pady=2)
        
        hyperwire_radio = ttk.Radiobutton(conn_options_frame, text="Force Hyperwire connection", 
                                        variable=self.connection_var, value="hyperwire")
        hyperwire_radio.pack(anchor='w', pady=2)
        
        # Connection status
        self.conn_status_frame = tk.Frame(conn_frame, bg='white')
        self.conn_status_frame.pack(fill='x', pady=10)
        
        self.conn_status_label = ttk.Label(self.conn_status_frame, text="Ready to connect to controller...",
                                          style='Subtitle.TLabel')
        self.conn_status_label.pack()
        
        # Connect button
        self.connect_btn = ttk.Button(conn_frame, text="Connect to Controller", 
                                     style='Action.TButton', command=self.connect_controller)
        self.connect_btn.pack(pady=10)
        
        # Available axes display
        self.axes_frame = tk.LabelFrame(self.content_frame, text="Available Axes", 
                                       font=('Source Sans Pro', 10, 'bold'),
                                       fg='#0082BE', bg='white')
        self.axes_frame.pack(fill='x', pady=10, padx=20)
        
        self.axes_label = ttk.Label(self.axes_frame, text="Connect to controller to see available axes",
                                   style='Subtitle.TLabel')
        self.axes_label.pack(pady=10)
        
        # Payload configuration
        self.payload_frame = tk.LabelFrame(self.content_frame, text="Payload Configuration", 
                                          font=('Source Sans Pro', 10, 'bold'),
                                          fg='#0082BE', bg='white')
        self.payload_frame.pack(fill='x', pady=10, padx=20)
        
        self.payload_content_frame = tk.Frame(self.payload_frame, bg='white')
        self.payload_content_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(self.payload_content_frame, text="Set payload values for each axis (kg):",
                 style='Subtitle.TLabel').pack(anchor='w')
        
        # Process button
        self.process_btn = ttk.Button(self.content_frame, text="Process MCD", 
                                     style='Action.TButton', command=self.process_mcd,
                                     state='disabled')
        self.process_btn.pack(pady=10)
        
        # Test output button
        self.test_btn = ttk.Button(self.content_frame, text="Test Output", 
                                  style='Nav.TButton', command=self.test_output)
        self.test_btn.pack(pady=5)
        
        # Progress display
        progress_frame = tk.LabelFrame(self.content_frame, text="Process Output", 
                                      font=('Source Sans Pro', 10, 'bold'),
                                      fg='#0082BE', bg='white')
        progress_frame.pack(fill='both', expand=True, pady=10, padx=20)
        
        self.output_text = scrolledtext.ScrolledText(progress_frame, height=25, 
                                                   font=('Courier', 10),
                                                   bg='#3D4543', fg='#00ADEF', 
                                                   insertbackground='#00ADEF')
        self.output_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Add initial text to show the output area is working
        self.output_text.insert(tk.END, "MCD Payload Modifier - Output Console\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n")
        self.output_text.insert(tk.END, "Ready to process MCD files...\n\n")
        self.output_text.see(tk.END)
        
    def test_output(self):
        """Test the output redirection to verify it's working"""
        print("🧪 Testing output redirection...")
        print("✅ If you can see this message, the output system is working!")
        print(f"📁 Current MCD path: {self.mcd_path}")
        print(f"🎮 Controller connected: {self.controller is not None}")
        print(f"📊 Available axes: {self.available_axes}")
        print("=" * 50)
    
    def browse_mcd_file(self):
        """Browse for MCD file"""
        file_path = filedialog.askopenfilename(
            title="Select MCD File",
            filetypes=[("MCD files", "*.mcd"), ("All files", "*.*")]
        )
        
        if file_path:
            self.mcd_path = file_path
            self.mcd_path_var.set(file_path)
            
            # Extract MCD name from path
            self.mcd_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Enable process button if controller is connected
            if self.controller:
                self.process_btn.config(state='normal')
    
    def connect_controller(self):
        """Handle connect button click - runs connection in separate thread"""
        self.connect_btn.config(text="Connecting...", state='disabled')
        self.conn_status_label.config(text="Connecting to controller...")
        
        def connect_thread():
            try:
                # Get the selected connection type
                connection_type = self.connection_var.get()
                
                # Use the connect function with the selected connection type
                self.controller, self.available_axes = self._establish_controller_connection(connection_type)
                
                # Update UI on main thread
                self.root.after(0, self.connection_success)
                
            except Exception as e:
                self.root.after(0, lambda e=e: self.connection_failed(str(e)))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _establish_controller_connection(self, connection_type="auto"):
        """Establish connection to controller using the specified connection type"""
        if connection_type == "usb":
            try:
                controller = a1.Controller.connect_usb()
                controller.start()
            except:
                raise Exception('USB connection failed. Check connections and try again.')
        elif connection_type == "hyperwire":
            try:
                controller = a1.Controller.connect()
                controller.start()
            except:
                raise Exception('Hyperwire connection failed. Check Firmware version and try again.')
        else:  # auto
            try:
                controller = a1.Controller.connect()
                controller.start()
            except:
                if messagebox.askyesno('Could Not Connect To Hyperwire', 'Is this an iDrive?'):
                    try:
                        controller = a1.Controller.connect_usb()
                        controller.start()
                    except:
                        raise Exception('USB connection failed. Check connections and try again.')
                else:
                    raise Exception('Hyperwire connection failed. Check Firmware version and try again.')
        
        connected_axes = {}
        non_virtual_axes = []
        
        number_of_axes = controller.runtime.parameters.axes.count
        
        if number_of_axes <= 12:
            for axis_index in range(0, 11):
                status_item_configuration = a1.StatusItemConfiguration()
                status_item_configuration.axis.add(a1.AxisStatusItem.AxisStatus, axis_index)
                
                result = controller.runtime.status.get_status_items(status_item_configuration)
                axis_status = int(result.axis.get(a1.AxisStatusItem.AxisStatus, axis_index).value)
                if (axis_status & 1 << 13) > 0:
                    connected_axes[controller.runtime.parameters.axes[axis_index].identification.axisname.value] = axis_index
            for key, value in connected_axes.items():
                non_virtual_axes.append(key)
        else:
            for axis_index in range(0, 32):
                status_item_configuration = a1.StatusItemConfiguration()
                status_item_configuration.axis.add(a1.AxisStatusItem.AxisStatus, axis_index)
                result = controller.runtime.status.get_status_items(status_item_configuration)
                axis_status = int(result.axis.get(a1.AxisStatusItem.AxisStatus, axis_index).value)
                if (axis_status & 1 << 13) > 0:
                    connected_axes[controller.runtime.parameters.axes[axis_index].identification.axisname.value] = axis_index
            for key, value in connected_axes.items():
                non_virtual_axes.append(key)
        
        if len(non_virtual_axes) == 0:
            # Try USB connection
            controller = a1.Controller.connect_usb()
            number_of_axes = controller.runtime.parameters.axes.count
            if number_of_axes <= 12:
                for axis_index in range(0, 11):
                    status_item_configuration = a1.StatusItemConfiguration()
                    status_item_configuration.axis.add(a1.AxisStatusItem.AxisStatus, axis_index)
                    
                    result = controller.runtime.status.get_status_items(status_item_configuration)
                    axis_status = int(result.axis.get(a1.AxisStatusItem.AxisStatus, axis_index).value)
                    if (axis_status & 1 << 13) > 0:
                        connected_axes[controller.runtime.parameters.axes[axis_index].identification.axisname.value] = axis_index
                for key, value in connected_axes.items():
                    non_virtual_axes.append(key)
            else:
                for axis_index in range(0, 32):
                    status_item_configuration = a1.StatusItemConfiguration()
                    status_item_configuration.axis.add(a1.AxisStatusItem.AxisStatus, axis_index)
                    result = controller.runtime.status.get_status_items(status_item_configuration)
                    axis_status = int(result.axis.get(a1.AxisStatusItem.AxisStatus, axis_index).value)
                    if (axis_status & 1 << 13) > 0:
                        connected_axes[controller.runtime.parameters.axes[axis_index].identification.axisname.value] = axis_index
                for key, value in connected_axes.items():
                    non_virtual_axes.append(key)
        
        return controller, non_virtual_axes
    
    def connection_success(self):
        """Handle successful connection"""
        self.connect_btn.config(text="Connected ✓", state='disabled')
        self.conn_status_label.config(text=f"Connected successfully! Controller: {self.controller.name}")
        
        # Update axes display
        axes_text = ", ".join(self.available_axes) if self.available_axes else "No axes found"
        self.axes_label.config(text=f"Available axes: {axes_text}")
        
        # Create payload input fields
        self.create_payload_inputs()
        
        # Enable process button if MCD is selected
        if self.mcd_path:
            self.process_btn.config(state='normal')
    
    def connection_failed(self, error_msg):
        """Handle failed connection"""
        self.connect_btn.config(text="Connect to Controller", state='normal')
        self.conn_status_label.config(text=f"Connection failed: {error_msg}")
        messagebox.showerror("Connection Error", f"Failed to connect to controller:\n{error_msg}")
    
    def create_payload_inputs(self):
        """Create payload input fields for each axis"""
        # Clear existing inputs
        for widget in self.payload_content_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.payload_content_frame, text="Set payload values for each axis (kg):",
                 style='Subtitle.TLabel').pack(anchor='w')
        
        self.payload_vars = {}
        
        # Create input fields for each axis
        if self.available_axes:
            for i, axis in enumerate(self.available_axes):
                frame = tk.Frame(self.payload_content_frame, bg='white')
                frame.pack(fill='x', pady=2)
                
                ttk.Label(frame, text=f"{axis}:", width=15, style='Subtitle.TLabel').pack(side='left')
                
                payload_var = tk.StringVar(value="0.0")
                self.payload_vars[axis] = payload_var
                
                payload_entry = ttk.Entry(frame, textvariable=payload_var, width=15)
                payload_entry.pack(side='left', padx=(10, 5))
                
                ttk.Label(frame, text="kg", style='Subtitle.TLabel').pack(side='left')
    
    def modify_mcd_payloads(self, mcd_path, payload_values):
        """
        Unpack the MCD, update LoadMass/LoadInertia in config/MachineSetupData for each axis in payload_values.
        Only updates if payload is nonzero.
        """
        temp_dir = tempfile.mkdtemp(prefix="mcd_extract_")
        try:
            # Extract the MCD
            with zipfile.ZipFile(mcd_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            msd_path = os.path.join(temp_dir, "config", "MachineSetupData")
            if not os.path.exists(msd_path):
                print("❌ MachineSetupData not found in MCD")
                return None

            tree = ET.parse(msd_path)
            root = tree.getroot()

            # Find all Stage components in order
            stages = []
            for mech_axis in root.findall(".//MachineSetupConfiguration/MechanicalProducts/MechanicalProduct/MechanicalAxes/MechanicalAxis"):
                stage = mech_axis.find("./Stage/LinearStageComponent")
                if stage is None:
                    stage = mech_axis.find("./Stage/RotaryStageComponent")
                if stage is not None:
                    stages.append(stage)

            # Get payload values in order
            payload_keys = list(payload_values.keys())
            payload_vals = [payload_values[k] for k in payload_keys if float(payload_values[k]) != 0]

            if not payload_vals:
                print("No nonzero payloads to update.")
                return None

            # Update stages in order
            updated = False
            for i, payload in enumerate(payload_vals):
                if i >= len(stages):
                    break
                stage = stages[i]
                # Try LoadMass first, then LoadInertia
                load_mass = stage.find("LoadMass")
                load_inertia = stage.find("LoadInertia")
                if load_mass is not None:
                    load_mass.text = str(payload)
                    updated = True
                elif load_inertia is not None:
                    load_inertia.text = str(payload)
                    updated = True

            if not updated:
                print("No LoadMass or LoadInertia fields updated.")
                return None

            # Save the modified MachineSetupData
            tree.write(msd_path, encoding='utf-8', xml_declaration=True)

            # Repack the MCD
            with zipfile.ZipFile(mcd_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                for root_dir, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        new_zip.write(file_path, arcname)
            print(f"✅ Payloads updated and new MCD saved as: {mcd_path}")
            return mcd_path

        except Exception as e:
            print(f"❌ Error modifying MCD payloads: {e}")
            return None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def modify_controller_name(self, mcd_path, mode="Loaded"):
        """Modify the controller name in the MCD file"""
        import re
        
        temp_dir = tempfile.mkdtemp(prefix="mcd_extract_")
        try:
            # Extract the MCD
            with zipfile.ZipFile(mcd_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            name_path = os.path.join(temp_dir, "config", "Names")
            if os.path.exists(name_path):
                name_tree = ET.parse(name_path)
                name_root = name_tree.getroot()

                # Find the ControllerName element
                controller_name_elem = name_root.find(".//ControllerName")
                if controller_name_elem is not None and controller_name_elem.text:
                    current_name = controller_name_elem.text.strip()
                    if mode.lower() == "no load":
                        # If "No Load" not present, add it
                        if re.search(r'no[\s\-]*load', current_name, flags=re.IGNORECASE):
                            new_text = current_name
                        else:
                            new_text = current_name + " No Load"
                    else:  # mode == "Loaded"
                        # Replace any "No Load" with "Loaded", or add "Loaded" if not present
                        new_text = re.sub(r'[\s\-]*no[\s\-]*load[\s\-]*', ' Loaded', current_name, flags=re.IGNORECASE)
                        if 'Loaded' not in new_text:
                            new_text = new_text.strip() + ' Loaded'
                    controller_name_elem.text = new_text.strip()
                    
                    # Save the modified Names file
                    name_tree.write(name_path, encoding='utf-8', xml_declaration=True)

                    # Repack the MCD
                    with zipfile.ZipFile(mcd_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                        for root_dir, dirs, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root_dir, file)
                                arcname = os.path.relpath(file_path, temp_dir)
                                new_zip.write(file_path, arcname)
                    
                    print(f"✅ Controller name updated: '{current_name}' → '{new_text}'")
                    return mcd_path
                else:
                    print("⚠️ ControllerName element not found in Names file")
                    return None
            else:
                print("⚠️ Names file not found in MCD")
                return None

        except Exception as e:
            print(f"❌ Error modifying controller name: {e}")
            return None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def process_mcd(self):
        """Process the MCD file with payload modifications"""
        if not self.mcd_path:
            messagebox.showerror("Error", "Please select an MCD file first!")
            return
        
        if not self.controller:
            messagebox.showerror("Error", "Please connect to controller first!")
            return
        
        # Collect payload values
        payload_values = {}
        for axis, var in self.payload_vars.items():
            try:
                payload_values[axis] = float(var.get())
            except ValueError:
                messagebox.showerror("Error", f"Please enter a valid number for {axis} payload!")
                return
        
        self.process_btn.config(state='disabled')
        self.output_text.delete(1.0, tk.END)
        
        def process_thread():
            try:
                # Redirect stdout to our text widget
                old_stdout = sys.stdout
                sys.stdout = self.redirect_text
                
                print("🚀 Starting MCD payload modification process...")
                print(f"📁 MCD File: {self.mcd_path}")
                print(f"🎯 Payload Values: {payload_values}")
                print()
                
                # Step 1: Create backup of original MCD
                backup_path = self.mcd_path.replace('.mcd', '-backup.mcd')
                shutil.copy2(self.mcd_path, backup_path)
                print(f"💾 Backup created: {backup_path}")
                
                # Step 2: Modify MCD with payload values
                print("\n🔧 Modifying MCD payloads...")
                modified_mcd = self.modify_mcd_payloads(self.mcd_path, payload_values)
                
                if not modified_mcd:
                    print("❌ Failed to modify MCD payloads")
                    return
                
                # Step 3: Update controller name from "No Load" to "Loaded"
                print("\n📝 Updating controller name from 'No Load' to 'Loaded'...")
                try:
                    updated_mcd = self.modify_controller_name(modified_mcd, "Loaded")
                    if updated_mcd:
                        print("✅ Controller name updated successfully")
                        modified_mcd = updated_mcd
                    else:
                        print("⚠️ Could not update controller name, continuing with original")
                except Exception as e:
                    print(f"⚠️ Error updating controller name: {e}")
                    print("Continuing with original MCD...")
                
                # Step 4: Calculate parameters using GenerateMCD
                print("\n🧮 Calculating parameters...")
                try:
                    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                    MS_DLL_PATH = os.path.join(CURRENT_DIR, "extern", "Automation1")
                    CONFIG_MANAGER_PATH = os.path.join(CURRENT_DIR, "System.Configuration.ConfigurationManager.8.0.0", "lib", "netstandard2.0")

                    # Update MCD name to reflect "Loaded" state
                    loaded_mcd_name = self.mcd_name.replace(" No Load", "").replace(" NoLoad", "").replace("No Load", "").replace("NoLoad", "")
                    loaded_mcd_name = loaded_mcd_name.strip() + " Loaded"
                    print(f"📝 Using MCD name: {loaded_mcd_name}")

                    # Create AerotechController instance with updated name
                    mcd_converter = AerotechController(CURRENT_DIR, MS_DLL_PATH, CONFIG_MANAGER_PATH, loaded_mcd_name)
                    mcd_converter.initialize()

                    read_from_file = mcd_converter.MachineControllerDefinition.GetMethod("ReadFromFile")
                    mcd_obj = read_from_file.Invoke(None, [modified_mcd])

                    # Call calculate_from_current_mcd
                    calculated_mcd, warnings = mcd_converter.calculate_from_current_mcd(mcd_obj)
                    
                    if warnings:
                        print("⚠️ Warnings during calculation:")
                        for warning in warnings:
                            print(f"   - {warning}")
                    
                    print("✅ Parameter calculation completed successfully!")
                    
                except Exception as e:
                    print(f"❌ Error during parameter calculation: {e}")
                    import traceback
                    print(traceback.format_exc())
                
                print("\n🎉 MCD payload modification process completed!")
                
            except Exception as e:
                print(f"❌ Error during process: {e}")
                import traceback
                print(traceback.format_exc())
            finally:
                sys.stdout = old_stdout
                self.root.after(0, self.process_finished)
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def process_finished(self):
        """Called when processing finishes"""
        self.process_btn.config(state='normal')
    
    def monitor_output(self):
        """Monitor the output queue and update text widget"""
        try:
            while True:
                text = self.output_queue.get_nowait()
                self.output_text.insert(tk.END, text)
                self.output_text.see(tk.END)
                self.root.update_idletasks()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.monitor_output)

def center_window(root, width=900, height=900):
    """Center the window on the screen"""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    center_x = int(screen_width/2 - width/2)
    center_y = int(screen_height/2 - height/2)
    
    root.geometry(f'{width}x{height}+{center_x}+{center_y}')

def main():
    """Main function to run the UI"""
    root = tk.Tk()
    
    # Set window properties
    root.resizable(True, True)
    
    # Center the window on screen
    center_window(root, 900, 900)
    
    # Create and start the application
    app = MCDPayloadUI(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit MCD Payload Modifier?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
