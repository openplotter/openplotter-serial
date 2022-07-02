## openplotter-serial

OpenPlotter app to manage serial devices

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Install dependencies:

`sudo apt install gpsd gpsd-clients`

Clone the repository:

`git clone https://github.com/openplotter/openplotter-serial`

Make your changes and create the package:

```
cd openplotter-serial
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-serial_x.x.x-xxx_all.deb
```

Run post-installation script:

`sudo serialPostInstall`

Run:

`openplotter-serial`

Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://cloudsmith.io/~openplotter/repos/openplotter/packages/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1