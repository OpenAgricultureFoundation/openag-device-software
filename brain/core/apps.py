from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    name = 'brain.core'

    def ready(self):
    	# Ensure startup code only runs once
        if os.environ.get('RUN_MAIN') != 'true':
        	return
     
        # Startup code here
        print("Startup!!!!!!!___!__!__!___!_!_!_")