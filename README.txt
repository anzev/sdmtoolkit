README for SDM Toolkit for Orange4WS

All files in this directory and all subdirectories are licensed under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.                                        

Bug reports, questions, and comments should be sent to:                                                                                                                                                                                                                        

anze.vavpetic@ijs.si  


1. CODE ORGANIZATION

    The toolkit is organized into two main parts: 

    o the server side:
        * OWL2x/                        ... accessing and converting OWL files.
        * owl2x.py                      ... python interface for OWL2X.
        * sdmaleph/                     ... SDM-Aleph system implementation & web service.
        * sdmsegs/                      ... SDM-SEGS system implementation & web service.

    o the client side:
        * orange/OrangeWidgets/SDM/     ... Orange widgets.

    The server side contains the main code of the corresponding data mining algorithms and the servers for the web services.

    The client side contains the clients for the web services (namely, Orange widgets) and the 'Rule browser' widget. 
    By default, the widgets call the web services located at our server, so you in fact do not need to install the server side part - but, we do not make any guarantees that the services will be accessible at the time that you need them :-).


2. INSTALLATION

2.1 Client side

    o Install the prerequisites:
        * The open source Orange data mining platform (http://orange.biolab.si), required by Orange4WS.
        * The Orange4WS upgrade for Orange (http://orange4ws.ijs.si), required by SegMine.
    o Run python setup.py install.
    o If you don't plan to deploy the web services on your own server, you are done. Otherwise continue with Section 2.2.

2.2 Server side

    o Unzip anywhere.
    o To run the servers you need the following prerequisites:
        * The prerequisites required for the client side (see Section 2.1).
        * A reasonably up-to-date version of Java (we use the open-source Jena semantic web framework: http://jena.sourceforge.net/, which is included in our toolkit).
        * Yap Prolog Interpreter version 6, compile with --enable-tabling=yes. 
          If you don't install yap to /usr/local/bin/yap, you must fix the YAP variable in sdmaleph/aleph.py to the appropriate path.
    o Done.


3. USE CASE

    See https://sourceforge.net/p/sdmtoolkit/wiki/usecase/ for a complete use case example.


Thank you for your interest in the SDM Toolkit for Orange4WS!