INSTALL
-------

Assuming you copied everything to /var/www/fflow:

    apt-get install -y python-virtualenv supervisor build-essential python-dev
    cd /var/www/fflow
    virtualenv localpy
    ./localpy/bin/pip install -r pip-requirements.txt
    ln -s /var/www/fflow/supervisor.conf /etc/supervisor/conf.d/stats.conf
    supervisorctl reload
