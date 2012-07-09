run:
	cd archpl && python manage.py runserver 0:8000 --nothread

db:
	cd archpl && python manage.py syncdb --noinput

shell:
	cd archpl && python manage.py shell

dbshell:
	cd archpl && python manage.py dbshell
