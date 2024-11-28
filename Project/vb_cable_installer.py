import os
import requests
import zipfile
import subprocess

class VBCableInstaller:
    def __init__(self, driver_path="C:\Program Files\VB\CABLE", download_url="https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack45.zip", installer_zip="VBCABLE_Driver_Pack43.zip", extracted_path="VBCABLE_Installer"):
        self.driver_path = driver_path
        self.download_url = download_url
        self.installer_zip = installer_zip
        self.extracted_path = extracted_path

    def is_vb_cable_installed(self):
        """Check if the VB-Cable driver is installed by verifying the driver path."""
        return os.path.exists(self.driver_path)

    def download_vb_cable_installer(self):
        """Download the VB-Cable installer from the specified URL."""
        print("Starting download of VB-Cable installer...")
        response = requests.get(self.download_url, stream=True)
        if response.status_code == 200:
            with open(self.installer_zip, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):    
                    file.write(chunk)
            print(f"Downloaded VB-Cable installer to {self.installer_zip}")
            return self.installer_zip
        else:
            print(f"Failed to download VB-Cable installer. Status code: {response.status_code}")
            return None

    def install_vb_cable(self, installer_path):
        """Install VB-Cable by extracting and running the installer."""
        print(f"Extracting installer from {installer_path}...")
        with zipfile.ZipFile(installer_path, "r") as zip_ref:
            zip_ref.extractall(self.extracted_path)
        print(f"Extracted installer to {self.extracted_path}")
        
        installer_exec_path = os.path.join(self.extracted_path, "VBCABLE_Setup_x64.exe")  # Ensure this is the correct executable name
        try:
            subprocess.run(["start", "/wait", installer_exec_path], shell=True, check=True)
            print("VB-Cable installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Installation failed: {e}")

    def install(self):
        """Check if VB-Cable is installed, if not, download and install it."""
        if self.is_vb_cable_installed():
            print("VB-Cable is already installed. No need to download or install.")
        else:
            print("VB-Cable is not installed. Downloading and installing...")
            installer_path = self.download_vb_cable_installer()
            if installer_path:
                self.install_vb_cable(installer_path)
