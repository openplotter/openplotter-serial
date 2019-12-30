## openplotter-serial

OpenPlotter app to manage serial devices

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Install dependencies:

`sudo apt install gpsd`

Clone the repository:

`git clone https://github.com/openplotter/openplotter-serial`

Install:
```
cd openplotter-serial
sudo python3 setup.py install
```
Run post-installation script:

`sudo serialPostInstall`

Run:

`openplotter-serial`

Make your changes and repeat installation and post-installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1