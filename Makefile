all:

install:
	[ -e /var/www ] && mv /var/www /var/www.old
	cp -a www /var
	cp fitsproc.py /var/www/cgi-bin
	chmod -x /var/www/cgi-bin/fitsproc.py
	chown -R www-data.www-data /var/www
	[ -e /etc/apache2/sites-available/default ] && mv /etc/apache2/sites-available/default /etc/apache2/sites-available/default.old 
	cp apache2/sites-available/default /etc/apache2/sites-available/default
	/etc/init.d/apache2 restart

clean:
	rm -f *~ *.pyc
