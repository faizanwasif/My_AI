from dotenv import load_dotenv
from src.controllers.app_controller import AppController

def main():
    load_dotenv()
    controller = AppController()
    controller.run()

if __name__ == "__main__":
    main()