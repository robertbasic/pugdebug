# pugdebug

pugdebug is a standalone debugging client for PHP applications that uses XDebug as the debugging engine.

A python 3.4, PyQt5 project.

## current release

The current release of pugdebug is [1.0.0-beta.1](https://github.com/robertbasic/pugdebug/releases/tag/v1.0.0-beta.1).

It includes a tar.gz/ZIP package with the binary, for both Linux and Windows. It should include everything
needed for pugdebug to work correctly, so just download the package for your operating system,
unpack it and start pugdebug.

Please report any [issues](https://github.com/robertbasic/pugdebug/issues) you encounter.

## executables

There are executables available for Linux and Windows operating systems.
Every [release](https://github.com/robertbasic/pugdebug/releases) includes a tar.gz/ZIP package with the
executables. The executable includes everything needed for pugdebug to work correctly on your system. There
is no need to install or set up anything else.

## change log

Please take a look at the [change log](./CHANGELOG.md)

## setting up the environment

> NOTE: Setting up the environment should be needed only when you want to help out with
> developing pugdebug itself. And for OS X as there are no current builds for it yet.

The main dependencies are Python 3.4,
[QT5.4](http://doc.qt.io/qt-5/gettingstarted.html),
[SIP4.6](http://www.riverbankcomputing.com/software/sip/download)
and [PyQt5.4](http://www.riverbankcomputing.com/software/pyqt/download5).

There is a wiki page with
[instructions how to set up the development environment](https://github.com/robertbasic/pugdebug/wiki/Install-pugdebug)
for Fedora, Ubuntu, Windows and OSX.


There is also a [blog post](http://robertbasic.com/blog/install-pyqt5-in-python-3-virtual-environment)
about setting up a virtual environment on a Fedora that goes into bit more details.

## setting up xdebug

To be able to debug PHP with pugdebug, you need to have [xdebug](http://xdebug.org/docs/remote)
propely set up for remote debugging.

A minimal configuration would be something like:

```
xdebug.idekey=pugdebug
xdebug.remote_enable=1
xdebug.remote_port=9000
xdebug.remote_host=127.0.0.1
```

If the project you want to debug is in a vagrant virtual machine, your xdebug
config should be something like:

```
xdebug.idekey=pugdebug
xdebug.remote_enable=1
xdebug.remote_port=9000
xdebug.remote_connect_back=1
```

Do note that when debugging CLI scripts from a vagrant virtual machine, the
`remote_connect_back` setting will not work, and we need to use the
`remote_host` setting. The xdebug configuration should look something like:

```
xdebug.idekey=pugdebug
xdebug.remote_enable=1
xdebug.remote_port=9000
xdebug.remote_host=33.33.33.1
```

You can find the IP address to use for the remote host setting by issuing the
following command on the host machine:

```
ip addr
```

and a part of the output will include something like this:

```
6: vboxnet2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UNKNOWN group default qlen 1000
    link/ether 0a:00:27:00:00:02 brd ff:ff:ff:ff:ff:ff
    inet 33.33.33.1/24 brd 33.33.33.255 scope global vboxnet2
       valid_lft forever preferred_lft forever
    inet6 fe80::800:27ff:fe00:2/64 scope link
       valid_lft forever preferred_lft forever
```

and from there we can see the IP address of `33.33.33.1`.

## using pugdebug

If you are using a pugdebug build, just execute the binary, that should bring up
pugdebug.

If you cloned this repository, go to the sources directory, activate the Python
virtual environment and start pugdebug by issuing a `python app.py` command.

## pugdebug settings

To bring up the `Settings` window, navigate to `Files -> Settings` (shortcut: `Ctrl+S`).

### pugdebug path settings

The `Path` section refers to the path settings.

The `Root` under the `Path` section is the root path where the project you want to debug is
located.

The `Maps from` under the `Path` section is for when the project you want to debug is under
a virtual machine, like Vagrant. Here you would enter the path of the project under that VM.

For example, if a project I'm working on is in `/home/robert/wwww/pugdebug` and that maps to
`/var/www` under the VM, the `Root` would be set to `/home/robert/www/pugdebug` and the
`Maps from` would be set to `/var/www`.

### pugdebug debugger settings

The `Host` setting should be the IP address of the machine on which pugdebug runs. In most cases
it is perfectly fine to leave this field blank.

The `Port` setting is the port number on which xdebug will attempt to connect to the machin on
which pugdebug runs. The default port is `9000`.

The `IDE Key` setting allows to filter out messages from xdebug based on this value.

`Break at first line` tells the debugger should it break on the first line or not.

`Max depth`, `Max children` and `Max data` settings control the amount of information
about variables is retrieved from xdebug.

## debugging sessions

To start a debugging session, click the "Start" button in the top left corner (Shortcut: F2).

Load your web project in your browser and start a
[HTTP debugging session](http://xdebug.org/docs/remote#browser_session).

pugdebug should pick up that session and display the index file of your web
project, while stopping the execution on the first line.

Using the `Run`, `Over`, `In`, `Out` continuation commands you can step through
your PHP code.

Setting breakpoints is possible by double clicking the line where a breakpoint
should be placed.

The correspoding line number should be highlighted and a new breakpoint should
be listed in the breakpoint viewer (bottom right corner).

Double clicking the line with a breakpoint should remove that breakpoint.

## debugging cli scripts

It is also possible to debug CLI scripts with pugdebug.

Start pugdebug as stated in the previous section, click `Start` to
start a debugging session and then in a new terminal type:

```
export XDEBUG_CONFIG="idekey=pugdebug"
```

(or whatever you set the `xdebug.idekey` setting to) and then start
your PHP CLI script normally:

```
php script.php
```

pugdebug should pick up the debugging session and let you debug your script.

## todo

Take a look at the [issue tracker](https://github.com/robertbasic/pugdebug/issues).

## contributions

Contributions are more than welcome! Report bugs, tell me your ideas and needs,
write code, test it on different platforms ...

## slack

There's a slack created for [pugdebug](https://pugdebug.slack.com/).

If you would like access, open a [new ticket](https://github.com/robertbasic/pugdebug/issues).
