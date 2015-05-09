# pugdebug

pugdebug is (well, should be) a PHP standalone debugger.

A python 3.4.x, pyqt5 project.

## setting up the environment

The main dependencies are Python 3.4,
[QT5.4](http://doc.qt.io/qt-5/gettingstarted.html),
[SIP4.6](http://www.riverbankcomputing.com/software/sip/download)
and [PyQt5.4](http://www.riverbankcomputing.com/software/pyqt/download5).

I wrote a [blog post](http://robertbasic.com/blog/install-pyqt5-in-python-3-virtual-environment)
about setting up a virtual environment for it.

Clone this repo and after setting up the virtual environment, install the application
requirements by running:

```
pip install -r requirements.txt
```

After the requirements are installed, start pugdebug with a simple command:

```
python app.py
```

[@ihabunek](https://github.com/ihabunek) and [@vranac](https://github.com/vranac)
report that this process is pretty painless on Ubuntu and OSX machines. Some
package names might differ from what I used, but a document explaining the venv
setup process on different systems should be available soon.

Do note that I'm trying to figure out how to build executables for this beast.

### OS X setup with Homebrew

Easiest way to install dependencies on OS X is to use [Homebrew].
To install the dependencies, execute the following commands from your terminal:
```
brew install python3
brew install qt5 pyqt5 sip
```

Go to directory where you checked out the pugdebug, and execute
```
python3 app.py
```

At the moment, there seems to be an issue with using virtualenv, python3 and pyqt5 on OS X Yosemite.

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

In a terminal go to the directory where you have pugdebug cloned and start it by
issuing a `python app.py` command.

On the left side you can see a simple file browser that should list your home
directory.

Under it is an input field with the label `Root:`, containing the path to your
home directory.

By entering a new root path in the `root` input field will change the root
directory of the file browser.

For example, on my laptop it starts with `/home/robert` and the file browser
lists my home directory. If I enter `/home/robert/www/pugdebug` into the `root`
input field, the file browser will change to the pugdebug web project.

But this is just temporary, it will be nicer in the future.

## debugging sessions

To start a debugging session, click the "Start" button in the top left corner.

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
start a debugging session and then in a second terminal type:

```
export XDEBUG_CONFIG="idekey=pugdebug"
```

(or whatever you set the `xdebug.idekey` setting to) and then start
your PHP CLI script normally:

```
php script.php
```

pugdebug should pick up the debugging session and let you debug your script.

## executables

I'm trying to make executables with
[pyqtdeploy](http://www.riverbankcomputing.com/software/pyqtdeploy/download).
So far I managed to create one for Fedora 21.

## todo

Take a look at the [issue tracker](https://github.com/robertbasic/pugdebug/issues).

## contributions

Contributions are more than welcome! Report bugs, tell me your ideas and needs,
write code, test it on different platforms ...

[Homebrew]: http://brew.sh/

## slack

There's a slack created for pugdebug at https://pugdebug.slack.com/

If you would like access, open a [new ticket](https://github.com/robertbasic/pugdebug/issues).
