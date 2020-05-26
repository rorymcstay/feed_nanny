import logging
from logging.config import dictConfig
import os
from feed.settings import nanny_params, mongo_params, logger_settings_dict




if __name__ == '__main__':
    dictConfig(logger_settings_dict)

    logging.getLogger("urllib3").setLevel("INFO")

    logging.info("####### Environment #######")
    logging.info(f'nanny: {nanny_params}, mongo: {mongo_params}')
    logging.info("\n".join([f'{key}={os.environ[key]}' for key in os.environ]))

    from src.main.app import app
    logging.info(app.url_map)

    app.run(port=os.getenv("FLASK_PORT", os.getenv("NANNY_PORT", 5003)), host=os.getenv('NANNY_HOST'))
