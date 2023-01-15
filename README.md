# cimec_bot
This is a telegram chatbot that parse the University of Trento website and offers an information of CIMeC's latest news or events.
The chatbot link: https://t.me/cimec_info_bot
The main code file: cimec_bot.py
We deploy the chatbot on Heroku using Flask.
Necessary files in the directory so that Heroku could recognize the app:
Procfile – a text file for Heroku, to explicitly declare what command should be executed to start the app.
requirements.txt – the list of non-Python libraries with versions for Heroku to install
runtime.txt – to specify which Python version to use
