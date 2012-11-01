# predict-remote

Is a client/server wrapper around the [LIBLINEAR](http://www.csie.ntu.edu.tw/~cjlin/liblinear/)'s Python interface.
Needs [Twisted](http://twistedmatrix.com/trac/).

## Why?

When the classifier you trained is too big to give an instantaneous result via the 'predict' binary it's better to load it in memory and query it remotely.
The loading price is paid only once, when you start the server, and not every time some document needs to be classified.
