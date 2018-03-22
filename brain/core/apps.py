from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    name = 'brain.core'

    def ready(self):
    	# Ensure startup code only runs once
        if os.environ.get('RUN_MAIN') != 'true':
        	return
     
        # Startup code here
        print("--------------------")
        

        # Import tasks
        from .tasks import printy
        
        # Setup tasks
        # printy.delay(34)




