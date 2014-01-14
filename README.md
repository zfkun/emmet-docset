#Emmet-DocSet

[Emmet](http://emmet.io/) (formerly Zen Coding) DocSet for [Dash](http://kapeli.com).


## Update

+ 2013/12/01
    + deprecated old build.py
    + use Phantomjs for automation

+ 2014/01/14
    + add build.js for node
    + deprecated build.js ( -_-!, finally.. )


## Requirements

* Mac OS
* Python 2.7+
* [Homebrew](https://github.com/Homebrew/homebrew)
* [Phantomjs](https://github.com/ariya/phantomjs)

	```
	brew update & brew install phantomjs
	```


## Usage


```
phantomjs build
```
or

```
chmod +x build
./build
```


**if you just need rebuild:**

```
python build.py
```


## Feed [(Online)](http://zfkun.github.io/emmet-docset/Emmet.xml)

    dash-feed://http%3A%2F%2Fzfkun.github.io%2Femmet-docset%2FEmmet.xml