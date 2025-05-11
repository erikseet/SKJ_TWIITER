# Twiiter – Twitter/X Clone

Toto je jednoduchá Twitter/X klon aplikácia vytvorená pomocou Django frameworku.

## Inštalácia

### Požiadavky

- Python 3.8 alebo novší  
- Django 5.2 alebo novší  

### Kroky na inštaláciu

1. Klonujte repozitár:

   git clone https://github.com/vasusername/twiiter.git  
   cd twiiter

2. Vytvorte a aktivujte virtuálne prostredie:

   python -m venv venv  
   source venv/bin/activate  # Pre Linux/Mac  
   venv\Scripts\activate     # Pre Windows

3. Nainštalujte potrebné závislosti:

   pip install -r requirements.txt

4. Vytvorte a aplikujte migrácie:

   python manage.py makemigrations  
   python manage.py migrate

5. Vytvorte superpoužívateľa (admin):

   python manage.py createsuperuser

6. Spustite vývojový server:

   python manage.py runserver

7. Otvorte prehliadač a prejdite na adresu:

   http://127.0.0.1:8000/
