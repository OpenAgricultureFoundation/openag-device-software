from django.apps import AppConfig
import os


class CoreConfig(AppConfig):
    name = 'app'

    def ready(self):
    	# Ensure startup code only runs once
        if os.environ.get('RUN_MAIN') != 'true':
        	return
     
        # Startup code here