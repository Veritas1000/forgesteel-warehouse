from forgesteel_warehouse import init_app
from forgesteel_warehouse.utils.app_utils import bootstrap

if __name__ == "__main__":
    bootstrap()
    
    app = init_app()
    app.run(host='0.0.0.0', debug=True)
