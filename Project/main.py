from multiprocessing import Process
from vb_cable_installer import VBCableInstaller
from auth_token import obtain_auth_token
from main_input_output import main_input, main_output

def main():
    installer = VBCableInstaller()
    installer.install()

    token = obtain_auth_token()

    if not token:
        raise Exception("Token was not obtained successfully. Exiting.")

    input_process = Process(target=main_input, args=(token,))
    output_process = Process(target=main_output, args=(token,))

    input_process.start()
    output_process.start()

    input_process.join()
    output_process.join()

if __name__ == "__main__":
    main()