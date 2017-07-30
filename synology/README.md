# Installing on DSM 6.1

Install the official Python 3 module in the packages program.

## To get pip installed:
* Download the following file get-pip.py or
    * wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
* run: sudo python3 get-pip.py

## To install the application:
* Copy the HueBoblightd-<vers>-py3-none-any.whl file onto your NAS
* Install with pip install HueBoblightd-<vers>-py3-none-any.whl

## To create an automatic startup script:
* Copy the hueboblight.sh script to "/usr/local/etc/rc.d/"
* Set the file permission to 755
   * sudo chown 755 /usr/local/etc/rc.d/hueboblightd.sh
* Modify the {PYTHON_EXEC}, {EXEC}, {CONFIG} & {LOG_DIR} variables appropiate to your setup
* The script will now be called with "start" or "stop" arguments when the server boots or shuts down
* To start the server for testing:
   * sudo /usr/local/etc/rc.d/hueboblightd.sh start
* To restart the server causing it to re-read the configuration file:
  * sudo /usr/local/etc/rc.d/hueboblightd.sh restart
* To toggle the logging level between INFO & DEBUG:
  * sudo /usr/local/etc/rc.d/hueboblightd.sh logging