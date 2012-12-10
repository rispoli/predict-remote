import argparse
from twisted.internet import protocol, reactor

class Predict(protocol.Protocol):
    def connectionMade(self):
        self.transport.write(self.factory.in_file.readline())
        self.factory.in_file.close()

    def dataReceived(self, data):
        self.factory.out_file.write(data)

    def connectionLost(self, reason):
        self.factory.out_file.close()

class PredictFactory(protocol.ClientFactory):
    protocol = Predict

    def __init__(self, in_file, out_file):
        self.in_file  = in_file
        self.out_file = out_file

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed: " + reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        reactor.stop()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hostname', help = 'hostname')
    parser.add_argument('port', type = int, help = 'port number to listen on')
    parser.add_argument('in_file', type = argparse.FileType('r'), help = 'input file')
    parser.add_argument('out_file', type = argparse.FileType('w'), help = 'output file')
    args = parser.parse_args()

    reactor.connectTCP(args.hostname, args.port, PredictFactory(args.in_file, args.out_file))
    reactor.run()

if __name__ == "__main__":
    main()
