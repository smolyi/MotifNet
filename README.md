# MotifNet
Identify network motifs using FANMOD algorithm, which was developed and published by Sebastian Wernicke and Florian Rasche [https://academic.oup.com/bioinformatics/article/22/9/1152/199945].

The code here is the server-side implementation of the MotifNet web-server [https://netbio.bgu.ac.il/motifnet/#/].

MotifNet was published as scientific web-tool in a peer-reviewed journal [https://academic.oup.com/bioinformatics/article/33/12/1907/2971438].

cgi-bin
=======
The cgi-bin folder which recieves requests from the website (the client-side). In this folder, scripts will either defer the request to the RPC-Server (using the RPC-Client), or execute new processes (e.g. run FANMOD, delete sessions, etc.; depends on the request).

RPC-Server
==========
The RPC-server is a processes that constently run on the server, communicates with the database and stores user-data on the server's memory for fast queries.

RemoteFanmodServer
==================
The code executing FANMOD package. This code also wraps FANMOD by allowing input networks with node names rather than only integers.

www.zip
========
The html, JS, css code of the MotifNet website that is implemented using React and SemanticUI libraries.
